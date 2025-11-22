# End-to-End Research Workflow Demo

This example demonstrates the **complete Kosmos autonomous research system** integrating all Phase 1 + Phase 2 components.

## What This Demonstrates

### Components Integrated

1. **Plan Creator/Reviewer** (karpathy orchestration)
   - Strategic task planning with exploration/exploitation balance
   - 5-dimension quality validation

2. **Delegation Manager** (task execution)
   - Multi-agent coordination
   - Parallel task execution

3. **Novelty Detector** (redundancy prevention)
   - Vector-based similarity search
   - Prevents duplicate work

4. **Data Analyst + Skills** (domain expertise)
   - 120+ scientific skills
   - Domain-specific analysis

5. **ScholarEval** (quality validation)
   - 8-dimension peer review
   - Filters low-quality discoveries

6. **Context Compressor** (memory management)
   - 20x context reduction
   - Hierarchical compression

7. **Artifact State Manager** (persistent storage)
   - JSON artifacts
   - Cycle summaries

### Research Cycle

Each cycle:
1. Create 10-task research plan
2. Check novelty vs past work
3. Review plan quality (5 dimensions)
4. Execute approved tasks in parallel
5. Validate findings with ScholarEval
6. Store discoveries
7. Compress context for next cycle
8. Generate cycle summary

## Installation

### Prerequisites

```bash
# Install Kosmos with dependencies
cd ../../kosmos
poetry install

# Or with pip
pip install -e .

# Install optional dependencies for novelty detection
pip install sentence-transformers torch
```

### Verify Installation

```bash
# Run simple component test
python research_workflow_demo.py --test
```

Expected output:
```
================================================================================
SIMPLE COMPONENT TEST (Non-async)
================================================================================

Testing component imports...
  ✓ Orchestration components
  ✓ Research workflow
  ✓ ScholarEval validator
  ✓ Context compressor
  ✓ Artifact state manager
  ✓ Skill loader

All components imported successfully!

Testing Novelty Detector...
  ✓ Indexed 3 past tasks
  ✓ Novelty check: score=0.68, novel=false
    Similar to: Analyze gene expression in cancer samples...

Novelty detector working correctly!

Testing Skill Loader...
  ✓ Found 120 scientific skills
    Examples: scanpy, biopython, rdkit, statsmodels, matplotlib
  ✓ Supported task types: 12
    Examples: single_cell_analysis, genomics, drug_discovery

Component tests complete!
```

## Running the Demo

### Quick Run (5 cycles)

```bash
python research_workflow_demo.py
```

**Runtime**: ~15-20 minutes for 5 cycles

**Output**:
```
================================================================================
KOSMOS END-TO-END RESEARCH WORKFLOW DEMO
================================================================================

Starting 5-cycle research workflow...

================================================================================
CYCLE 1/5
================================================================================

[Cycle 1] Creating research plan...
[Cycle 1] Plan created with 10 tasks
[Cycle 1] Checking plan novelty...
[Cycle 1] Novelty check: 10/10 tasks are novel
[Cycle 1] Reviewing plan...
[Cycle 1] Plan review: APPROVED (score: 8.2/10)
[Cycle 1] Executing plan...
[Cycle 1] Execution complete: 9 succeeded, 1 failed
[Cycle 1] Validating finding cycle1_task1...
[Cycle 1] Finding cycle1_task1 validated (score: 0.82)
...

================================================================================
RESEARCH WORKFLOW COMPLETE
================================================================================

RESULTS:
  Total Cycles: 5
  Total Tasks: 47
  Total Findings: 32
  Validated Findings: 24
  Validation Rate: 75.0%

OUTPUT:
  Directory: ./demo_output
  Final Report: ./demo_output/final_research_report.md

CYCLE SUMMARY:
--------------------------------------------------------------------------------
Cycle    Status       Tasks    Findings   Validated    Score
--------------------------------------------------------------------------------
1        completed    9        7          5            8.2/10
2        completed    10       8          6            7.8/10
3        completed    9        6          5            8.1/10
4        completed    10       7          5            7.5/10
5        completed    9        4          3            7.9/10
--------------------------------------------------------------------------------

QUALITY METRICS:
  Average Plan Score: 7.9/10
  Discovery Validation Rate: 75.0%
  Task Success Rate: 68.1%
```

### Full Production Run (20 cycles)

For a full research run, modify the code:

```python
# In research_workflow_demo.py, change:
results = await workflow.run(num_cycles=20, tasks_per_cycle=10)
```

**Runtime**: ~10-15 hours for 20 cycles

## Output Structure

```
./demo_output/
├── workflow_config.json           # Configuration
├── artifacts/                     # Per-cycle artifacts
│   ├── cycle_1/
│   │   ├── task_1_finding.json   # Individual findings
│   │   ├── task_2_finding.json
│   │   └── summary.md            # Cycle summary
│   ├── cycle_2/
│   └── ...
├── checkpoint_cycle_1.json        # Checkpoints (for resuming)
├── checkpoint_cycle_2.json
├── ...
├── research_results.json          # Final results (JSON)
└── final_research_report.md       # Final report (Markdown)
```

## Examining Results

### Final Report

```bash
cat demo_output/final_research_report.md
```

Contains:
- Executive summary
- Key findings (top 10)
- Cycle-by-cycle summary
- Methodology

### Individual Findings

```bash
# View a specific finding
cat demo_output/artifacts/cycle_1/task_1_finding.json
```

```json
{
  "finding_id": "cycle1_task1",
  "cycle": 1,
  "task": 1,
  "summary": "Identified 245 differentially expressed genes in cancer samples with high significance (p < 0.001)",
  "statistics": {
    "p_value": 0.0001,
    "confidence": 0.95,
    "effect_size": 2.3,
    "sample_size": 150
  },
  "methods": "Differential expression analysis using DESeq2...",
  "interpretation": "These genes are enriched for metabolic pathways...",
  "scholar_eval": {
    "overall_score": 0.82,
    "passes_threshold": true,
    "novelty": 0.85,
    "rigor": 0.88,
    ...
  }
}
```

### Cycle Summary

```bash
cat demo_output/artifacts/cycle_1/summary.md
```

## Customization

### Change Research Objective

```python
workflow = ResearchWorkflow(
    research_objective="Your research question here",
    # ... other parameters
)
```

### Adjust Quality Thresholds

```python
workflow = ResearchWorkflow(
    min_plan_score=8.0,        # Stricter plan approval (default: 7.0)
    min_discovery_score=0.80,  # Higher quality bar (default: 0.75)
    # ...
)
```

### Increase Parallelism

```python
workflow = ResearchWorkflow(
    max_parallel_tasks=5,  # More concurrent tasks (default: 3)
    # ...
)
```

### Disable Optional Components

```python
workflow = ResearchWorkflow(
    enable_novelty_detection=False,  # Skip novelty checking
    enable_scholar_eval=False,       # Skip validation
    # ...
)
```

## Troubleshooting

### "sentence-transformers not installed"

**Solution**:
```bash
pip install sentence-transformers torch
```

**Workaround**: Novelty detector falls back to keyword matching

### "Out of memory"

**Solution**:
- Reduce `max_parallel_tasks` to 1 or 2
- Increase system memory
- Use smaller embedding model:

```python
from kosmos.orchestration import NoveltyDetector

detector = NoveltyDetector(model_name="all-MiniLM-L6-v2")  # Smaller, faster
```

### "LLM API errors"

**Solution**:
- Check `kosmos.core.llm` configuration
- Ensure API keys are set
- Check rate limits

### Tasks timing out

**Solution**:
```python
from kosmos.orchestration import DelegationManager

manager = DelegationManager(task_timeout_minutes=240)  # 4 hours
```

## Performance Expectations

### Demo (5 cycles)
- **Runtime**: 15-20 minutes
- **Tasks**: 40-50
- **Findings**: 25-35
- **Validated**: 18-26 (75% rate)

### Production (20 cycles)
- **Runtime**: 10-15 hours
- **Tasks**: 180-200
- **Findings**: 120-160
- **Validated**: 90-120 (75% rate)

### Resource Usage
- **CPU**: 4-8 cores recommended
- **Memory**: 8-16GB RAM
- **Disk**: ~500MB for outputs
- **Network**: LLM API calls (~500K tokens total)

## What's Next

After running this demo:

1. **Review outputs**: Examine findings and cycle summaries
2. **Adjust parameters**: Tune quality thresholds and parallelism
3. **Run production**: Increase to 20 cycles for full research
4. **Integration**: Integrate with your own data sources
5. **Customization**: Add domain-specific skills and agents

## Related Examples

- `01_context_compression/` - Context compression demo
- `02_task_planning/` - Task planning only
- `03_hybrid_state_manager/` - State management only

## Support

For issues or questions:
- Check `INTEGRATION_PHASE2_COMPLETE.md` for detailed documentation
- Review `KOSMOS_GAP_ANALYSIS_AND_INTEGRATION_PLAN.md` for architecture
- File issues at: https://github.com/jimmc414/kosmos-research/issues
