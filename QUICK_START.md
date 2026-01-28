# Quick Start Guide: Ralph + RLM Integration

## Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Verify RLM installation**:
```bash
python -c "from agents import RLMExecutor; print('✅ RLM ready')"
```

## Testing the Integration

### Option 1: Run Integration Test
```bash
cd examples
python test_ralph_integration.py
```

This creates a sample PRD in `tasks/backend_prd.json` for testing.

### Option 2: Simple Calculator Example

1. **Send to Telegram bot**:
```
Create a simple calculator with add and subtract functions
```

2. **PM agent will**:
   - Create `tasks/backend_prd.json` with 2 stories
   - Launch backend agent

3. **Backend agent will**:
   - **Iteration 1**: 
     - Read PRD
     - Find Task #1 (add function)
     - Implement `calculator.py`
     - Write tests
     - Run pytest/mypy/ruff
     - Commit changes
     - Mark task #1 as `passes: true`
     - Update `tasks/backend_progress.txt`
   
   - **Iteration 2**:
     - Read PRD again (fresh context)
     - Find Task #2 (subtract function)
     - Implement subtract()
     - Write tests
     - Run quality checks
     - Commit changes
     - Mark task #2 as `passes: true`
     - Update progress file
   
   - **Report**: "2/2 tasks complete"

4. **PM agent will**:
   - Monitor progress
   - Report to user: "✅ Calculator complete!"

## Understanding the Files

### PRD File: `tasks/backend_prd.json`
```json
{
  "featureName": "Simple Calculator",
  "branchName": "test/calculator",
  "agent": "backend",
  "userStories": [
    {
      "id": 1,
      "title": "Add Function",
      "passes": false  // ← Agent updates this
    }
  ]
}
```

### Progress File: `tasks/backend_progress.txt`
```
## Task #1: Add Function
Completed: 2026-01-28 10:30:00

Learnings:
- Created calculator.py in project root
- Used pytest for testing
- All type hints added for mypy

Files modified:
- calculator.py
- test_calculator.py
```

### Git Commits
```
[backend] Task #1: Add Function

Implemented by autonomous agent.
All quality checks passing.
```

## Monitoring Progress

### Check PRD status
```bash
cat tasks/backend_prd.json | grep "passes"
```

### Check progress logs
```bash
cat tasks/backend_progress.txt
```

### Check git history
```bash
git log --grep="autonomous agent"
```

## Troubleshooting

### Agent stuck on a task?
Check `tasks/{agent}_progress.txt` for blocker documentation.

### Quality checks failing?
Agent should document in progress.txt and escalate to PM.

### PRD not created?
Verify PM agent received the feature request and check logs.

## Advanced Usage

### Custom RLM Environment
```python
from agents import RLMExecutor

# Use Modal for cloud isolation
executor = RLMExecutor(environment="modal")
```

### Multiple Features
PM can handle multiple PRDs simultaneously:
- `tasks/feature1_backend_prd.json`
- `tasks/feature1_frontend_prd.json`
- `tasks/feature2_backend_prd.json`

### Dependency Management
Frontend PRD waits for backend completion:
```json
{
  "agent": "frontend",
  "dependencies": ["backend"]  // ← Won't start until backend done
}
```

## What to Expect

### Single Feature (e.g., Calculator)
- **Time**: 2-10 minutes per task
- **Commits**: 1 per completed story
- **Output**: Working, tested code

### Complex Feature (e.g., User Auth)
- **Backend PRD**: 5-8 stories (DB, API, validation)
- **Frontend PRD**: 4-6 stories (login form, signup, session)
- **QA PRD**: 3-5 stories (security tests, E2E tests)
- **Total time**: Runs autonomously for hours
- **Result**: Fully tested, integrated feature

## Success Indicators

✅ PRD files created in `tasks/`
✅ Progress files being updated
✅ Git commits per completed task
✅ Quality checks passing
✅ All stories marked `passes: true`
✅ PM reports completion to user

## Next Steps

After successful test:
1. Try more complex features
2. Monitor autonomous iterations
3. Review progress files for learnings
4. Adjust PRD templates as needed

Happy autonomous coding! 🤖✨
