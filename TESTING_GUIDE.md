# Testing Guide: Comparing Agents Before & After Ralph Integration

## Overview

This guide helps you test and compare agent behavior before and after the Ralph + RLM integration using simple, controlled projects.

## Testing Strategy

### Before Integration (Baseline)
Agents work in a more interactive, conversational mode:
- Require more human guidance
- May ask clarifying questions
- Work on tasks one at a time with feedback loops
- No structured PRD tracking
- No autonomous iteration loops

### After Integration (Ralph Pattern)
Agents work autonomously:
- Follow structured PRD workflows
- Iterate through tasks independently
- Track progress in progress.txt files
- Create git commits per task
- Run quality gates automatically

## Simple Test Projects

### Test 1: Simple Calculator (Backend Only)
**Estimated time:** 5-10 minutes

**Request:**
```
Create a simple calculator with add and subtract functions
```

**Before Integration - Expected Behavior:**
1. Agent asks clarifying questions about requirements
2. Implements both functions in one go
3. May or may not write tests without prompting
4. Single commit or manual commit prompting
5. No structured progress tracking

**After Integration - Expected Behavior:**
1. PM creates `tasks/backend_prd.json` with 2 stories:
   - Story 1: Add function
   - Story 2: Subtract function
2. Backend agent works autonomously:
   - **Iteration 1:** Implements add() → tests → commit → marks complete
   - **Iteration 2:** Implements subtract() → tests → commit → marks complete
3. Creates `tasks/backend_progress.txt` with learnings
4. Two separate git commits
5. Quality checks (pytest, mypy, ruff) run automatically

**How to Verify:**
```bash
# Check PRD was created
cat tasks/backend_prd.json | jq '.userStories[] | {id, title, passes}'

# Check progress file exists
cat tasks/backend_progress.txt

# Check git commits
git log --oneline --grep="\[backend\]"

# Should see 2 commits:
# [backend] Task #2: Subtract Function
# [backend] Task #1: Add Function
```

---

### Test 2: Todo List API (Backend + Frontend)
**Estimated time:** 20-30 minutes

**Request:**
```
Create a simple todo list API with a web interface
```

**Before Integration - Expected Behavior:**
1. Backend and frontend might work simultaneously
2. Coordination happens through human oversight
3. May have integration issues that require manual fixing
4. Commits are ad-hoc
5. Testing may be incomplete

**After Integration - Expected Behavior:**
1. PM creates 3 PRD files:
   - `tasks/backend_prd.json` - API endpoints, data models
   - `tasks/frontend_prd.json` - UI components, API integration
   - `tasks/qa_prd.json` - Tests and validation
2. Agents work in sequence:
   - Backend completes first (no dependencies)
   - Frontend waits for backend, then proceeds
   - QA validates both
3. Each agent creates progress.txt
4. Multiple commits per agent
5. All quality gates pass

**How to Verify:**
```bash
# Check all PRDs exist
ls tasks/*_prd.json

# Check dependency order was followed
# Backend should have earlier commits than frontend
git log --all --graph --decorate --oneline

# Verify all tasks completed
for file in tasks/*_prd.json; do
  echo "=== $file ==="
  cat $file | jq '.userStories[] | select(.passes == false) | {id, title}'
done
# Should return empty (all tasks passed)

# Check progress files
ls tasks/*_progress.txt
```

---

### Test 3: User Authentication (Full Stack)
**Estimated time:** 45-60 minutes

**Request:**
```
Add user authentication with login and signup
```

**Before Integration - Expected Behavior:**
1. Back-and-forth conversations about security requirements
2. Implementation may miss security best practices
3. Tests may be incomplete
4. Manual coordination between backend/frontend
5. No structured tracking of security checklist

**After Integration - Expected Behavior:**
1. PM creates comprehensive PRDs covering:
   - Backend: User model, password hashing, JWT, API endpoints
   - Frontend: Login form, signup form, session management
   - QA: Security tests, OWASP checks, integration tests
2. Quality gates enforce security:
   - Backend: Must pass security linting
   - QA: Must validate auth flows, check for vulnerabilities
3. Progress tracking documents security learnings
4. Each agent follows security best practices autonomously

**How to Verify:**
```bash
# Check security-related tasks were completed
cat tasks/backend_prd.json | jq '.userStories[] | select(.title | contains("password") or contains("security"))'

# Check QA validated security
cat tasks/qa_progress.txt | grep -i "security\|owasp\|authentication"

# Verify password hashing was implemented (not plaintext)
grep -r "bcrypt\|argon2\|scrypt" --include="*.py"

# Check for security anti-patterns (should find none)
grep -r "password.*plain\|sha1" --include="*.py"
```

---

## Comparison Metrics

### Autonomy Level
**Before:** Requires human intervention every few steps
**After:** Runs for 30-60 minutes autonomously per feature

### Quality Consistency
**Before:** Quality depends on explicit human prompting
**After:** Quality gates enforced automatically

### Progress Tracking
**Before:** No structured tracking
**After:** PRD + progress.txt provide full audit trail

### Git History
**Before:** Large commits with multiple changes
**After:** Small, atomic commits per task

### Test Coverage
**Before:** Variable, often incomplete
**After:** Required by quality gates

---

## Quick Comparison Checklist

Run this checklist for any test project:

### ✅ Before Integration
- [ ] How many times did you need to intervene?
- [ ] Were tests written without prompting?
- [ ] Were quality checks run automatically?
- [ ] Can you reconstruct what was done from git history?
- [ ] Was there a structured plan followed?

### ✅ After Integration
- [ ] Was a PRD created automatically?
- [ ] Did agents work through tasks sequentially?
- [ ] Were quality checks run before commits?
- [ ] Are there progress.txt files with learnings?
- [ ] Are git commits atomic and well-described?
- [ ] Did dependency order work (backend → frontend → QA)?

---

## Side-by-Side Test

For the most accurate comparison, run the same test twice:

### Setup
```bash
# Create two test directories
mkdir -p ~/test-before-ralph
mkdir -p ~/test-after-ralph

# Switch to before integration (remove Ralph changes)
cd ~/test-before-ralph
# ... run test with original agent configs

# Switch to after integration (with Ralph)
cd ~/test-after-ralph
# ... run test with Ralph-enabled agents
```

### Run Test
1. **Send same request to both setups:**
   ```
   Create a simple calculator with add and subtract functions
   ```

2. **Time the execution:**
   - Note when you send the request
   - Note when agents report completion
   - Count human interventions needed

3. **Compare outputs:**
   ```bash
   # Compare git logs
   cd ~/test-before-ralph && git log --oneline > ../before-commits.txt
   cd ~/test-after-ralph && git log --oneline > ../after-commits.txt
   diff ../before-commits.txt ../after-commits.txt
   
   # Compare file structure
   tree ~/test-before-ralph > ../before-structure.txt
   tree ~/test-after-ralph > ../after-structure.txt
   diff ../before-structure.txt ../after-structure.txt
   ```

---

## Observing Ralph Loop in Action

To see the autonomous iteration pattern working:

### 1. Watch PRD Updates
```bash
# Open in separate terminal
watch -n 2 'cat tasks/backend_prd.json | jq ".userStories[] | {id, title, passes}"'
```

You'll see `passes` change from `false` to `true` as agent completes tasks.

### 2. Monitor Progress File
```bash
# Tail the progress file
tail -f tasks/backend_progress.txt
```

Watch learnings being added after each task completion.

### 3. Watch Git Commits
```bash
# In another terminal
watch -n 5 'git log --oneline -5'
```

See commits appear as each task completes.

### 4. Check Quality Gates
```bash
# Monitor test runs
watch -n 3 'pytest --tb=line 2>&1 | tail -20'
```

See tests running between iterations.

---

## Red Flags (Things That Shouldn't Happen)

### ❌ Before Integration
- Agent gets stuck in loops asking same questions
- No tests written unless explicitly requested
- Large monolithic commits
- Inconsistent code quality

### ❌ After Integration (Needs Debugging)
- PRD not created by PM
- Agent skips quality gates
- `passes: false` never changes to `true`
- No progress.txt updates
- Commits missing or malformed
- Agent escalates immediately without trying

---

## Success Indicators

### ✅ After Integration Working Well
- PRD created within 1 minute of request
- Agent completes 2-3 tasks per 10 minutes
- Each task has atomic commit
- All quality gates pass before commit
- Progress file grows with each iteration
- All stories marked `passes: true` at end
- PM reports completion summary to user

---

## Troubleshooting Tests

### PRD Not Created
**Check:** PM agent prompt has PRD Generation section
```bash
grep -A 5 "PRD Generation" opencode/.config/agent/project-manager.md
```

### Agent Not Iterating
**Check:** Agent has Ralph Loop section
```bash
grep -A 5 "Autonomous Work Pattern" opencode/.config/agent/backend.md
```

### Quality Gates Not Running
**Check:** Quality checks are defined in Ralph Loop
```bash
grep -A 3 "Quality Checks" opencode/.config/agent/backend.md
```

### No Git Commits
**Check:** Commit step is in workflow
```bash
grep -A 5 "Commit Changes" opencode/.config/agent/backend.md
```

---

## Recommended Test Sequence

Start simple and increase complexity:

1. **Day 1:** Calculator (backend only)
   - Validates: Basic Ralph loop, PRD creation, commits

2. **Day 2:** Todo List (backend + frontend)
   - Validates: Multi-agent coordination, dependencies

3. **Day 3:** Authentication (full stack + QA)
   - Validates: Security, complete workflow, QA integration

4. **Day 4:** Complex feature (e.g., payment integration)
   - Validates: Real-world complexity, error handling, escalation

---

## Measuring Improvements

Track these metrics across tests:

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Time to completion | ? min | ? min | ?% faster/slower |
| Human interventions | ? times | ? times | ?% reduction |
| Test coverage | ?% | ?% | ?% increase |
| Commit quality | subjective | atomic | better |
| Progress visibility | none | full audit | complete |
| Autonomous work time | 5-10 min | 30-60 min | 3-6x increase |
| **Accuracy score** | **?/10** | **?/10** | **see below** |
| **Total cost (USD)** | **$?** | **$?** | **?% difference** |

---

## Accuracy Comparison

### Accuracy Scoring Framework

Rate each completed feature on a scale of 1-10 across these dimensions:

#### 1. Functional Correctness (0-10 points)
- **10:** All features work perfectly, no bugs
- **8:** Minor bugs that don't affect core functionality
- **6:** Some features broken, workarounds needed
- **4:** Major functionality broken
- **2:** Barely functional
- **0:** Completely broken

**How to measure:**
```bash
# Run all tests
pytest --cov --cov-report=term-missing

# Manual testing checklist
# - Try all user flows
# - Test edge cases
# - Verify error handling
# - Check validation
```

#### 2. Code Quality (0-10 points)
- **10:** Clean, idiomatic, well-structured, follows best practices
- **8:** Good quality, minor style issues
- **6:** Works but has code smells
- **4:** Messy, hard to maintain
- **2:** Barely readable
- **0:** Unmaintainable spaghetti

**How to measure:**
```bash
# Backend Python
ruff check . --statistics
mypy . --strict
radon cc . -a  # Cyclomatic complexity

# Frontend TypeScript
eslint . --format=json | jq '.[] | .errorCount, .warningCount'
tsc --noEmit
```

#### 3. Test Coverage (0-10 points)
- **10:** >90% coverage, all edge cases tested
- **8:** 70-90% coverage, main flows tested
- **6:** 50-70% coverage, basic tests
- **4:** 30-50% coverage, minimal tests
- **2:** <30% coverage
- **0:** No tests

**How to measure:**
```bash
# Backend
pytest --cov --cov-report=term
# Look for coverage %

# Frontend
npm test -- --coverage
# Check coverage/lcov-report/index.html
```

#### 4. Security & Best Practices (0-10 points)
- **10:** All security best practices followed
- **8:** Minor security improvements possible
- **6:** Some security concerns
- **4:** Notable vulnerabilities
- **2:** Major security issues
- **0:** Critical vulnerabilities

**How to measure:**
```bash
# Python security scan
bandit -r . -f json

# Dependency vulnerabilities
pip-audit
npm audit

# Check for common issues
grep -r "TODO\|FIXME\|XXX" --include="*.py" --include="*.ts"
```

#### 5. Completeness (0-10 points)
- **10:** All requirements met, polished
- **8:** Core requirements met, minor gaps
- **6:** Most requirements met
- **4:** Significant gaps
- **2:** Many missing features
- **0:** Mostly incomplete

**How to measure:**
```bash
# Compare against original request
# - List all requested features
# - Check each is implemented
# - Verify acceptance criteria met

# For Ralph: Check PRD completion
cat tasks/backend_prd.json | jq '[.userStories[].passes] | add / length * 100'
# Should be 100% if complete
```

### Accuracy Score Calculation

```
Total Accuracy = (Functional + Quality + Coverage + Security + Completeness) / 5
```

### Expected Accuracy Differences

**Before Integration:**
- Functional: 7-8/10 (works but may have bugs)
- Quality: 6-7/10 (inconsistent without quality gates)
- Coverage: 4-6/10 (tests optional, often skipped)
- Security: 5-7/10 (depends on explicit prompting)
- Completeness: 6-8/10 (may miss edge cases)
- **Average: 5.6-7.2/10**

**After Integration (Ralph):**
- Functional: 8-9/10 (quality gates prevent broken code)
- Quality: 8-9/10 (linting/typecheck enforced)
- Coverage: 7-9/10 (tests required before commit)
- Security: 7-9/10 (security checks in QA PRD)
- Completeness: 8-10/10 (PRD ensures all features)
- **Average: 7.6-9.2/10**

**Expected improvement: +20-35% accuracy**

---

## Cost Comparison

### Cost Components

#### 1. LLM API Costs

**Track token usage for each test:**

```python
# Add to your OpenCode integration
import json
from datetime import datetime

class CostTracker:
    def __init__(self):
        self.sessions = []
    
    def log_api_call(self, model, input_tokens, output_tokens):
        cost = self.calculate_cost(model, input_tokens, output_tokens)
        self.sessions.append({
            'timestamp': datetime.now().isoformat(),
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost': cost
        })
    
    def calculate_cost(self, model, input_tokens, output_tokens):
        # Pricing as of Jan 2026 (update with current rates)
        rates = {
            'claude-sonnet-4.5': {
                'input': 0.003,   # per 1K tokens
                'output': 0.015
            },
            'gpt-4-turbo': {
                'input': 0.01,
                'output': 0.03
            },
            'claude-3-opus': {
                'input': 0.015,
                'output': 0.075
            }
        }
        
        rate = rates.get(model, rates['claude-sonnet-4.5'])
        cost = (input_tokens / 1000 * rate['input'] + 
                output_tokens / 1000 * rate['output'])
        return cost
    
    def total_cost(self):
        return sum(s['cost'] for s in self.sessions)
    
    def report(self):
        total = self.total_cost()
        total_tokens = sum(s['input_tokens'] + s['output_tokens'] 
                          for s in self.sessions)
        return {
            'total_cost': f"${total:.4f}",
            'total_tokens': total_tokens,
            'api_calls': len(self.sessions),
            'breakdown': self.sessions
        }

# Usage
tracker = CostTracker()
# Log each API call from your webhook/integration
# tracker.log_api_call('claude-sonnet-4.5', input_tokens=5000, output_tokens=1500)

# At end of test
print(json.dumps(tracker.report(), indent=2))
```

#### 2. Cost Tracking Methods

**Method A: API Response Headers**
Most LLM APIs return token usage:
```python
# OpenAI
response = client.chat.completions.create(...)
usage = response.usage
print(f"Input: {usage.prompt_tokens}, Output: {usage.completion_tokens}")

# Anthropic Claude
response = client.messages.create(...)
usage = response.usage
print(f"Input: {usage.input_tokens}, Output: {usage.output_tokens}")
```

**Method B: Log File Analysis**
```bash
# If your integration logs API calls
grep "API_CALL" opencode.log | \
  jq -s '[.[] | .tokens] | {total: add, calls: length}'
```

**Method C: Manual Token Estimation**
```bash
# Count tokens approximately (rough estimate: 4 chars = 1 token)
total_chars=$(cat tasks/*.json tasks/*.txt | wc -m)
estimated_tokens=$((total_chars / 4))
echo "Estimated tokens: $estimated_tokens"
```

#### 3. Cost Comparison Framework

| Cost Factor | Before Integration | After Integration | Analysis |
|-------------|-------------------|-------------------|----------|
| **Iterations** | More back-and-forth | Autonomous loops | 📊 Measure iteration count |
| **Context loading** | Repeated context | Fresh context per iteration | 📊 Compare context sizes |
| **Failed attempts** | Trial and error | Quality gates prevent | 📊 Count failed commits |
| **Planning overhead** | Ad-hoc | Upfront PRD creation | 📊 Compare initial tokens |
| **Total tokens** | Variable | More predictable | 📊 Sum all API calls |

#### 4. Expected Cost Patterns

**Before Integration:**
```
Typical Calculator Test:
- Initial planning: 3-5K tokens
- Implementation: 8-12K tokens  
- Back-and-forth (3-5 iterations): 15-25K tokens
- Bug fixes: 5-10K tokens
- Total: ~30-50K tokens
- Cost: $0.15 - $0.30 (Claude Sonnet 4.5)
```

**After Integration:**
```
Typical Calculator Test:
- PRD creation: 5-8K tokens (more structured)
- Iteration 1: 10-15K tokens (includes context loading)
- Iteration 2: 10-15K tokens (fresh context)
- Quality checks: 3-5K tokens per iteration
- Total: ~35-60K tokens
- Cost: $0.20 - $0.40 (Claude Sonnet 4.5)
```

**Initial observation: Ralph may cost 15-30% more in tokens** due to:
- Fresh context loading each iteration
- Reading git history and progress files
- More structured planning (PRD)
- Quality gate execution

**BUT: Higher accuracy reduces downstream costs:**
- Fewer bugs to fix later: -$0.50 to -$2.00
- Less human debugging time: -2 to -5 hours
- Better test coverage: prevents production issues

#### 5. True Cost Calculation

Include human time in cost analysis:

```
True Cost = LLM API Cost + (Human Time × Hourly Rate)

Before Integration:
- LLM: $0.20
- Human interventions: 5 × 5 min = 25 min
- Human cost (@ $100/hr): $41.67
- Total: $41.87

After Integration:
- LLM: $0.35
- Human interventions: 0-1 × 5 min = 5 min  
- Human cost (@ $100/hr): $8.33
- Total: $8.68

Savings: $33.19 per feature (79% reduction)
```

#### 6. Cost Tracking Template

Create a cost log for each test:

```json
{
  "test_name": "calculator",
  "date": "2026-01-28",
  "integration": "after",
  "llm_costs": {
    "model": "claude-sonnet-4.5",
    "total_tokens": 45000,
    "input_tokens": 30000,
    "output_tokens": 15000,
    "cost_usd": 0.315
  },
  "human_costs": {
    "interventions": 1,
    "time_minutes": 5,
    "hourly_rate": 100,
    "cost_usd": 8.33
  },
  "total_cost_usd": 8.645,
  "accuracy_score": 8.6,
  "cost_per_accuracy_point": 1.01,
  "notes": "Single intervention to approve feature completion"
}
```

#### 7. Cost Optimization Tips

**For Ralph Integration:**
- Tune PRD granularity (fewer, larger stories = less context reloading)
- Optimize progress.txt format (concise learnings)
- Cache common patterns in agent prompts
- Use smaller models for quality checks (gpt-4-turbo-mini)
- Batch related tasks to reduce iterations

**Cost vs Accuracy Trade-off:**
```
High Accuracy + Lower Cost:
- Use Ralph for complex features (worth the setup)
- Use traditional for simple fixes
- Optimize PRD templates over time
- Monitor cost per feature type

Measure ROI:
ROI = (Accuracy Improvement × Business Value - Extra LLM Cost) / Total Cost
```

### Cost Comparison Checklist

For each test, record:

- [ ] Total API tokens used
- [ ] Number of API calls
- [ ] LLM cost ($)
- [ ] Human interventions count
- [ ] Human time spent (minutes)
- [ ] Total true cost ($)
- [ ] Accuracy score (/10)
- [ ] Cost per accuracy point ($/point)
- [ ] Bug count post-implementation
- [ ] Time to production readiness

### Sample Comparison Table

| Metric | Before Ralph | After Ralph | Difference |
|--------|-------------|-------------|------------|
| LLM tokens | 35,000 | 45,000 | +28.6% |
| LLM cost | $0.21 | $0.32 | +52.4% |
| Human interventions | 5 | 1 | -80% |
| Human time | 25 min | 5 min | -80% |
| Human cost (@$100/hr) | $41.67 | $8.33 | -80% |
| **Total cost** | **$41.88** | **$8.65** | **-79.3%** |
| Accuracy score | 6.4/10 | 8.6/10 | +34.4% |
| Bugs found | 3 | 0 | -100% |
| **Cost per accuracy point** | **$6.54** | **$1.01** | **-84.6%** |

---

## Next Steps

After testing:

1. **Document findings:** Create a comparison report
2. **Tune PRD templates:** Adjust based on what works
3. **Refine quality gates:** Add project-specific checks
4. **Train team:** Share successful patterns
5. **Scale up:** Try on real project features

---

## Example Test Session Log

```
[09:00] Request sent: "Create a calculator"
[09:01] PM creates backend_prd.json with 2 stories
[09:02] Backend agent starts iteration 1
[09:05] Tests pass, commit created for add()
[09:06] Backend agent starts iteration 2
[09:09] Tests pass, commit created for subtract()
[09:10] Backend reports: "2/2 tasks complete"
[09:10] PM reports to user: "✅ Calculator complete!"

Total time: 10 minutes
Human interventions: 0
Quality: All tests pass, 100% coverage
Commits: 2 atomic commits
```

Compare this to your baseline!

---

## Support

If tests reveal issues:
1. Check IMPLEMENTATION_CHECKLIST.md for setup verification
2. Review RALPH_RLM_INTEGRATION.md for configuration
3. Check agent prompts for Ralph Loop sections
4. Verify git is initialized in workspace
5. Ensure Python environment is set up

Happy testing! 🧪✨
