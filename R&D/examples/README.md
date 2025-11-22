# Kosmos R&D Implementation Examples

This directory contains working demonstration code showing how to integrate patterns from the investigated projects into Kosmos to address critical architectural gaps.

## Overview

These examples solve the core gaps identified in `/R&D/KOSMOS_GAP_ANALYSIS_AND_INTEGRATION_PLAN.md`:

| Example | Solves Gap | Key Patterns | Estimated Effort |
|---------|------------|--------------|------------------|
| **01_context_compression** | Gap 0 (Foundational) | scientific-writer + claude-skills-mcp + karpathy | 2-3 weeks |
| **02_task_planning** | Gap 2 (Critical) | karpathy + scientific-skills + claude-skills-mcp | 3-4 weeks |
| **03_hybrid_state_manager** | Gap 1 (Critical) | All 4 projects | 2-3 weeks |

## Quick Start

Each example is self-contained and runnable independently:

```bash
# Example 1: Context Compression
cd 01_context_compression
python compression_demo.py

# Example 2: Task Planning
cd 02_task_planning
python task_planning_demo.py

# Example 3: Hybrid State Manager
cd 03_hybrid_state_manager
python hybrid_state_demo.py
```

## Example 1: Context Compression Pipeline

**Location**: `01_context_compression/`

**What it demonstrates**:
- Hierarchical compression (task → cycle → final)
- Notebook summarization (42K lines → 2-line summary)
- Literature compression (1500 papers → structured summaries)
- Progressive disclosure and lazy loading

**Patterns used**:
- **scientific-writer**: Document summarization, synthesis
- **claude-skills-mcp**: Progressive disclosure, lazy loading, multi-tier caching
- **karpathy**: Artifact-based communication

**Key insight**: By combining these patterns, Kosmos can compress 200+ agent rollouts (1,500 papers + 42,000 lines of code each) into a manageable context size while preserving critical information.

**Expected output**:
```
CONTEXT COMPRESSION PIPELINE DEMO
================================================================================

1. TASK-LEVEL COMPRESSION (Notebook → Summary)
--------------------------------------------------------------------------------
Original: 42000 characters
Compressed: 145 characters

Summary: BRCA1 gene shows significant upregulation in cancer cells.
Correlation between BRCA1 and TP53 expression is r = 0.85.

Statistics: {
  "p_values": [0.001],
  "correlations": [0.85],
  "fold_changes": [2.5]
}

2. LITERATURE COMPRESSION (Papers → Summaries)
...
```

## Example 2: Task Planning with Karpathy Pattern

**Location**: `02_task_planning/`

**What it demonstrates**:
- Plan Creator agent (generates 10 tasks)
- Plan Reviewer agent (validates quality)
- Exploration/exploitation balance
- Novelty detection via vector similarity
- Strategic prioritization

**Patterns used**:
- **karpathy**: Plan Creator, Plan Reviewer, delegation
- **scientific-skills**: Workflow templates
- **claude-skills-mcp**: Vector similarity for novelty

**Key insight**: Karpathy's planning pattern (create → review → execute) provides a proven architecture for autonomous task generation with quality checks.

**Expected output**:
```
TASK PLANNING PIPELINE DEMO (Karpathy Pattern)
================================================================================

CYCLE 1 TASK GENERATION
================================================================================
✓ Plan approved: Plan looks good!

Exploration ratio: 70.0%
Generated 10 prioritized tasks:

1. [DATA_ANALYSIS] Explore novel aspect 1 of cancer progression
   Priority: 0.85 (Novelty: 1.00, Gap: 0.30)

2. [HYPOTHESIS_GENERATION] Explore novel aspect 3 of cancer progression
   Priority: 0.82 (Novelty: 0.95, Gap: 0.80)
...
```

## Example 3: Hybrid State Manager

**Location**: `03_hybrid_state_manager/`

**What it demonstrates**:
- 4-layer storage architecture
- File artifacts (human-readable JSON)
- Graph database (relationship queries)
- Vector search (semantic similarity)
- Citation tracking (provenance)
- Query interface (find, read, list)

**Patterns used**:
- **karpathy**: Artifact-based persistence (`sandbox/cycle_N/`)
- **scientific-skills**: Neo4j knowledge graph
- **claude-skills-mcp**: Vector embeddings for semantic search
- **scientific-writer**: Citation graph for provenance

**Key insight**: A hybrid approach combining files + graph + vectors + citations provides the flexibility needed for both human debugging and sophisticated queries.

**Expected output**:
```
HYBRID STATE MANAGER DEMO
================================================================================
Architecture:
  Layer 1: File artifacts (karpathy)
  Layer 2: Graph database (scientific-skills)
  Layer 3: Vector search (claude-skills-mcp)
  Layer 4: Citation graph (scientific-writer)

ADDING FINDINGS TO STATE MANAGER
================================================================================

✓ Added finding finding_1_1 to all 4 storage layers
  - Artifact: sandbox_demo/cycle_1/task_1_findings.json
  - Graph: Indexed with relationships
  - Vector: Embedded for semantic search
  - Citations: 2 papers tracked
...
```

## Integration Roadmap

To integrate these examples into the main Kosmos codebase:

### Week 1-2: Foundation
1. Copy `hybrid_state_manager/` to `kosmos/world_model/hybrid_state.py`
2. Replace mock implementations with real ones:
   - SQLite → Neo4j driver
   - Mock embeddings → sentence-transformers
3. Add tests in `tests/unit/world_model/`

### Week 3-4: Compression
1. Copy `context_compression/` to `kosmos/compression/`
2. Integrate scientific-writer for summarization
3. Add lazy loading for notebooks
4. Add multi-tier caching

### Week 5-8: Task Planning
1. Copy `task_planning/` to `kosmos/task_generation/`
2. Create Plan Creator and Plan Reviewer agents
3. Integrate with State Manager
4. Add exploration/exploitation heuristics

### Week 9-16: End-to-End Testing
1. Test with real datasets
2. Reproduce Discovery 1 from paper
3. Tune compression ratios and priorities
4. Validate against paper metrics (>75% accuracy)

## Dependencies

These examples use minimal dependencies for demonstration. For production:

```bash
# Context compression
pip install anthropic  # For LLM summarization
# scientific-writer integration (when ready)

# Task planning
pip install sentence-transformers  # For novelty detection
pip install numpy

# Hybrid state manager
pip install neo4j  # Replace SQLite
pip install sentence-transformers  # For vector search
pip install pinecone-client  # Or weaviate-client
```

## Architecture Diagrams

See `/R&D/KOSMOS_GAP_ANALYSIS_AND_INTEGRATION_PLAN.md` Part 2 for detailed architecture diagrams showing how these components fit together.

## Performance Expectations

Based on the patterns demonstrated:

| Metric | Current (Paper) | With Integration | Improvement |
|--------|----------------|------------------|-------------|
| Context size | 100K+ tokens | 5K tokens | 20x reduction |
| Task redundancy | Unknown | <30% (novelty>0.7) | Measurable |
| State Manager queries | N/A | <1s (indexed) | Fast |
| Report generation | Manual | Automated | Quality maintained |

## Next Steps

1. **Review** the gap analysis document for full context
2. **Run** each example to understand the patterns
3. **Read** the inline comments for implementation details
4. **Integrate** one example at a time into Kosmos
5. **Test** with real data and iterate

## Questions?

For questions about these examples or integration approach:
1. Read the detailed analysis: `/R&D/KOSMOS_GAP_ANALYSIS_AND_INTEGRATION_PLAN.md`
2. Check the source projects:
   - `/R&D/kosmos-claude-skills-mcp/`
   - `/R&D/kosmos-claude-scientific-skills/`
   - `/R&D/kosmos-claude-scientific-writer/`
   - `/R&D/kosmos-karpathy/`
3. Review the main Kosmos code: `/R&D/kosmos/`

---

**Total Implementation Time**: 16 weeks (4 months)
**Team Size**: 2-3 engineers
**Success Criteria**: Reproduce Discovery 1 with >75% statement accuracy
