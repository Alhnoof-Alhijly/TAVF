
# TAVF Development Environment

## 1. Development Tools

- Operating System: Windows
- IDE: Visual Studio Code
- Python: 3.14.4
- Version Control: Git and GitHub

## 2. Virtual Environment

Create the virtual environment:

```powershell
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

## 3. Dependencies

Install the required Python packages:

```powershell
python -m pip install -r requirements.txt
```

Main libraries:
- OpenAI SDK
- pandas
- pyarrow
- python-dotenv

## 4. API Configuration

Create a `.env` file in the project root.

```env
OPENAI_API_KEY=your_api_key_here
```

The `.env` file must be excluded from Git using `.gitignore`.

## 5. Environment Verification

Verify Python and the installed libraries:

```powershell
python --version
python -c "import openai, pandas, pyarrow, dotenv; print('Environment OK')"
```

## 6. Known Limitation

The OpenAI SDK is installed and imports successfully.

The API connection test is currently blocked by insufficient API credits. Credits must be available before running the baseline experiment.
