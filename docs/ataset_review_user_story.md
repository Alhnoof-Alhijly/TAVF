
# User Story Dataset Review

## 1. Objective

This review evaluates candidate datasets for the User Story Refinement task in TAVF. Dataset selection is based on four requirements: scientific publication, public availability, task relevance, and manageable size.

## 2. Candidate Datasets

### 2.1 UStAI

**Reference:** Yamani, Baslyman, and Ahmed, "Leveraging LLMs for User Stories in AI Systems: UStAI Dataset," PROMISE 2025.

**Dataset:** https://github.com/asmayamani/UStAI

UStAI provides LLM-generated user stories for AI systems. The downloaded files contain 3,440 generated stories and a subset of 1,260 annotated stories.

The annotations include quality attributes based on the Quality User Story (QUS) framework, such as atomicity, minimality, conceptual soundness, ambiguity, and estimability.

**Assessment:** UStAI is publicly available, published in a peer-reviewed conference, and manageable in size. However, it primarily contains generated user stories rather than original stories paired with gold-standard refinements.

**Decision:** Retained as a reference for designing the User Story Evaluation Rubric. Not selected as the experimental dataset.

### 2.2 Dalpiaz User Story Dataset

**Reference:** F. Dalpiaz, "Requirements data sets (user stories)," 2018.

**Dataset:** https://zenodo.org/records/13880060

**DOI:** https://doi.org/10.17632/7zbk8zsd8y.2

The dataset contains 22 collections of requirements expressed as user stories. It was originally used in experiments on ambiguity detection with REVV-Light.

Our downloaded collection contains 1,680 user stories from 22 source files.

**Assessment:** The dataset is publicly available, has an archived research-data record, and has been used in published research. Its original user stories are directly suitable as inputs for refinement.

It does not provide gold-standard refined stories or acceptance criteria. Therefore, output quality will be evaluated using a task-specific rubric rather than textual similarity.

The data record is distributed under CC BY 4.0, although the curator notes uncertainty about intellectual-property rights for some original source material. Source attribution will be preserved.

**Decision:** Selected as the experimental dataset for User Story Refinement.

## 3. Final Selection

| Criterion | UStAI | Dalpiaz |
|---|---|---|
| Research publication | PROMISE 2025 | Research dataset used in ambiguity-detection experiments |
| Public availability | Yes | Yes |
| Suitable for refinement | Usable, but LLM-generated | Original user stories |
| Manageable size | Yes | Yes |
| Experimental role | Evaluation reference | Selected dataset |

## 4. Experimental Preparation

The Dalpiaz collection was processed using the following procedure:

1. Extracted 1,680 user stories from 22 text files.
2. Removed duplicate stories.
3. Filtered stories to 10–40 words, retaining 1,623 candidates.
4. Sampled 44 candidates from the 22 source files using a fixed random seed.
5. Selected 20 stories with identifiable opportunities for refinement.

The final selection covers 15 source files and includes ambiguity, redundancy, grammatical problems, weak benefits, and solution-oriented wording.

**Final dataset:** `data/processed/userstories_final20.csv`

**Task:** User Story Refinement

**Input:** Original user story.

**Expected output:** A refined story that improves quality while preserving the original intent.

**Evaluation:** Eight-criterion User Story Evaluation Rubric.

## 5. References

[1] A. Yamani, M. Baslyman, and M. Ahmed, "Leveraging LLMs for User Stories in AI Systems: UStAI Dataset," in *Proceedings of PROMISE*, 2025, pp. 21–30. doi: 10.1145/3727582.3728689.

[2] F. Dalpiaz, "Requirements data sets (user stories)," Mendeley Data, Version 2, 2024. doi: 10.17632/7zbk8zsd8y.2.

[3] F. Dalpiaz, "Requirements data sets (user stories)," Zenodo, Version 1, 2018. https://zenodo.org/records/13880060
