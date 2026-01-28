"""
Integration test for Ralph + RLM autonomous agent pattern
"""

import json
from pathlib import Path


def test_backend_agent_autonomous_work():
    """
    Test backend agent can work autonomously through a simple PRD
    """
    # Create test PRD
    test_prd = {
        "featureName": "Simple Calculator",
        "branchName": "test/calculator",
        "overview": "Basic calculator with add/subtract",
        "agent": "backend",
        "userStories": [
            {
                "id": 1,
                "title": "Add Function",
                "priority": 1,
                "description": "Implement add(a, b) function",
                "acceptanceCriteria": [
                    "Function exists in calculator.py",
                    "Function returns sum of a and b",
                    "Tests pass"
                ],
                "technicalNotes": [
                    "Create calculator.py",
                    "Write tests in test_calculator.py"
                ],
                "passes": False
            }
        ]
    }
    
    # Save PRD
    tasks_dir = Path("tasks")
    tasks_dir.mkdir(exist_ok=True)
    
    with open(tasks_dir / "backend_prd.json", "w") as f:
        json.dump(test_prd, f, indent=2)
    
    print("✅ Test PRD created")
    print("📋 Next: Invoke backend agent with this PRD")
    print("   Agent should:")
    print("   1. Read tasks/backend_prd.json")
    print("   2. Implement calculator.py with add() function")
    print("   3. Write tests")
    print("   4. Mark story as passes=true")
    print("   5. Update tasks/backend_progress.txt")


if __name__ == "__main__":
    test_backend_agent_autonomous_work()
