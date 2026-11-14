"""Dependency-free XLSX creation and lossless rating transfer to detailed CSV."""
import argparse
import csv
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
import posixpath
import zipfile
import xml.etree.ElementTree as E

ROOT = Path(__file__).resolve().parents[1]
NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
SHEETS = {
    "User Stories": ("user_story_refinement", (("Conceptually Sound", "conceptually_sound"), ("Problem-oriented", "problem_oriented"),
                                             ("Unambiguous", "unambiguous"), ("Source Fidelity", "source_fidelity"))),
    "Bug Reports": ("bug_report_refinement", (("Clarity", "clarity"), ("Reproducibility", "reproducibility"),
                                            ("Factual Consistency", "factual_consistency"))),
}
BASE = ("Anonymous ID", "Sample ID", "A/B", "Original source", "Output")
NOTES = "Evidence / notes"


def col(index):
    result = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def xml(node):
    return E.tostring(node, encoding="utf-8", xml_declaration=True)


def load_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)


def build(csv_path, output, *, pairs_per_type=50):
    if output.exists():
        raise ValueError("Workbook exists; refusing to overwrite")
    _, rows = load_csv(csv_path)
    expected = pairs_per_type * 4
    if pairs_per_type not in (25, 50) or len(rows) != expected or len({r["blinded_output_id"] for r in rows}) != expected:
        raise ValueError("Unexpected number of unique paired outputs")
    content = E.Element("Types", xmlns="http://schemas.openxmlformats.org/package/2006/content-types")
    for extension, kind in (("rels", "application/vnd.openxmlformats-package.relationships+xml"), ("xml", "application/xml")):
        E.SubElement(content, "Default", Extension=extension, ContentType=kind)
    for name, kind in (("workbook", "sheet.main"), ("styles", "styles")):
        E.SubElement(content, "Override", PartName=f"/xl/{name}.xml", ContentType=f"application/vnd.openxmlformats-officedocument.spreadsheetml.{kind}+xml")
    package_rel = E.Element("Relationships", xmlns="http://schemas.openxmlformats.org/package/2006/relationships")
    E.SubElement(package_rel, "Relationship", Id="rId1", Type=REL + "/officeDocument", Target="xl/workbook.xml")
    workbook = E.Element("workbook", xmlns=NS, attrib={"xmlns:r": REL})
    sheets = E.SubElement(workbook, "sheets")
    links = E.Element("Relationships", xmlns="http://schemas.openxmlformats.org/package/2006/relationships")
    files = {"_rels/.rels": xml(package_rel)}
    for number, (name, (kind, criteria)) in enumerate(SHEETS.items(), 1):
        selected = [r for r in rows if r["task_type"] == kind]
        if len(selected) != pairs_per_type * 2:
            raise ValueError("Unexpected number of outputs per sheet")
        pairs = {}
        for r in selected:
            pairs.setdefault(r["sample_id"], set()).add(r["output_label"])
        if len(pairs) != pairs_per_type or any(labels != {"A", "B"} for labels in pairs.values()):
            raise ValueError("Workbook must contain complete A/B pairs")
        last_row = len(selected) + 1
        headers = list(BASE) + [title for title, _ in criteria] + [NOTES]
        sheet = E.Element("worksheet", xmlns=NS)
        views = E.SubElement(sheet, "sheetViews")
        view = E.SubElement(views, "sheetView", workbookViewId="0")
        E.SubElement(view, "pane", xSplit="3", ySplit="1", topLeftCell="D2", activePane="bottomRight", state="frozen")
        columns = E.SubElement(sheet, "cols")
        for i in range(1, len(headers) + 1):
            E.SubElement(columns, "col", min=str(i), max=str(i), width=str(38 if i < 3 else 7 if i == 3 else
                          65 if i in (4, 5) else 48 if i == len(headers) else 20), customWidth="1")
        data = E.SubElement(sheet, "sheetData")
        values = [headers]
        for r in selected:
            values.append([r["blinded_output_id"], r["sample_id"], r["output_label"], r["source_input"], r["output_text"]]
                          + ["" for _ in criteria] + [""])
        for ri, values_row in enumerate(values, 1):
            row = E.SubElement(data, "row", r=str(ri), ht="42" if ri == 1 else "180", customHeight="1")
            for ci, value in enumerate(values_row, 1):
                style = "1" if ri == 1 else "3" if 6 <= ci < len(headers) else "2"
                if len(value) > 32767 or any(ord(c) < 32 and c not in "\t\n\r" for c in value):
                    raise ValueError("Text cannot be represented losslessly in an Excel cell")
                cell = E.SubElement(row, "c", r=f"{col(ci)}{ri}", s=style, t="inlineStr")
                inline = E.SubElement(cell, "is")
                E.SubElement(inline, "t", attrib={"{http://www.w3.org/XML/1998/namespace}space": "preserve"}).text = value
        E.SubElement(sheet, "autoFilter", ref=f"A1:{col(len(headers))}{last_row}")
        validations = E.SubElement(sheet, "dataValidations", count=str(len(criteria)))
        for ci in range(6, 6 + len(criteria)):
            rule = E.SubElement(validations, "dataValidation", type="list", allowBlank="1", showErrorMessage="1",
                                errorStyle="stop", errorTitle="Use a rating from 1 to 5", error="Choose 1, 2, 3, 4 or 5; leave blank if unassessable.",
                                sqref=f"{col(ci)}2:{col(ci)}{last_row}")
            E.SubElement(rule, "formula1").text = '"1,2,3,4,5"'
        files[f"xl/worksheets/sheet{number}.xml"] = xml(sheet)
        E.SubElement(content, "Override", PartName=f"/xl/worksheets/sheet{number}.xml", ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml")
        E.SubElement(sheets, "sheet", name=name, sheetId=str(number), attrib={"r:id": f"rId{number}"})
        E.SubElement(links, "Relationship", Id=f"rId{number}", Type=REL + "/worksheet", Target=f"worksheets/sheet{number}.xml")
    E.SubElement(links, "Relationship", Id="rId3", Type=REL + "/styles", Target="styles.xml")
    styles = f'''<?xml version="1.0" encoding="UTF-8"?>
<styleSheet xmlns="{NS}"><fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>
<fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FFDCE6F1"/><bgColor indexed="64"/></patternFill></fill></fills>
<borders count="1"><border/></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="4"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyAlignment="1"><alignment wrapText="1" vertical="center"/></xf>
<xf numFmtId="49" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>
<xf numFmtId="1" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment horizontal="center" vertical="top"/></xf></cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>'''
    files.update({"[Content_Types].xml": xml(content), "xl/workbook.xml": xml(workbook),
                  "xl/_rels/workbook.xml.rels": xml(links), "xl/styles.xml": styles.encode()})
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, value in files.items():
            archive.writestr(name, value)


def read_workbook(path):
    with zipfile.ZipFile(path) as archive:
        ns = {"s": NS}
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared = ["".join(n.itertext()) for n in E.fromstring(archive.read("xl/sharedStrings.xml")).findall("s:si", ns)]
        links = {n.attrib["Id"]: n.attrib["Target"] for n in E.fromstring(archive.read("xl/_rels/workbook.xml.rels"))}
        result = {}
        for sheet in E.fromstring(archive.read("xl/workbook.xml")).findall("s:sheets/s:sheet", ns):
            target = links[sheet.attrib["{" + REL + "}id"]]
            name = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/" + target)
            rows = []
            for row in E.fromstring(archive.read(name)).findall("s:sheetData/s:row", ns):
                values = {}
                for cell in row.findall("s:c", ns):
                    if cell.find("s:f", ns) is not None:
                        raise ValueError("Formulas are not supported in the scoring workbook")
                    key = re_column(cell.attrib["r"])
                    if cell.attrib.get("t") == "inlineStr":
                        value = "".join(t.text or "" for t in cell.findall("s:is//s:t", ns))
                    else:
                        value = cell.findtext("s:v", "", ns)
                        if cell.attrib.get("t") == "s":
                            value = shared[int(value)]
                    values[key] = value
                rows.append(values)
            result[sheet.attrib["name"]] = rows
        return result


def re_column(reference):
    return "".join(c for c in reference if c.isalpha())


def transfer(workbook, original_csv, output_csv, *, selection_file=None):
    if output_csv.exists():
        raise ValueError("Refusing to overwrite a detailed scoring file")
    fields, original = load_csv(original_csv)
    lookup = {r["blinded_output_id"]: dict(r) for r in original}
    sheets = read_workbook(workbook)
    if set(sheets) != set(SHEETS) or len(lookup) != 200:
        raise ValueError("Expected two sheets and 200 output IDs")
    seen = set()
    for name, (kind, criteria) in SHEETS.items():
        data = sheets[name]
        headers = list(BASE) + [title for title, _ in criteria] + [NOTES]
        if [data[0].get(col(i), "") for i in range(1, len(headers) + 1)] != headers:
            raise ValueError("Workbook headers changed")
        for cells in data[1:]:
            if not any(cells.values()):
                continue
            values = {header: cells.get(col(i), "") for i, header in enumerate(headers, 1)}
            ident = values["Anonymous ID"]
            if ident not in lookup or ident in seen:
                raise ValueError("Unknown or duplicate output ID")
            seen.add(ident)
            row = lookup[ident]
            if any(row[key] != values[title] for key, title in (("sample_id", "Sample ID"), ("output_label", "A/B"),
                   ("source_input", "Original source"), ("output_text", "Output"))) or row["task_type"] != kind:
                raise ValueError("Source/output text or identity changed")
            for title, key in criteria:
                entered = values[title].strip()
                if entered:
                    try:
                        number = Decimal(entered)
                        if number not in {Decimal(n) for n in range(1, 6)}:
                            raise ValueError("Ratings must be integers 1–5")
                    except InvalidOperation:
                        raise ValueError("Invalid rating") from None
                    rating = str(int(number))
                    if row[key + "_rating"] and row[key + "_rating"] != rating:
                        raise ValueError("Conflicting existing detailed rating")
                    row[key + "_rating"] = rating
            note = values[NOTES]
            if note and note != row.get("notes", ""):
                row["notes"] = "\n\n".join(value for value in (row.get("notes", ""), note) if value)
    selection_file = selection_file or workbook.with_suffix(".selection.json")
    expected_ids = set(json.loads(selection_file.read_text(encoding="utf-8"))["blinded_output_ids"]) if selection_file.exists() else set(lookup)
    if not expected_ids <= set(lookup) or seen != expected_ids:
        raise ValueError("Missing workbook outputs")
    with output_csv.open("x", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(lookup[r["blinded_output_id"]] for r in original)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "transfer"))
    parser.add_argument("--csv", type=Path, default=ROOT / "results/final_evaluation/human_semantic_final_v1_1/evaluator/scoring_sheet.csv")
    parser.add_argument("--workbook", type=Path, default=ROOT / "results/final_evaluation/human_semantic_final_v1_1/evaluator/single_rater.xlsx")
    parser.add_argument("--output-csv", type=Path)
    parser.add_argument("--pairs-per-type", type=int, choices=(25, 50), default=50)
    parser.add_argument("--selection-file", type=Path, help="Selection sidecar when transferring a reduced workbook")
    args = parser.parse_args()
    if args.action == "build":
        build(args.csv, args.workbook, pairs_per_type=args.pairs_per_type)
    elif args.output_csv is None:
        parser.error("transfer requires --output-csv pointing to a new file")
    else:
        transfer(args.workbook, args.csv, args.output_csv, selection_file=args.selection_file)
