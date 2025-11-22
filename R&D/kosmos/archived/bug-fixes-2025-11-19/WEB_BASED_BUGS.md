# Web-Based Claude Code Bugs - Kosmos AI Scientist v0.2.0

**Total Bugs: 31**
**Type: Bugs that can be fixed through code inspection without test execution**
**Date: 2025-11-19**

These bugs can be confidently fixed through code review alone as they involve:
- Clear syntax errors
- Missing imports or dependencies
- Method signature mismatches visible in code
- Configuration issues with clear documentation
- Type mismatches evident from code review
- Deprecated API usage

---

## CRITICAL SEVERITY (8 bugs)
*Application cannot start or immediate crash issues*

### 1. Pydantic V2 Configuration Parsing Failure
- **File:** `kosmos/config.py`
- **Line:** BaseSettings implementation
- **Error:** `SettingsError: error parsing value for field "enabled_domains" from source "EnvSettingsSource"`
- **Root Cause:** Pydantic V2 requires JSON format `["chemistry","physics"]` but .env uses `chemistry,physics`
- **Fix:** Add BeforeValidator to parse comma-separated strings:
```python
from pydantic import field_validator, BeforeValidator
from typing import Annotated

def parse_comma_separated(v):
    if isinstance(v, str):
        return [x.strip() for x in v.split(',')]
    return v

enabled_domains: Annotated[List[str], BeforeValidator(parse_comma_separated)]
```
- **Confidence:** 100%

### 2. Missing `psutil` Dependency
- **File:** `pyproject.toml`
- **Import Location:** `kosmos/api/health.py:12`
- **Error:** `ModuleNotFoundError: No module named 'psutil'`
- **Fix:** Add to dependencies section: `psutil = "^5.9.0"`
- **Confidence:** 100%

### 3. Missing `redis` Dependency
- **File:** `pyproject.toml`
- **Import Location:** `kosmos/api/health.py:230`
- **Error:** `ModuleNotFoundError: No module named 'redis'`
- **Fix:** Add to dependencies section: `redis = "^5.0.0"`
- **Confidence:** 100%

### 4. Workflow State String Case Mismatch
- **File:** `kosmos/cli/commands/run.py`
- **Lines:** 248-259
- **Issue:** Comparing UPPERCASE strings against lowercase enum values
- **Current Code:** `if task_status == "COMPLETED":`
- **Fix:** `if task_status.lower() == WorkflowState.COMPLETED.value:`
- **Confidence:** 95%

### 5. World Model `create_paper()` Method - Wrong Parameter Format
- **File:** `kosmos/world_model/simple.py`
- **Lines:** 144-155
- **Issue:** Method signature doesn't match interface
- **Fix:** Update parameter structure to match interface definition
- **Confidence:** 90%

### 6. World Model `create_concept()` Method - Extra Metadata Parameter
- **File:** `kosmos/world_model/simple.py`
- **Lines:** 171-176
- **Issue:** Extra `metadata` parameter not in interface
- **Fix:** Remove `metadata` parameter from method signature
- **Confidence:** 90%

### 7. Non-existent scipy Function Import
- **File:** `kosmos/domains/neuroscience/neurodegeneration.py`
- **Line:** 485
- **Error:** `ImportError: cannot import name 'false_discovery_control'`
- **Current:** `from scipy.stats import false_discovery_control`
- **Fix:** `from statsmodels.stats.multitest import multipletests`
- **Confidence:** 95%

### 8. Missing pytest e2e Marker
- **File:** `pytest.ini`
- **Error:** `pytest: error: 'e2e' not found in markers configuration`
- **Fix:** Add to `[tool.pytest.ini_options]` markers section:
```ini
markers = [
    "e2e: end-to-end tests",
    ...existing markers...
]
```
- **Confidence:** 100%

---

## HIGH SEVERITY (12 bugs)
*Common path failures affecting standard workflows*

### 9. Provider Type Mismatch in Fallback
- **File:** `kosmos/core/llm.py`
- **Lines:** 651-652
- **Error:** `TypeError: Expected LLMProvider, got <class 'ClaudeClient'>`
- **Fix:** Pass LLMProvider instance instead of class reference
- **Confidence:** 90%

### 10. Pydantic Validator Accessing Raw Dicts
- **File:** `kosmos/models/result.py`
- **Lines:** 209-217
- **Error:** `AttributeError: 'dict' object has no attribute 'test_name'`
- **Current:** `values.test_name`
- **Fix:** `values['test_name']`
- **Confidence:** 95%

### 11. Missing `get_pqtl()` Biology API Method
- **File:** `kosmos/domains/biology/genomics.py`
- **Line:** 231
- **Issue:** Method called but not implemented
- **Fix:** Implement method following pattern of similar methods like `get_eqtl()`
- **Confidence:** 85%

### 12. Missing `get_atac_peaks()` Biology API Method
- **File:** `kosmos/domains/biology/genomics.py`
- **Line:** 237
- **Issue:** Method called but not implemented
- **Fix:** Implement method following pattern of similar methods
- **Confidence:** 85%

### 13. Missing StatisticalTestResult.is_primary Field
- **File:** `kosmos/analysis/summarizer.py`
- **Line:** 189
- **Error:** `AttributeError: 'StatisticalTestResult' object has no attribute 'is_primary'`
- **Fix:** Add `is_primary: bool = False` to StatisticalTestResult model
- **Confidence:** 95%

### 14. Missing ExperimentResult CI Fields
- **File:** `kosmos/analysis/summarizer.py`
- **Line:** 280
- **Error:** `AttributeError: 'ExperimentResult' object has no attribute 'primary_ci_lower'`
- **Fix:** Add fields to ExperimentResult model:
```python
primary_ci_lower: Optional[float] = None
primary_ci_upper: Optional[float] = None
```
- **Confidence:** 95%

### 15. Enum.lower() Method Call
- **File:** `kosmos/execution/code_generator.py`
- **Lines:** 65, 139, 154
- **Error:** `AttributeError: 'StatisticalTest' object has no attribute 'lower'`
- **Current:** `test_type.lower()`
- **Fix:** `test_type.value.lower()` or `test_type.name.lower()`
- **Confidence:** 95%

### 16. Missing Result Exclusion Keys
- **File:** `kosmos/execution/result_collector.py`
- **Line:** 365
- **Issue:** Duplicate keys in StatisticalTestResult serialization
- **Fix:** Add missing fields to `exclude_keys_list`
- **Confidence:** 90%

### 17. Cache Type Enum Mismatch
- **File:** `kosmos/cli/commands/cache.py`
- **Line:** 264
- **Error:** `KeyError: 'GENERAL'`
- **Current:** `cache_type = "GENERAL"`
- **Fix:** `cache_type = CacheType.GENERAL`
- **Confidence:** 95%

### 18. False Positives in Code Validator
- **File:** `kosmos/safety/code_validator.py`
- **Lines:** 245-251, 267-275
- **Issue:** String matching causes false positives
- **Fix:** Replace string matching with AST parsing:
```python
import ast
tree = ast.parse(code)
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        # Check imports properly
```
- **Confidence:** 90%

### 19. Falsy Value Bug in Resource Limits
- **File:** `kosmos/safety/guardrails.py`
- **Lines:** 156-170
- **Issue:** Resource limits bypassed when set to 0
- **Current:** `if limit:`
- **Fix:** `if limit is not None:`
- **Confidence:** 95%

### 20. PerovskiteDB Type Safety
- **File:** `kosmos/domains/materials/apis.py`
- **Lines:** 682-685
- **Issue:** Pandas Series vs dict method mismatch
- **Fix:** Convert Series to dict: `result.to_dict()` before dict methods
- **Confidence:** 90%

---

## TEST FIXTURE BUGS (6 bugs)
*Test configuration issues with clear field/type mismatches*

### 21. Hypothesis Model Field: research_question_id
- **File:** `tests/integration/test_analysis_pipeline.py`
- **Issue:** Field should be `research_question` not `research_question_id`
- **Fix:** Rename field in test fixture
- **Confidence:** 95%

### 22. Hypothesis Model Field: experiment_type as string
- **File:** `tests/integration/test_analysis_pipeline.py`
- **Issue:** Using string instead of enum
- **Current:** `experiment_type="observational"`
- **Fix:** `experiment_type=ExperimentType.OBSERVATIONAL`
- **Confidence:** 95%

### 23. Hypothesis Model Field: feasibility_score
- **File:** `tests/integration/test_analysis_pipeline.py`
- **Issue:** Field doesn't exist in model
- **Fix:** Remove field or map to correct field name
- **Confidence:** 90%

### 24. ExperimentResult Model: plots_generated vs generated_files
- **File:** `tests/unit/agents/test_data_analyst.py`
- **Issue:** Incorrect field name
- **Current:** `plots_generated=[]`
- **Fix:** `generated_files=[]`
- **Confidence:** 95%

### 25. ResourceRequirements Model: Field Renames
- **File:** `tests/integration/test_analysis_pipeline.py`
- **Issues:**
  - `estimated_runtime_seconds` → `compute_hours`
  - `storage_gb` → `data_size_gb`
- **Fix:** Update field names in test fixtures
- **Confidence:** 95%

### 26. StatisticalTestSpec String vs Enum
- **File:** `tests/integration/test_execution_pipeline.py`
- **Line:** 36
- **Current:** `test_type="t_test"`
- **Fix:** `test_type=StatisticalTest.T_TEST`
- **Confidence:** 95%

---

## MEDIUM SEVERITY (5 bugs)
*Degraded functionality but not blocking*

### 27. Interactive Mode Type Inconsistency
- **File:** `kosmos/cli/interactive.py`
- **Line:** 236
- **Issue:** Type inconsistency in input/output handling
- **Fix:** Ensure consistent type handling for user input
- **Confidence:** 85%

### 28. Missing max_iterations Validation
- **File:** `kosmos/cli/interactive.py`
- **Lines:** 217-221
- **Issue:** No bounds checking on max_iterations
- **Fix:** Add validation:
```python
if max_iterations < 1 or max_iterations > 1000:
    raise ValueError("max_iterations must be between 1 and 1000")
```
- **Confidence:** 90%

### 29. Hardcoded Relative Paths (5 instances)
- **Files:** Multiple locations
- **Issue:** Using relative paths instead of configurable paths
- **Current:** `"./data"`, `"./output"`, etc.
- **Fix:** Use `Path.cwd() / "data"` or configuration-based paths
- **Confidence:** 85%

### 30. Deprecated datetime.utcnow()
- **Files:** Multiple files
- **Issue:** Deprecated in Python 3.12+
- **Current:** `datetime.utcnow()`
- **Fix:** `datetime.now(timezone.utc)`
- **Confidence:** 95%

### 31. Missing Dependency Lock File
- **File:** Repository root
- **Issue:** No `poetry.lock` file for reproducible builds
- **Fix:** Generate with `poetry lock` command
- **Confidence:** 90%

---

## Implementation Priority

### Phase 1 - Blocking Issues (Must Fix First)
1. Bug #1 - Pydantic configuration (blocks all startup)
2. Bugs #2, #3 - Missing dependencies (blocks imports)
3. Bug #8 - pytest marker (blocks test execution)

### Phase 2 - Critical Method Fixes
4. Bugs #5-7 - World model methods
5. Bugs #9-15 - Type and method issues
6. Bugs #16-20 - Configuration and validation

### Phase 3 - Test Fixtures
7. Bugs #21-26 - Test fixture field corrections

### Phase 4 - Code Quality
8. Bugs #27-31 - Medium severity improvements

---

## Verification
After fixes, verify with:
```bash
# Check imports work
python -c "from kosmos.config import KosmosSettings"

# Check static typing
mypy kosmos/ --ignore-missing-imports

# Run linting
ruff check kosmos/
```

---

*These bugs can be safely fixed without running tests as they involve clear, localized issues with well-defined solutions.*