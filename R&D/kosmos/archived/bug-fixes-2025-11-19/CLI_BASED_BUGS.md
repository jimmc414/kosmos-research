# CLI-Based Claude Code Bugs - Kosmos AI Scientist v0.2.0

**Total Bugs: 29**
**Type: Bugs requiring test execution to validate fixes**
**Date: 2025-11-19**

These bugs require running tests because they involve:
- Runtime behavior verification
- API response handling
- Platform-specific issues
- Database/initialization sequences
- Integration between components
- Dynamic type handling

---

## CRITICAL SEVERITY (7 bugs)
*Runtime failures requiring test validation*

### 1. Database Operation Missing Required Arguments
- **File:** `kosmos/execution/result_collector.py`
- **Lines:** 441-448
- **Error:** `TypeError: create_result() missing 2 required positional arguments: 'session' and 'id'`
- **Testing Required:** Database integration tests
- **Verification Commands:**
```bash
pytest tests/integration/test_result_collector.py -v
pytest tests/integration/test_database_operations.py -v
```
- **Risk:** Database session management may have cascading effects

### 2. World Model `create_author()` - Extra Parameters
- **File:** `kosmos/world_model/simple.py`
- **Lines:** 193-199
- **Issue:** Extra `email` and `metadata` parameters
- **Testing Required:** World model integration tests
- **Verification Commands:**
```bash
pytest tests/integration/test_world_model.py::test_create_author -v
pytest tests/unit/world_model/test_simple.py -v
```
- **Risk:** Parameter removal may affect downstream calls

### 3. World Model `create_method()` - Extra Parameter
- **File:** `kosmos/world_model/simple.py`
- **Lines:** 216-222
- **Issue:** Extra parameter not in interface
- **Testing Required:** Method creation flow tests
- **Verification Commands:**
```bash
pytest tests/integration/test_world_model.py::test_create_method -v
```
- **Risk:** May have dependent code expecting parameter

### 4. World Model `create_citation()` - Wrong Parameter Name
- **File:** `kosmos/world_model/simple.py`
- **Lines:** 446-451
- **Issue:** Parameter name mismatch with interface
- **Testing Required:** Citation creation tests
- **Verification Commands:**
```bash
pytest tests/integration/test_world_model.py::test_citations -v
```
- **Risk:** External callers may use wrong parameter name

### 5. Broken Test Import - ParallelExecutionResult
- **File:** `tests/integration/test_parallel_execution.py`
- **Error:** `ImportError: cannot import name 'ExperimentResult' from 'kosmos.execution.parallel'`
- **Testing Required:** Must run to find correct import
- **Verification Commands:**
```bash
python -c "from kosmos.execution.parallel import *; print(dir())"
pytest tests/integration/test_parallel_execution.py -v
```
- **Risk:** May need multiple import updates

### 6. Broken Test Import - EmbeddingGenerator
- **File:** `tests/integration/test_phase2_e2e.py`
- **Error:** `ImportError: cannot import name 'EmbeddingGenerator' from 'kosmos.knowledge.embeddings'`
- **Testing Required:** Must identify correct class name
- **Verification Commands:**
```bash
python -c "from kosmos.knowledge.embeddings import *; print(dir())"
pytest tests/integration/test_phase2_e2e.py -v
```
- **Risk:** Class may have been renamed or moved

### 7. Reset Functions May Not Exist (Test Contamination)
- **File:** `tests/conftest.py`
- **Lines:** 306-321
- **Issue:** ImportError masked by try/except causing test contamination
- **Testing Required:** Full test suite isolation verification
- **Verification Commands:**
```bash
# Run tests in different orders to detect contamination
pytest tests/ -v --random-order
pytest tests/ -v --reverse
pytest tests/unit tests/integration -v
pytest tests/integration tests/unit -v
```
- **Risk:** Tests may pass individually but fail together

---

## HIGH SEVERITY (13 bugs)
*API and runtime issues requiring execution verification*

### 8-12. Unvalidated LLM Response Array Access (5 locations)
- **Files & Lines:**
  - `kosmos/core/llm.py:321`
  - `kosmos/core/llm.py:392`
  - `kosmos/core/providers/anthropic.py:240`
  - `kosmos/core/providers/anthropic.py:360`
  - `kosmos/core/providers/openai.py:186,297`
- **Error:** `IndexError: list index out of range`
- **Testing Required:** Mock API responses with various structures
- **Verification Commands:**
```bash
pytest tests/unit/core/test_llm.py -v
pytest tests/unit/core/providers/ -v
pytest tests/integration/test_llm_providers.py -v
```
- **Fix Pattern:**
```python
if response.choices and len(response.choices) > 0:
    content = response.choices[0].message.content
else:
    raise LLMError("Empty response from API")
```
- **Risk:** API response structure varies by provider

### 13. NoneType Embeddings Model Access
- **File:** `kosmos/knowledge/embeddings.py`
- **Lines:** 112-116
- **Error:** `AttributeError: 'NoneType' object has no attribute 'encode'`
- **Testing Required:** Initialization sequence tests
- **Verification Commands:**
```bash
pytest tests/unit/knowledge/test_embeddings.py -v
pytest tests/integration/test_embeddings_init.py -v
```
- **Risk:** May depend on environment variables or external services

### 14. NoneType Vector DB Collection Access
- **File:** `kosmos/knowledge/vector_db.py`
- **Lines:** 170-175, 216-220, 340
- **Error:** `AttributeError: 'NoneType' object has no attribute 'add'`
- **Testing Required:** Vector DB initialization tests
- **Verification Commands:**
```bash
pytest tests/unit/knowledge/test_vector_db.py -v
pytest tests/integration/test_vector_db_ops.py -v
```
- **Risk:** Database connection timing issues

### 15. Windows Path Handling in Docker
- **File:** `kosmos/execution/sandbox.py`
- **Lines:** 226-233
- **Issue:** Docker volume path corruption on Windows
- **Testing Required:** Platform-specific testing on WSL2
- **Verification Commands:**
```bash
# On Windows WSL2
pytest tests/integration/test_sandbox.py::test_windows_paths -v
python -c "from kosmos.execution.sandbox import DockerSandbox; DockerSandbox().validate_paths()"
```
- **Risk:** Platform-specific behavior

### 16. PubMed API Response Validation Missing
- **File:** `kosmos/literature/pubmed_client.py`
- **Line:** 146
- **Error:** `KeyError: 'IdList'`
- **Testing Required:** API response mocking
- **Verification Commands:**
```bash
pytest tests/unit/literature/test_pubmed_client.py -v
pytest tests/integration/test_pubmed_api.py -v --mock-api
```
- **Risk:** External API structure changes

### 17. PubMed API IndexError
- **File:** `kosmos/literature/pubmed_client.py`
- **Line:** 253
- **Error:** `IndexError` on empty results
- **Testing Required:** Empty response handling
- **Verification Commands:**
```bash
pytest tests/unit/literature/test_pubmed_client.py::test_empty_response -v
```

### 18. Semantic Scholar Type Mismatch
- **File:** `kosmos/literature/semantic_scholar.py`
- **Line:** 357
- **Error:** `AttributeError: 'str' object has no attribute 'get'`
- **Testing Required:** Response type validation
- **Verification Commands:**
```bash
pytest tests/unit/literature/test_semantic_scholar.py -v
pytest tests/integration/test_semantic_scholar_api.py -v
```
- **Risk:** API returns different types based on query

### 19. Database Not Initialized
- **File:** `kosmos/cli/main.py`
- **Lines:** 242-245
- **Error:** `RuntimeError: Database not initialized`
- **Testing Required:** Application startup sequence
- **Verification Commands:**
```bash
python -m kosmos.cli.main --help
pytest tests/integration/test_cli_startup.py -v
```
- **Risk:** Initialization order dependencies

### 20. Unvalidated Research Plan Access
- **File:** `kosmos/cli/commands/run.py`
- **Lines:** 296-302
- **Error:** `AttributeError: 'NoneType' object has no attribute 'hypothesis_pool'`
- **Testing Required:** Various input scenarios
- **Verification Commands:**
```bash
pytest tests/integration/test_run_command.py -v
python -m kosmos.cli.commands.run --dry-run
```
- **Risk:** Multiple code paths can lead to None

### 21. Uninitialized Vector DB in Graph Builder
- **File:** `kosmos/knowledge/graph_builder.py`
- **Lines:** 68-71, 375
- **Error:** `AttributeError: 'GraphBuilder' object has no attribute 'vector_db'`
- **Testing Required:** Object lifecycle testing
- **Verification Commands:**
```bash
pytest tests/unit/knowledge/test_graph_builder.py -v
pytest tests/integration/test_graph_builder_init.py -v
```
- **Risk:** Initialization timing issues

---

## TEST FIXTURE BUGS (7 bugs)
*Model structure verification required*

### 22. Hypothesis Model Field: variables list
- **File:** `tests/integration/test_analysis_pipeline.py`
- **Issue:** Non-existent field `variables`
- **Testing Required:** Run test to find correct field
- **Verification Commands:**
```bash
pytest tests/integration/test_analysis_pipeline.py::test_hypothesis -v --tb=short
python -c "from kosmos.models import Hypothesis; print(Hypothesis.__fields__)"
```

### 23. VariableResult Model: q1/q3 fields
- **File:** `tests/unit/agents/test_data_analyst.py`
- **Issue:** Fields `q1` and `q3` don't exist
- **Testing Required:** Discover actual field names
- **Verification Commands:**
```bash
pytest tests/unit/agents/test_data_analyst.py -v --tb=short
python -c "from kosmos.models import VariableResult; print(VariableResult.__fields__)"
```

### 24. ExperimentProtocol Model: title field
- **File:** `tests/integration/test_analysis_pipeline.py`
- **Issue:** Field doesn't exist at top level
- **Testing Required:** Find correct structure
- **Verification Commands:**
```bash
python -c "from kosmos.models import ExperimentProtocol; print(ExperimentProtocol.__fields__)"
```

### 25. ExperimentProtocol Model: data_requirements
- **File:** `tests/integration/test_analysis_pipeline.py`
- **Issue:** Non-existent field
- **Testing Required:** Find correct field name
- **Verification:** Same as #24

### 26. ExperimentProtocol Model: expected_duration_minutes
- **File:** `tests/integration/test_analysis_pipeline.py`
- **Issue:** Field not at top level
- **Testing Required:** Find nested structure
- **Verification:** Same as #24

### 27. ResourceRequirements Model: cpu_cores
- **File:** `tests/integration/test_analysis_pipeline.py`
- **Issue:** Non-existent field
- **Testing Required:** Find actual fields
- **Verification Commands:**
```bash
python -c "from kosmos.models import ResourceRequirements; print(ResourceRequirements.__fields__)"
```

### 28. Hypothesis Model Field: experiment_type Enum Value
- **File:** `tests/integration/test_analysis_pipeline.py`
- **Issue:** Invalid enum value
- **Testing Required:** Validate enum values
- **Verification Commands:**
```bash
python -c "from kosmos.models import ExperimentType; print(list(ExperimentType))"
```

---

## MEDIUM SEVERITY (5 bugs)
*Runtime behavior requiring execution tests*

### 29. asyncio.run() in Async Context
- **File:** `kosmos/agents/research_director.py`
- **Lines:** 1292-1294, 1348-1350
- **Error:** `RuntimeError: asyncio.run() cannot be called from a running event loop`
- **Testing Required:** Async context testing
- **Verification Commands:**
```bash
pytest tests/unit/agents/test_research_director.py -v
pytest tests/integration/test_async_execution.py -v
```
- **Fix Pattern:**
```python
if asyncio.get_event_loop().is_running():
    await coroutine()
else:
    asyncio.run(coroutine())
```

### 30. Overly Broad Exception Handling
- **File:** `kosmos/execution/sandbox.py`
- **Lines:** 286-296
- **Issue:** All exceptions classified as timeouts
- **Testing Required:** Various failure mode tests
- **Verification Commands:**
```bash
pytest tests/unit/execution/test_sandbox_errors.py -v
pytest tests/integration/test_sandbox_failure_modes.py -v
```
- **Risk:** Masks actual errors

### 31. Non-Numeric Data Type Mismatch
- **File:** `kosmos/execution/result_collector.py`
- **Lines:** 280-288
- **Issue:** Type operations on non-numeric data
- **Testing Required:** Various data type inputs
- **Verification Commands:**
```bash
pytest tests/unit/execution/test_result_collector.py::test_numeric_operations -v
pytest tests/integration/test_result_types.py -v
```

### 32. Missing Test Markers
- **File:** `pytest.ini`
- **Issue:** Various test markers not defined
- **Testing Required:** Run test suite to find all markers
- **Verification Commands:**
```bash
pytest --markers
pytest tests/ --collect-only | grep -E "@pytest.mark"
```

### 33. Type Coercion Issues
- **Files:** Multiple locations
- **Issue:** Implicit type conversions failing
- **Testing Required:** Type boundary testing
- **Verification Commands:**
```bash
mypy kosmos/ --strict
pytest tests/unit/test_type_safety.py -v
```

---

## Test Execution Strategy

### Phase 1: Environment Setup
```bash
# Install all dependencies including test requirements
poetry install --with dev,test

# Verify basic imports work
python -c "import kosmos; print(kosmos.__version__)"
```

### Phase 2: Unit Tests First
```bash
# Run unit tests to catch basic issues
pytest tests/unit/ -v --tb=short

# Run with coverage to identify untested code
pytest tests/unit/ --cov=kosmos --cov-report=html
```

### Phase 3: Integration Tests
```bash
# Run integration tests
pytest tests/integration/ -v --tb=short

# Run specific problem areas
pytest tests/integration/test_world_model.py -v
pytest tests/integration/test_database_operations.py -v
```

### Phase 4: Platform-Specific Tests
```bash
# On Windows WSL2
pytest tests/integration/test_sandbox.py -v -k windows

# Docker-specific tests
pytest tests/integration/test_docker_sandbox.py -v
```

### Phase 5: Full Test Suite
```bash
# Run everything
pytest tests/ -v

# Check for test isolation issues
pytest tests/ --random-order
```

---

## Risk Matrix

| Bug Category | Risk Level | Test Coverage Needed |
|--------------|-----------|---------------------|
| Database Operations | HIGH | Integration + Transaction tests |
| API Response Handling | HIGH | Mock + Real API tests |
| Platform-Specific | HIGH | Multi-platform testing |
| Async/Await | MEDIUM | Event loop tests |
| Type Safety | MEDIUM | Static + Runtime checks |
| Test Fixtures | LOW | Direct model validation |

---

## Success Metrics

1. **Test Pass Rate:** Target >90% (from 57.4% baseline)
2. **Code Coverage:** Target >70% (from 22.77% baseline)
3. **No Regressions:** All previously passing tests still pass
4. **Error Handling:** Proper exceptions, not crashes
5. **Platform Support:** Works on Linux, macOS, Windows WSL2

---

*These bugs require careful testing to ensure fixes don't introduce regressions or new issues.*