---
applyTo: '**'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.

**Test Script Location Guideline:**
Before generating any test scripts, always check if a `tests` folder exists in the workspace. If it does, save all new test scripts in that folder.

**Important:** Never attempt to create or manage Python environments (e.g., virtualenv, conda, venv) in any model or automation. Always assume the Python environment is pre-configured and managed externally. Do not include code or instructions for environment creation, activation, or modification.

**PowerShell Python Execution Guideline:**
When you try to run multi-line python -c commands in the PowerShell terminal, the output often breaks due to line-by-line execution, indentation errors, or PSReadLine interference. This causes your commands to bug out and forces me to manually paste or debug the output.

To avoid this, do not generate inline python -c scripts in the terminal. Instead, create a temporary .py file with the same contents, save it to the workspace (e.g. test_imports.py), and run it using:

```powershell
python .\test_imports.py
```

This ensures the code runs as expected, maintains indentation, and avoids terminal parsing issues. Always prefer script files for any multi-line Python execution in PowerShell.