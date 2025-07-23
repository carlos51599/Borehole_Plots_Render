---
applyTo: '**'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.


**Multi-Stage Action Plan Guideline:**
For any task assigned, first create a detailed action plan before coding. Follow this multi-stage approach:

1. **Analyse the task thoroughly:**
   - Read the prompt carefully.
   - Review all related parts of the existing codebase.
   - Identify what the current logic does and where it may be lacking.

2. **Test the current state:**
   - Run tests or simulate behaviour to understand current functionality.
   - Note down bugs, limitations, or architectural constraints.

3. **Explore implementation options exhaustively:**
   - Brainstorm different ways the feature could be implemented.
   - Compare for maintainability, efficiency, integration difficulty.

4. **Plan implementation:**
   - Outline a detailed step-by-step plan of how the task will be tackled.
   - Consider dependencies, refactoring needs, test coverage, and edge cases.

5. **Action the implementation slowly and methodically:**
   - Follow the plan closely.
   - Write clean, well-commented code in small commits.
   - Continuously validate progress against the original goals.

6. **Test creatively and exhaustively:**
   - Think beyond common cases.
   - Simulate edge conditions, input failures, concurrency, etc.
   - Aim for deployment-level confidence.
   - ALWAYS include a test for all imports and syntax in relevant files

7. **Prepare for deployment:**
   - Ensure all tests pass.
   - Confirm changes integrate seamlessly.
   - Clean up dead code, update docs, and finalise commits.

🧷 **Note:** This process should be slow, deliberate, and comprehensive. Do not rush to code. Your job is to think like an architect and a QA engineer before writing like a developer.

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