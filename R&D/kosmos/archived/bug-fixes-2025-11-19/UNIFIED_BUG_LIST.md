# Unified Bug List - Kosmos AI Scientist v0.2.0

**Total Bugs Identified: 60+ execution-blocking issues**
**Test Pass Rate Baseline: 57.4% (81/141 integration tests passing)**
**Code Coverage Baseline: 22.77%**
**Date Compiled: 2025-11-18**
**Sources: CODE_REVIEW_BUGS.md, code_review_cc_sonnet.md, code_review_cc_opus.md, code_review_gemini3.md, code_review_gemini_deep_research.md**

---

## CRITICAL SEVERITY (Immediate Crash/Startup Failures)
*These bugs prevent the application from starting or cause immediate crashes*

### 1. [SHOWSTOPPER] Pydantic V2 Configuration Parsing Failure
**Source:** gemini_deep_research.md
**File:** `kosmos/config.py` (BaseSettings implementation)
**Error:** `SettingsError: error parsing value for field "enabled_domains" from source "EnvSettingsSource"`
**Impact:** Application cannot start AT ALL - affects every entry point
**Root Cause:** Pydantic V2 requires JSON format `["chemistry","physics"]` but .env uses `chemistry,physics`
**Fix Required:** Implement BeforeValidator for comma-separated string parsing

### 2. Missing `psutil` Dependency
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/api/health.py:12`
**Error:** `ModuleNotFoundError: No module named 'psutil'`
**Fix:** Add `psutil` to pyproject.toml dependencies

### 3. Missing `redis` Dependency
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/api/health.py:230`
**Error:** `ModuleNotFoundError: No module named 'redis'`
**Fix:** Add `redis` to pyproject.toml dependencies

### 4. Database Operation Missing Required Arguments
**Source:** code_review_cc_sonnet.md
**File:** `kosmos/execution/result_collector.py:441-448`
**Error:** `TypeError: create_result() missing 2 required positional arguments: 'session' and 'id'`
**Fix:** Add session and id parameters to db_ops.create_result() call

### 5. Workflow State String Case Mismatch
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/cli/commands/run.py:248-259`
**Issue:** Comparing UPPERCASE strings against lowercase enum values
**Impact:** Progress bars never update, status displays incorrectly

### 6-10. World Model Method Signature Mismatches (5 instances)
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/world_model/simple.py`
- Line 144-155: `create_paper()` - wrong parameter format
- Line 171-176: `create_concept()` - extra `metadata` parameter
- Line 193-199: `create_author()` - extra `email` and `metadata` parameters
- Line 216-222: `create_method()` - extra parameter
- Line 446-451: `create_citation()` - wrong parameter name

### 11. Provider Type Mismatch in Fallback
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/core/llm.py:651-652`
**Error:** `TypeError: Expected LLMProvider, got <class 'ClaudeClient'>`

### 12. Pydantic Validator Accessing Raw Dicts
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/models/result.py:209-217`
**Error:** `AttributeError: 'dict' object has no attribute 'test_name'`

### 13-14. Missing Biology API Methods
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/domains/biology/genomics.py`
- Line 231: `get_pqtl()` method doesn't exist
- Line 237: `get_atac_peaks()` method doesn't exist

### 15. Non-existent scipy Function Import
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/domains/neuroscience/neurodegeneration.py:485`
**Error:** `ImportError: cannot import name 'false_discovery_control'`

### 16. Missing StatisticalTestResult.is_primary Field
**Source:** code_review_cc_sonnet.md
**File:** `kosmos/analysis/summarizer.py:189`
**Error:** `AttributeError: 'StatisticalTestResult' object has no attribute 'is_primary'`

### 17. Missing ExperimentResult CI Fields
**Source:** code_review_cc_sonnet.md
**File:** `kosmos/analysis/summarizer.py:280`
**Error:** `AttributeError: 'ExperimentResult' object has no attribute 'primary_ci_lower'`

### 18. Enum.lower() Method Call
**Source:** code_review_cc_sonnet.md
**File:** `kosmos/execution/code_generator.py:65,139,154`
**Error:** `AttributeError: 'StatisticalTest' object has no attribute 'lower'`

### 19. Broken Test Import - ParallelExecutionResult
**Source:** code_review_gemini3.md
**File:** `tests/integration/test_parallel_execution.py`
**Error:** `ImportError: cannot import name 'ExperimentResult' from 'kosmos.execution.parallel'`

### 20. Broken Test Import - PaperEmbedder
**Source:** code_review_gemini3.md
**File:** `tests/integration/test_phase2_e2e.py`
**Error:** `ImportError: cannot import name 'EmbeddingGenerator' from 'kosmos.knowledge.embeddings'`

---

## HIGH SEVERITY (Common Path Failures)
*These bugs fail on common operations and standard workflows*

### 21. Missing pytest e2e Marker
**Source:** code_review_gemini3.md
**File:** `pytest.ini`
**Error:** `pytest: error: 'e2e' not found in markers configuration`

### 22-26. Unvalidated LLM Response Array Access (5 locations)
**Source:** CODE_REVIEW_BUGS.md
**Files:**
- `kosmos/core/llm.py:321,392`
- `kosmos/core/providers/anthropic.py:240,360`
- `kosmos/core/providers/openai.py:186,297`
**Error:** `IndexError: list index out of range`

### 27. NoneType Embeddings Model Access
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/knowledge/embeddings.py:112-116`
**Error:** `AttributeError: 'NoneType' object has no attribute 'encode'`

### 28. NoneType Vector DB Collection Access
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/knowledge/vector_db.py:170-175,216-220,340`
**Error:** `AttributeError: 'NoneType' object has no attribute 'add'`

### 29. Windows Path Handling in Docker
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/execution/sandbox.py:226-233`
**Error:** Docker volume path corruption on Windows

### 30. Missing Result Exclusion Keys
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/execution/result_collector.py:365`
**Issue:** Duplicate keys in StatisticalTestResult

### 31-32. PubMed API Response Validation Missing
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/literature/pubmed_client.py:146,253`
**Errors:** `KeyError: 'IdList'` and `IndexError`

### 33. Semantic Scholar Type Mismatch
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/literature/semantic_scholar.py:357`
**Error:** `AttributeError: 'str' object has no attribute 'get'`

### 34. Database Not Initialized
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/cli/main.py:242-245`
**Error:** `RuntimeError: Database not initialized`

### 35. Cache Type Enum Mismatch
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/cli/commands/cache.py:264`
**Error:** `KeyError: 'GENERAL'`

### 36. Unvalidated Research Plan Access
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/cli/commands/run.py:296-302`
**Error:** `AttributeError: 'NoneType' object has no attribute 'hypothesis_pool'`

### 37. Reset Functions May Not Exist
**Source:** code_review_cc_opus.md
**File:** `tests/conftest.py:306-321`
**Issue:** ImportError masked by try/except, causes test contamination

### 38. Uninitialized Vector DB in Graph Builder
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/knowledge/graph_builder.py:68-71,375`
**Error:** `AttributeError: 'GraphBuilder' object has no attribute 'vector_db'`

---

## TEST FIXTURE BUGS (Integration & Unit Tests)
*These prevent tests from running but don't affect production code directly*

### 39-48. Test Fixture Field Mismatches
**Source:** code_review_cc_sonnet.md, code_review_cc_opus.md
**Files:** `tests/integration/test_analysis_pipeline.py`, `tests/unit/agents/test_data_analyst.py`

- **Hypothesis model:**
  - Uses `research_question_id` instead of `research_question`
  - Uses `experiment_type` as string (doesn't exist)
  - Uses `feasibility_score` (doesn't exist)
  - Uses `variables` list (doesn't exist)

- **ExperimentResult model:**
  - Uses `primary_ci_lower/primary_ci_upper` (don't exist)
  - Uses `plots_generated` instead of `generated_files`

- **VariableResult model:**
  - Uses `q1/q3` fields (don't exist)

- **ResourceRequirements model:**
  - Uses `estimated_runtime_seconds` (should be `compute_hours`)
  - Uses `cpu_cores` (doesn't exist)
  - Uses `storage_gb` (should be `data_size_gb`)

- **ExperimentProtocol model:**
  - Uses `title` field (doesn't exist at top level)
  - Uses `data_requirements` (doesn't exist)
  - Uses `expected_duration_minutes` (doesn't exist at top level)

### 49. StatisticalTestSpec String vs Enum
**Source:** code_review_cc_opus.md
**File:** `tests/integration/test_execution_pipeline.py:36`
**Issue:** Using `"t_test"` string instead of `StatisticalTest.T_TEST` enum

---

## MEDIUM SEVERITY (Degraded Functionality)

### 50. False Positives in Code Validator
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/safety/code_validator.py:245-251,267-275`
**Issue:** String matching instead of AST parsing

### 51. Falsy Value Bug in Resource Limits
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/safety/guardrails.py:156-170`
**Issue:** Resource limits bypassed when set to 0

### 52. PerovskiteDB Type Safety
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/domains/materials/apis.py:682-685`
**Issue:** Pandas Series vs dict method mismatch

### 53. asyncio.run() in Async Context
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/agents/research_director.py:1292-1294,1348-1350`
**Error:** `RuntimeError: asyncio.run() cannot be called from a running event loop`

### 54. Overly Broad Exception Handling
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/execution/sandbox.py:286-296`
**Issue:** All exceptions misclassified as timeouts

### 55. Interactive Mode Type Inconsistency
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/cli/interactive.py:236`

### 56. Missing max_iterations Validation
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/cli/interactive.py:217-221`

### 57. Non-Numeric Data Type Mismatch
**Source:** CODE_REVIEW_BUGS.md
**File:** `kosmos/execution/result_collector.py:280-288`

### 58. Hardcoded Relative Paths (5 instances)
**Source:** CODE_REVIEW_BUGS.md
**Issue:** Data scattered unpredictably

### 59. Deprecated datetime.utcnow()
**Source:** CODE_REVIEW_BUGS.md
**Multiple files using deprecated Python 3.12+ function

### 60. Missing Dependency Lock File
**Source:** code_review_gemini_deep_research.md
**Issue:** No poetry.lock or requirements.lock - dependency drift risk

---

## Bug Division Strategy for AI Agent Comparison

### Agent A (30 bugs):
**Critical (8):** #1,2,5,6,7,11,12,15
**High (12):** #21,22,23,27,28,29,30,31,34,35,36,38
**Test Fixtures (5):** #39,40,41,42,43
**Medium (5):** #50,51,53,54,58

### Agent B (30 bugs):
**Critical (11):** #3,4,8,9,10,13,14,16,17,18,19,20
**High (10):** #24,25,26,32,33,37
**Test Fixtures (5):** #44,45,46,47,48,49
**Medium (5):** #52,55,56,57,59,60

---

## Metrics for Comparison

### Success Criteria:
1. **Bug Fix Count:** Total number of bugs successfully resolved
2. **Test Pass Rate:** Improvement from 57.4% baseline
3. **Code Coverage:** Improvement from 22.77% baseline
4. **Fix Quality:** No regressions, proper error handling
5. **Time Efficiency:** Time taken per bug category

### Verification Commands:
```bash
# Run integration tests
pytest tests/integration/ -v --tb=short

# Run unit tests
pytest tests/unit/ -v

# Check coverage
pytest tests/ --cov=kosmos --cov-report=html

# Verify specific fixes
python -c "from kosmos.config import KosmosSettings"
python -c "from tests.integration.test_analysis_pipeline import *"
```

---

## Implementation Notes

1. **Start with Bug #1** - The Pydantic V2 configuration bug prevents ANY startup
2. **Dependencies first** - Add missing packages to pyproject.toml before other fixes
3. **Test fixtures** - Can be batch-fixed by updating model field names
4. **Use AST parsing** for code validation instead of string matching
5. **Add null checks** before accessing optional attributes
6. **Platform testing** - Verify Windows path fixes on WSL2

---

*Compiled from 5 independent code reviews totaling 100+ hours of analysis*