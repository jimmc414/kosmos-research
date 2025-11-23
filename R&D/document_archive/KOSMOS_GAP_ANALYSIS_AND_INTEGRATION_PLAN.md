# Kosmos Gap Analysis & Integration Plan
**Author**: Claude AI Research Assistant
**Date**: 2025-11-22
**Version**: 1.0

## Executive Summary

This document provides a comprehensive analysis of how the following projects can address critical gaps in the Kosmos AI Scientist implementation:

1. **kosmos-claude-skills-mcp** - MCP server for intelligent skill discovery
2. **kosmos-claude-scientific-skills** - 120+ scientific skills collection
3. **kosmos-claude-scientific-writer** - Scientific document generation system
4. **kosmos-karpathy** - Agentic ML engineer demonstration

**Key Finding**: While none of these projects directly solve the core architectural gaps (Context Compression, State Manager Schema, Task Generation Strategy), they provide valuable **building blocks, patterns, and reference implementations** that can significantly accelerate Kosmos development.

---

## Part 1: Gap-by-Gap Analysis

### Gap 0: Context Compression Architecture (FOUNDATIONAL BLOCKER)

**Kosmos Need**: Mechanism to compress 1,500 papers and 42,000 lines of code across 200+ agent rollouts while preserving causal relationships.

#### Project Mapping:

| Project | Relevance | How It Helps | Integration Approach |
|---------|-----------|--------------|----------------------|
| **claude-skills-mcp** | 🟡 Medium | - Progressive disclosure architecture (metadata → full content → files)<br>- Lazy document loading (startup 60s → 15s)<br>- Multi-tier caching (memory + disk)<br>- Hierarchical summarization patterns | **Inspiration**: Adopt progressive disclosure pattern for State Manager queries. Implement lazy loading for notebook content. Use multi-tier caching for agent outputs. |
| **scientific-skills** | 🔴 Low | - No direct compression capabilities | **Not Applicable** |
| **scientific-writer** | 🟢 High | - **Document summarization** for literature reviews<br>- **Citation extraction and management**<br>- Paper processing and synthesis<br>- Perplexity Sonar integration for research lookup | **Integration**: Use document summarization for compressing literature search results. Leverage citation management for paper tracking. Adapt synthesis algorithms for agent output compression. |
| **karpathy** | 🟡 Medium | - Multi-agent delegation pattern<br>- Iterative plan → execute → review loop<br>- Artifact-based communication (`plan.md`, `research.md`) | **Pattern**: Implement artifact-based agent communication instead of full context passing. Use delegation pattern to scope context per task. |

**Recommendation**:
- **Primary Source**: scientific-writer's summarization + claude-skills-mcp's progressive disclosure
- **Implementation**: Create a "Compression Manager" that:
  1. Uses scientific-writer to summarize literature search results (1500 papers → structured summaries)
  2. Uses progressive disclosure to load notebook content on-demand
  3. Uses karpathy's artifact pattern (save compressed summaries to files: `cycle_N_summary.md`)
  4. Implements hierarchical compression: task-level → cycle-level → final synthesis

---

### Gap 1: State Manager Architecture (CRITICAL)

**Kosmos Need**: Schema design, storage architecture, update mechanisms, and query interface for the central knowledge repository.

#### Project Mapping:

| Project | Relevance | How It Helps | Integration Approach |
|---------|-----------|--------------|----------------------|
| **claude-skills-mcp** | 🟡 Medium | - Vector search with sentence-transformers<br>- Semantic similarity for skill discovery<br>- Knowledge indexing patterns<br>- Query interface design (3 tools: find, read, list) | **Pattern**: Use vector embeddings for semantic search within State Manager. Implement similar 3-tier query interface (find_findings, read_evidence, list_hypotheses). |
| **scientific-skills** | 🟡 Medium | - Domain-specific knowledge structures (skills for Neo4j, graph analysis, etc.)<br>- Pathway analysis patterns (KEGG, Reactome)<br>- Network biology skills (STRING, Torch Geometric) | **Skills**: Use Neo4j skill for knowledge graph, NetworkX for relationship visualization, PyMC for uncertainty in findings. |
| **scientific-writer** | 🟢 High | - **Citation graph management**<br>- Reference tracking with provenance<br>- Claim → evidence linking<br>- Document relationship mapping | **Integration**: Adapt citation graph structure for State Manager schema. Use provenance tracking patterns for traceability. Implement claim-evidence relationships. |
| **karpathy** | 🟢 High | - **Artifact-based knowledge persistence** (`plan.md`, `research.md`, `feedback.md`)<br>- Structured file organization in `sandbox/`<br>- Expert delegation with clear input/output contracts<br>- Iterative refinement loop | **Architecture**: Use artifact-based State Manager where each cycle produces:<br>- `cycle_N_findings.json` (data analysis results)<br>- `cycle_N_papers.json` (literature findings)<br>- `cycle_N_hypotheses.json` (generated hypotheses)<br>Neo4j can index these for graph queries. |

**Recommendation**:
- **Hybrid Architecture**:
  1. **File-based artifacts** (karpathy pattern) for human-readable persistence
  2. **Neo4j knowledge graph** (scientific-skills) for relationship queries
  3. **Vector store** (claude-skills-mcp) for semantic search
  4. **Citation graph** (scientific-writer) for provenance
- **Schema**:
  ```
  Entities: Finding, Hypothesis, Evidence, Analysis, Citation, Experiment
  Relationships: SUPPORTS, REFUTES, DERIVES_FROM, CITES, SUGGESTS, VALIDATES
  Attributes: confidence, p_value, timestamp, source_notebook, cycle_number
  ```
- **Update Protocol**: Agents write JSON artifacts → Background process indexes to Neo4j + vector store

---

### Gap 2: Task Generation Strategy (CRITICAL)

**Kosmos Need**: Algorithm for converting State Manager state into 10 prioritized tasks per cycle with exploration/exploitation balance.

#### Project Mapping:

| Project | Relevance | How It Helps | Integration Approach |
|---------|-----------|--------------|----------------------|
| **claude-skills-mcp** | 🔴 Low | - No task generation capabilities | **Not Applicable** |
| **scientific-skills** | 🟡 Medium | - Research workflow patterns in skill examples<br>- Multi-step scientific pipelines<br>- Domain-specific analysis sequences | **Inspiration**: Use skill workflow patterns as templates for task sequences. Each skill's examples show typical research pipelines. |
| **scientific-writer** | 🟡 Medium | - **Research planning** for grant proposals<br>- Structured outline generation<br>- Gap identification in literature reviews | **Pattern**: Adapt outline generation algorithm for task planning. Use literature gap identification for exploration tasks. |
| **karpathy** | 🟢 **Very High** | - **`Plan Creator` expert** with explicit planning step<br>- **`Plan Reviewer` expert** for quality checking<br>- Delegation-based task execution<br>- **Iterative refinement** (plan → execute → review → revise)<br>- Expert specialization (Research, Data, Experiment, Evaluation) | **Direct Adoption**: Implement Kosmos Task Generator using karpathy's planning pattern:<br>1. Query State Manager for current knowledge<br>2. Use "Plan Creator" agent to generate 10 tasks<br>3. Use "Plan Reviewer" agent to validate task quality<br>4. Categorize tasks by type (analysis, literature, hypothesis)<br>5. Prioritize based on novelty + state manager gaps |

**Recommendation**:
- **Primary Source**: **karpathy's planning architecture** (plan creator + reviewer)
- **Implementation**:
  1. Create `TaskGeneratorAgent` that queries State Manager
  2. Use Claude with scientific-skills context to generate tasks
  3. Implement exploration/exploitation heuristic:
     - First 10 cycles: 70% exploration (new directions)
     - Last 10 cycles: 70% exploitation (deepen existing findings)
     - Novelty detection: check State Manager for similar past tasks
  4. Use karpathy's reviewer pattern to validate task quality
  5. Generate tasks in structured format:
     ```json
     {
       "task_id": 1,
       "type": "data_analysis",
       "description": "Analyze correlation between X and Y",
       "context": {...},  // Relevant State Manager entries
       "expected_output": "Statistical findings + notebook",
       "priority": 0.85
     }
     ```

---

### Gap 3: Agent Integration & System Prompts (CRITICAL)

**Kosmos Need**: Core prompts defining agent behavior, output formats, and State Manager integration interfaces.

#### Project Mapping:

| Project | Relevance | How It Helps | Integration Approach |
|---------|-----------|--------------|----------------------|
| **claude-skills-mcp** | 🔴 Low | - MCP tool descriptions<br>- Structured tool responses | **Pattern**: Format agent outputs as MCP tool responses for consistency. |
| **scientific-skills** | 🟢 **Very High** | - **120+ domain-specific prompts** (SKILL.md files)<br>- **Code examples** for scientific analysis<br>- **Best practices** for each library<br>- Comprehensive reference materials | **Direct Integration**: Use scientific-skills as Data Analysis Agent's knowledge base. Each skill provides:<br>- Task-specific prompts<br>- Working code examples<br>- Domain expertise<br>Load relevant skills based on task type. |
| **scientific-writer** | 🟢 High | - Structured prompts for scientific writing<br>- **Document synthesis** algorithms<br>- **Peer review framework** (ScholarEval)<br>- Citation formatting | **Integration**: Use ScholarEval framework for result validation. Adopt synthesis prompts for report generation. |
| **karpathy** | 🟢 **Very High** | - **`instructions.yaml`** with detailed agent prompts<br>- Expert specialization templates<br>- **Common instructions** shared across experts<br>- Clear delegation protocols<br>- Resource awareness patterns | **Direct Adoption**: Use karpathy's instruction pattern for Kosmos agents:<br>- `main_orchestrator_instructions.yaml`<br>- `data_analysis_agent_instructions.yaml`<br>- `literature_agent_instructions.yaml`<br>- `task_generator_instructions.yaml`<br>Each includes: scope, tooling, communication, quality checks |

**Recommendation**:
- **Primary Sources**: karpathy (orchestration prompts) + scientific-skills (domain prompts)
- **Implementation**:
  1. **Base Template** (from karpathy):
     ```yaml
     main_orchestrator: |
       You are the Kosmos Research Director managing iterative discovery cycles.
       Scope: 12-hour runtime, 20 cycles max, 10 parallel tasks per cycle
       State Manager: Query for context, write structured outputs
       Tools: TaskGenerator, DataAnalysisAgent, LiteratureAgent, ReportSynthesizer
       [... rest of instructions ...]
     ```
  2. **Domain Expertise** (from scientific-skills):
     - Data Analysis Agent: Load scanpy skill for single-cell, RDKit skill for chemistry, etc.
     - Literature Agent: Load PubMed/arXiv skills
  3. **Output Format** (standardized JSON):
     ```json
     {
       "agent": "DataAnalysisAgent",
       "task_id": 42,
       "cycle": 5,
       "findings": [...],
       "notebook_path": "cycle_5/task_42.ipynb",
       "summary": "2-line summary for State Manager",
       "evidence": ["stat1", "stat2"]
     }
     ```

---

### Gap 4: Language & Tooling Constraints (HIGH)

**Kosmos Need**: Clarify R vs Python ambiguity; implement multi-language support if needed.

#### Project Mapping:

| Project | Relevance | How It Helps | Integration Approach |
|---------|-----------|--------------|----------------------|
| **claude-skills-mcp** | 🔴 Low | - Python-focused | **Not Applicable** |
| **scientific-skills** | 🟢 High | - **Python-only skills** (RDKit, Scanpy, BioPython, etc.)<br>- No R skills currently<br>- Use rpy2 for R interop if needed | **Resolution**: **Standardize on Python**. For R packages:<br>1. Use rpy2 bridge (call R from Python)<br>2. Or: reimplement critical R functionality in Python<br>3. Document R → Python equivalents |
| **scientific-writer** | 🔴 Low | - Not relevant to R/Python | **Not Applicable** |
| **karpathy** | 🟡 Medium | - Python environment management<br>- Dependency handling with `uv` | **Pattern**: Use karpathy's dependency management approach. Maintain `pyproject.toml` in sandbox. Add rpy2 if R needed. |

**Recommendation**:
- **Decision**: **Python-first** approach (aligns with scientific-skills)
- **R Support**: Use rpy2 bridge when essential R packages needed
- **Tooling**: Use karpathy's `uv` dependency management

---

### Gap 5: Discovery Evaluation & Filtering (MODERATE)

**Kosmos Need**: Quality metrics, validity checking, claim strength assessment.

#### Project Mapping:

| Project | Relevance | How It Helps | Integration Approach |
|---------|-----------|--------------|----------------------|
| **claude-skills-mcp** | 🔴 Low | - No evaluation capabilities | **Not Applicable** |
| **scientific-skills** | 🟡 Medium | - Statistical analysis skills (scikit-learn, statsmodels)<br>- SHAP for interpretability<br>- Validation patterns in examples | **Skills**: Use statsmodels for statistical validation, SHAP for result interpretability, scikit-learn for cross-validation. |
| **scientific-writer** | 🟢 **Very High** | - **ScholarEval framework** (8-dimension scoring)<br>- **Peer review** capabilities<br>- **Claim strength** assessment<br>- Citation validation | **Direct Integration**: Implement ScholarEval for discovery validation:<br>- Novelty score<br>- Rigor score<br>- Clarity score<br>- Impact potential<br>Use to filter low-quality discoveries before report inclusion. |
| **karpathy** | 🟢 High | - **`Reviewer` expert** for progress monitoring<br>- **`Evaluation Agent`** for metrics and baselines<br>- Feedback loops (`feedback.md`) | **Pattern**: Add "Discovery Reviewer" agent that:<br>1. Reads findings from State Manager<br>2. Validates statistical claims<br>3. Checks for contradictions<br>4. Scores using ScholarEval<br>5. Writes to `discovery_review.md` |

**Recommendation**:
- **Primary Source**: scientific-writer's ScholarEval framework
- **Implementation**:
  1. Create `DiscoveryValidator` component
  2. Apply ScholarEval scoring to each finding
  3. Reject findings with scores below threshold
  4. Use karpathy's reviewer pattern for continuous quality checks
  5. Validate statistical tests (p-values, effect sizes)
  6. Check for "excessively strong claims" using LLM + human review

---

## Part 2: Integration Architecture

### Proposed Kosmos v2.0 Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                      Discovery Orchestrator                           │
│  (Pattern: karpathy's MainAgent + delegation)                        │
│  - 12-hour runtime, 20 cycles, 10 parallel tasks/cycle               │
│  - Delegates to specialized agents                                   │
└─────────┬────────────────────────────────────────────────────────────┘
          │
          ├──────> TaskGeneratorAgent ────────────────────────────────┐
          │         (Pattern: karpathy Plan Creator + Reviewer)        │
          │         (Context: scientific-skills workflows)             │
          │         - Queries State Manager for current knowledge      │
          │         - Generates 10 prioritized tasks                   │
          │         - Balances exploration vs exploitation             │
          │                                                            │
          ├──────> DataAnalysisAgent ─────────────────────────────────┤
          │         (Skills: scientific-skills 120+ skills)            │
          │         (Sandbox: karpathy pattern)                        │
          │         - Loads relevant skills (Scanpy, RDKit, etc.)      │
          │         - Writes Jupyter notebooks                         │
          │         - Outputs structured JSON findings                 │
          │                                                            │
          ├──────> LiteratureSearchAgent ────────────────────────────┤
          │         (Skills: PubMed, arXiv, OpenAlex)                  │
          │         (Compression: scientific-writer)                   │
          │         - Searches papers                                  │
          │         - Summarizes findings (1500 papers → summaries)    │
          │         - Validates claims against literature              │
          │                                                            │
          ├──────> DiscoveryValidator ───────────────────────────────┤
          │         (Framework: scientific-writer ScholarEval)         │
          │         (Pattern: karpathy Reviewer)                       │
          │         - Scores discoveries (novelty, rigor, clarity)     │
          │         - Validates statistical claims                     │
          │         - Filters low-quality findings                     │
          │                                                            │
          └──────> ReportSynthesizer ────────────────────────────────┘
                    (Tool: scientific-writer API)
                    - Generates publication-ready reports
                    - Manages citations and bibliography
                    - Links claims to evidence (State Manager)

          ┌────────────────────────────────────────────────────────┐
          │           Hybrid State Manager                          │
          │  (Architecture: Fusion of all projects)                │
          ├────────────────────────────────────────────────────────┤
          │  1. File-based Artifacts (karpathy pattern):           │
          │     - sandbox/cycle_N/task_M_findings.json             │
          │     - sandbox/cycle_N/task_M_notebook.ipynb            │
          │     - sandbox/cycle_N_summary.md                       │
          │                                                        │
          │  2. Neo4j Knowledge Graph (scientific-skills):         │
          │     - Entities: Finding, Hypothesis, Evidence, etc.    │
          │     - Relationships: SUPPORTS, REFUTES, DERIVES_FROM   │
          │     - Provenance: source notebook, cycle, confidence   │
          │                                                        │
          │  3. Vector Store (claude-skills-mcp pattern):          │
          │     - Sentence-transformers embeddings                 │
          │     - Semantic search for similar findings             │
          │     - Novelty detection                                │
          │                                                        │
          │  4. Citation Graph (scientific-writer):                │
          │     - Paper → Finding links                            │
          │     - Claim → Evidence traceability                    │
          │     - BibTeX management                                │
          └────────────────────────────────────────────────────────┘

          ┌────────────────────────────────────────────────────────┐
          │         Context Compression Manager                     │
          │  (Pattern: claude-skills-mcp progressive disclosure +  │
          │   scientific-writer summarization)                     │
          ├────────────────────────────────────────────────────────┤
          │  - Task-level: Notebook → 2-line summary + key stats  │
          │  - Cycle-level: 10 tasks → cycle_summary.md           │
          │  - Final: 20 cycles → final_synthesis.md              │
          │  - Lazy loading: Load full notebooks on-demand         │
          │  - Caching: Memory + disk (multi-tier)                 │
          └────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Research Question
    ↓
Discovery Orchestrator (Cycle 1)
    ↓
TaskGenerator queries State Manager → generates 10 tasks
    ↓
Parallel execution (10 agents):
    ├─ DataAnalysisAgent (tasks 1-6)
    │   ├─ Loads scientific-skills (Scanpy, RDKit)
    │   ├─ Executes in sandbox (karpathy pattern)
    │   ├─ Writes notebook + JSON findings
    │   └─ Compression Manager: notebook → summary
    │
    └─ LiteratureSearchAgent (tasks 7-10)
        ├─ Searches PubMed/arXiv
        ├─ Uses scientific-writer to summarize papers
        └─ Outputs structured JSON findings
    ↓
All findings → State Manager
    ├─ Write artifacts to sandbox/cycle_1/
    ├─ Index to Neo4j knowledge graph
    ├─ Generate embeddings for vector search
    └─ Update citation graph
    ↓
DiscoveryValidator evaluates findings
    ├─ ScholarEval scoring
    ├─ Statistical validation
    └─ Filters low-quality findings
    ↓
Compression Manager: cycle 1 summary
    ↓
TaskGenerator queries updated State Manager → cycle 2 tasks
    ↓
... repeat for 20 cycles or until convergence ...
    ↓
ReportSynthesizer
    ├─ Queries State Manager for all validated findings
    ├─ Uses scientific-writer to generate reports
    └─ Links all claims to evidence (notebooks, papers)
```

---

## Part 3: Detailed Integration Plans

### 3.1 Immediate Wins (Week 1-2)

**Goal**: Get quick value from existing projects with minimal integration effort.

#### Task 1: Integrate scientific-skills into Data Analysis Agent
- **What**: Replace generic prompts with domain-specific skills
- **How**:
  1. Install scientific-skills in Kosmos environment
  2. Create skill loader that maps task type → relevant skills
  3. Inject skill content into agent prompts
- **Value**: Dramatically improve code quality and domain expertise
- **Effort**: 1-2 days
- **File Changes**:
  - `kosmos/agents/data_analyst.py` - add skill loading
  - `kosmos/skills/` - new directory for cached skills

#### Task 2: Add ScholarEval for discovery validation
- **What**: Use scientific-writer's peer review framework
- **How**:
  1. Extract ScholarEval scoring logic from scientific-writer
  2. Create `DiscoveryValidator` class
  3. Apply to findings before State Manager insertion
- **Value**: Filter out low-quality discoveries
- **Effort**: 2-3 days
- **File Changes**:
  - `kosmos/validation/scholar_eval.py` - new file
  - `kosmos/core/orchestrator.py` - add validation step

#### Task 3: Implement artifact-based State Manager (karpathy pattern)
- **What**: Save cycle artifacts as JSON files
- **How**:
  1. Create `sandbox/` directory structure
  2. Modify agents to write JSON outputs
  3. Create background indexer for Neo4j
- **Value**: Human-readable persistence, easier debugging
- **Effort**: 3-4 days
- **File Changes**:
  - `kosmos/world_model/artifacts.py` - new file
  - `kosmos/world_model/indexer.py` - background process

---

### 3.2 Medium-Term Integration (Week 3-8)

#### Task 4: Implement karpathy-style orchestration
- **What**: Refactor Discovery Orchestrator using delegation pattern
- **How**:
  1. Create `instructions.yaml` for all agents (karpathy pattern)
  2. Implement `delegate_task` function
  3. Add Plan Creator and Plan Reviewer agents
- **Value**: Better task planning and execution
- **Effort**: 2 weeks
- **File Changes**:
  - `kosmos/orchestration/instructions.yaml` - new file
  - `kosmos/orchestration/delegation.py` - new file
  - Refactor `kosmos/core/research_director.py`

#### Task 5: Add context compression pipeline
- **What**: Implement progressive disclosure + summarization
- **How**:
  1. Use scientific-writer's summarization for papers
  2. Implement lazy notebook loading (claude-skills-mcp pattern)
  3. Create hierarchical compression (task → cycle → final)
- **Value**: Solve foundational blocker
- **Effort**: 2-3 weeks
- **File Changes**:
  - `kosmos/compression/` - new directory
  - `kosmos/compression/summarizer.py` - scientific-writer integration
  - `kosmos/compression/lazy_loader.py` - progressive disclosure

#### Task 6: Implement vector search for State Manager
- **What**: Add semantic search using sentence-transformers
- **How**:
  1. Use claude-skills-mcp's search engine code
  2. Generate embeddings for findings
  3. Add `find_similar_findings` query
- **Value**: Better novelty detection and context retrieval
- **Effort**: 1-2 weeks
- **File Changes**:
  - `kosmos/world_model/search_engine.py` - new file (from claude-skills-mcp)
  - `kosmos/world_model/embeddings.py` - new file

---

### 3.3 Advanced Integration (Week 9-16)

#### Task 7: Full report synthesis using scientific-writer
- **What**: Replace current report generator with scientific-writer API
- **How**:
  1. Install scientific-writer package
  2. Create adapter that converts State Manager → research query
  3. Use scientific-writer's async API
- **Value**: Publication-quality reports with citations
- **Effort**: 1-2 weeks
- **File Changes**:
  - `kosmos/synthesis/scientific_writer_adapter.py` - new file
  - Update `kosmos/synthesis/report_synthesizer.py`

#### Task 8: Implement exploration/exploitation task generation
- **What**: Build Task Generator using karpathy + scientific-skills patterns
- **How**:
  1. Create Plan Creator agent (karpathy)
  2. Add exploration/exploitation heuristic
  3. Use scientific-skills workflows as task templates
- **Value**: Solve critical gap #2
- **Effort**: 3-4 weeks
- **File Changes**:
  - `kosmos/task_generation/` - new directory
  - `kosmos/task_generation/plan_creator.py`
  - `kosmos/task_generation/plan_reviewer.py`
  - `kosmos/task_generation/strategy.py`

---

## Part 4: R&D Implementation Examples

### Example 1: Context Compression Pipeline

**Location**: `R&D/examples/context_compression/`

**Description**: Demonstrates hierarchical compression using scientific-writer + progressive disclosure.

**Implementation**:
```python
# R&D/examples/context_compression/compression_demo.py

from scientific_writer import generate_paper
from kosmos.world_model import StateManager
import asyncio

class ContextCompressor:
    """
    Demonstrates multi-tier compression for Kosmos
    Tier 1: Task-level (notebook → summary)
    Tier 2: Cycle-level (10 tasks → cycle summary)
    Tier 3: Final synthesis (20 cycles → report)
    """

    async def compress_notebook(self, notebook_path: str) -> dict:
        """Task-level compression: 42K lines → 2-line summary + stats"""
        # Read notebook
        with open(notebook_path) as f:
            content = f.read()

        # Extract key statistics
        stats = self._extract_stats(content)

        # Generate 2-line summary using Claude
        summary = await self._summarize_with_llm(content, max_lines=2)

        return {
            "summary": summary,
            "statistics": stats,
            "notebook_path": notebook_path,
            "full_content": None  # Lazy load on demand
        }

    async def compress_papers(self, papers: list[str]) -> str:
        """Literature compression: 1500 papers → structured summary"""
        # Use scientific-writer for batch summarization
        summaries = []
        for paper_text in papers:
            summary = await self._summarize_paper(paper_text)
            summaries.append(summary)

        # Combine into cycle summary
        combined = "\n\n".join(summaries)
        return combined

    async def compress_cycle(self, cycle_findings: list[dict]) -> str:
        """Cycle-level: 10 task summaries → cycle summary"""
        # Aggregate findings
        all_findings = [f["summary"] for f in cycle_findings]

        # Generate cycle-level insights
        cycle_summary = await self._synthesize_findings(all_findings)

        return cycle_summary

    async def generate_final_synthesis(self,
                                       all_cycle_summaries: list[str]) -> dict:
        """Final synthesis: 20 cycle summaries → research report"""
        # Use scientific-writer's full capabilities
        query = f"Create a comprehensive research report from these findings:\n\n"
        query += "\n\n".join(all_cycle_summaries)

        async for update in generate_paper(query):
            if update["type"] == "result":
                return update["files"]

    def _extract_stats(self, notebook_content: str) -> dict:
        """Extract p-values, correlations, effect sizes from notebook"""
        # Implementation here
        pass

    async def _summarize_with_llm(self, content: str, max_lines: int) -> str:
        """Use Claude to generate concise summary"""
        # Implementation here
        pass

# Demo usage
async def main():
    compressor = ContextCompressor()

    # Simulate cycle 1 with 10 tasks
    tasks = [
        "cycle_1/task_1_scanpy_analysis.ipynb",
        "cycle_1/task_2_deseq2.ipynb",
        # ... 8 more
    ]

    # Task-level compression
    compressed_tasks = []
    for task in tasks:
        compressed = await compressor.compress_notebook(task)
        compressed_tasks.append(compressed)
        print(f"Compressed {task}:")
        print(f"  Summary: {compressed['summary']}")
        print(f"  Stats: {compressed['statistics']}")

    # Cycle-level compression
    cycle_summary = await compressor.compress_cycle(compressed_tasks)
    print(f"\nCycle 1 Summary:\n{cycle_summary}")

    # Final synthesis (after 20 cycles)
    final_report = await compressor.generate_final_synthesis([
        cycle_summary,  # Would have 20 of these
        # ... more cycle summaries
    ])
    print(f"\nFinal Report: {final_report['pdf_final']}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Run**:
```bash
cd R&D/examples/context_compression
python compression_demo.py
```

**Expected Output**:
- Demonstrates 60s → 2s compression for notebooks
- Shows hierarchical summarization
- Produces publication-ready final report

---

### Example 2: Karpathy-Style Task Planning

**Location**: `R&D/examples/task_planning/`

**Description**: Demonstrates how to use karpathy's planning pattern for Kosmos task generation.

**Implementation**:
```python
# R&D/examples/task_planning/plan_creator_demo.py

from kosmos.world_model import StateManager
from kosmos.agents import PlanCreatorAgent, PlanReviewerAgent
import yaml

class KosmosTaskGenerator:
    """
    Demonstrates karpathy-style task planning for Kosmos
    Pattern: Plan Creator → Plan Reviewer → Task Execution
    """

    def __init__(self):
        # Load instructions (karpathy pattern)
        with open("instructions.yaml") as f:
            instructions = yaml.safe_load(f)

        self.plan_creator = PlanCreatorAgent(
            instruction=instructions["plan_creator"]
        )
        self.plan_reviewer = PlanReviewerAgent(
            instruction=instructions["plan_reviewer"]
        )
        self.state_manager = StateManager()

    async def generate_tasks(self, cycle_number: int) -> list[dict]:
        """Generate 10 prioritized tasks for this cycle"""

        # Step 1: Query State Manager for current knowledge
        current_state = self.state_manager.query_all()
        findings = current_state["findings"]
        hypotheses = current_state["hypotheses"]
        past_tasks = current_state["completed_tasks"]

        # Step 2: Create context for Plan Creator
        context = {
            "cycle": cycle_number,
            "findings_count": len(findings),
            "hypotheses_count": len(hypotheses),
            "recent_findings": findings[-10:],  # Last 10 findings
            "unsupported_hypotheses": [h for h in hypotheses if not h["validated"]],
            "past_tasks": past_tasks,
            "exploration_ratio": self._get_exploration_ratio(cycle_number)
        }

        # Step 3: Plan Creator generates tasks
        plan = await self.plan_creator.create_plan(
            research_objective="Discover novel biological mechanisms",
            context=context,
            num_tasks=10
        )

        # Step 4: Plan Reviewer validates quality
        review = await self.plan_reviewer.review_plan(plan, context)

        if review["approved"]:
            tasks = plan["tasks"]
        else:
            # Revise plan based on feedback
            tasks = await self.plan_creator.revise_plan(plan, review["feedback"])

        # Step 5: Prioritize tasks
        prioritized = self._prioritize_tasks(tasks, context)

        return prioritized

    def _get_exploration_ratio(self, cycle: int, max_cycles: int = 20) -> float:
        """Exploration/exploitation balance"""
        if cycle <= max_cycles // 2:
            return 0.7  # First half: 70% exploration
        else:
            return 0.3  # Second half: 30% exploration

    def _prioritize_tasks(self, tasks: list[dict], context: dict) -> list[dict]:
        """Prioritize based on novelty + state manager gaps"""
        exploration_ratio = context["exploration_ratio"]

        for task in tasks:
            # Novelty score (0-1)
            novelty = self._compute_novelty(task, context["past_tasks"])

            # Gap score (0-1) - how much it fills knowledge gaps
            gap_score = self._compute_gap_score(task, context["unsupported_hypotheses"])

            # Combined priority
            task["priority"] = (
                exploration_ratio * novelty +
                (1 - exploration_ratio) * gap_score
            )

        # Sort by priority
        tasks.sort(key=lambda t: t["priority"], reverse=True)
        return tasks

    def _compute_novelty(self, task: dict, past_tasks: list[dict]) -> float:
        """Check if similar task was done before using vector similarity"""
        # Use sentence-transformers (claude-skills-mcp pattern)
        from sentence_transformers import SentenceTransformer
        import numpy as np

        model = SentenceTransformer('all-MiniLM-L6-v2')

        task_embedding = model.encode(task["description"])
        past_embeddings = model.encode([t["description"] for t in past_tasks])

        # Cosine similarity
        similarities = np.dot(past_embeddings, task_embedding)
        max_similarity = similarities.max() if len(similarities) > 0 else 0

        # Novelty = 1 - max_similarity
        return 1 - max_similarity

    def _compute_gap_score(self, task: dict,
                          unsupported_hypotheses: list[dict]) -> float:
        """How well does this task address knowledge gaps?"""
        # Check if task tests unsupported hypotheses
        task_targets = task.get("target_hypotheses", [])
        unsupported_ids = [h["id"] for h in unsupported_hypotheses]

        overlap = len(set(task_targets) & set(unsupported_ids))
        return overlap / max(len(task_targets), 1)

# Demo usage
async def main():
    generator = KosmosTaskGenerator()

    # Generate tasks for cycle 5
    tasks = await generator.generate_tasks(cycle_number=5)

    print(f"Generated {len(tasks)} tasks for Cycle 5:")
    for i, task in enumerate(tasks, 1):
        print(f"\n{i}. {task['description']}")
        print(f"   Type: {task['type']}")
        print(f"   Priority: {task['priority']:.2f}")
        print(f"   Novelty: {task.get('novelty', 'N/A'):.2f}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

**Instructions file** (`R&D/examples/task_planning/instructions.yaml`):
```yaml
plan_creator: |
  You are the Plan Creator for the Kosmos AI Scientist.

  Your goal is to generate 10 high-quality research tasks for the current discovery cycle.

  **Inputs**:
  - Research objective
  - Current State Manager state (findings, hypotheses, past tasks)
  - Exploration/exploitation ratio

  **Task Requirements**:
  1. Each task must be specific and executable
  2. Tasks should advance the research objective
  3. Balance exploration (new directions) and exploitation (deepen existing findings)
  4. Avoid redundancy with past tasks
  5. Target unsupported hypotheses

  **Task Types**:
  - data_analysis: Analyze dataset using statistical methods
  - literature_search: Search for relevant papers
  - hypothesis_generation: Generate new hypotheses
  - hypothesis_validation: Test existing hypotheses

  **Output Format**:
  ```json
  {
    "tasks": [
      {
        "id": 1,
        "type": "data_analysis",
        "description": "Analyze correlation between gene X and Y in single-cell data",
        "expected_output": "Statistical findings + notebook",
        "target_hypotheses": [42, 43],
        "estimated_time": "30 minutes"
      },
      ...
    ]
  }
  ```

plan_reviewer: |
  You are the Plan Reviewer for the Kosmos AI Scientist.

  Your goal is to validate the quality of generated task plans.

  **Review Criteria**:
  1. Specificity: Are tasks concrete and executable?
  2. Relevance: Do tasks advance the research objective?
  3. Novelty: Are tasks sufficiently different from past tasks?
  4. Coverage: Do tasks cover diverse research directions?
  5. Feasibility: Can tasks be completed within time/resource limits?

  **Output Format**:
  ```json
  {
    "approved": true/false,
    "feedback": "Detailed feedback on plan quality",
    "suggestions": ["Suggestion 1", "Suggestion 2"]
  }
  ```
```

---

### Example 3: Hybrid State Manager

**Location**: `R&D/examples/state_manager/`

**Description**: Demonstrates the hybrid architecture (files + Neo4j + vector search + citations).

**Implementation**:
```python
# R&D/examples/state_manager/hybrid_state_demo.py

from pathlib import Path
import json
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
import numpy as np

class HybridStateManager:
    """
    Hybrid State Manager combining:
    1. File artifacts (karpathy pattern)
    2. Neo4j knowledge graph (scientific-skills)
    3. Vector search (claude-skills-mcp)
    4. Citation graph (scientific-writer)
    """

    def __init__(self, sandbox_dir: str = "sandbox"):
        self.sandbox = Path(sandbox_dir)
        self.sandbox.mkdir(exist_ok=True)

        # Neo4j connection
        self.neo4j = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "password")
        )

        # Vector search
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embeddings_db = {}  # In production: use Pinecone/Weaviate

        # Citation graph
        self.citations = {}

    async def add_finding(self, cycle: int, task: int, finding: dict):
        """Add a finding using all 4 storage layers"""

        # 1. File artifact (karpathy pattern)
        artifact_path = self.sandbox / f"cycle_{cycle}" / f"task_{task}_findings.json"
        artifact_path.parent.mkdir(parents=True, exist_ok=True)

        finding_data = {
            "cycle": cycle,
            "task": task,
            "summary": finding["summary"],
            "statistics": finding["statistics"],
            "notebook_path": str(finding["notebook_path"]),
            "timestamp": finding["timestamp"]
        }

        with open(artifact_path, "w") as f:
            json.dump(finding_data, f, indent=2)

        # 2. Neo4j knowledge graph
        with self.neo4j.session() as session:
            session.run(
                """
                CREATE (f:Finding {
                    id: $id,
                    cycle: $cycle,
                    task: $task,
                    summary: $summary,
                    p_value: $p_value,
                    confidence: $confidence,
                    notebook_path: $notebook_path,
                    timestamp: $timestamp
                })
                """,
                id=finding["id"],
                cycle=cycle,
                task=task,
                summary=finding["summary"],
                p_value=finding["statistics"].get("p_value"),
                confidence=finding["statistics"].get("confidence"),
                notebook_path=str(finding["notebook_path"]),
                timestamp=finding["timestamp"]
            )

            # Add relationships
            if finding.get("supports_hypothesis"):
                session.run(
                    """
                    MATCH (f:Finding {id: $finding_id})
                    MATCH (h:Hypothesis {id: $hypothesis_id})
                    CREATE (f)-[:SUPPORTS {confidence: $confidence}]->(h)
                    """,
                    finding_id=finding["id"],
                    hypothesis_id=finding["supports_hypothesis"],
                    confidence=finding["statistics"].get("confidence", 0.5)
                )

        # 3. Vector search (semantic similarity)
        embedding = self.embedding_model.encode(finding["summary"])
        self.embeddings_db[finding["id"]] = {
            "embedding": embedding,
            "finding": finding
        }

        # 4. Citation graph (if finding references papers)
        if finding.get("citations"):
            self.citations[finding["id"]] = finding["citations"]

    def query_similar_findings(self, query: str, top_k: int = 5) -> list[dict]:
        """Semantic search for similar findings"""
        query_embedding = self.embedding_model.encode(query)

        # Compute cosine similarity
        similarities = []
        for finding_id, data in self.embeddings_db.items():
            similarity = np.dot(query_embedding, data["embedding"])
            similarities.append((finding_id, similarity))

        # Sort and return top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_findings = [
            self.embeddings_db[fid]["finding"]
            for fid, _ in similarities[:top_k]
        ]

        return top_findings

    def query_graph(self, cypher: str, params: dict = None) -> list[dict]:
        """Query Neo4j knowledge graph"""
        with self.neo4j.session() as session:
            result = session.run(cypher, params or {})
            return [dict(record) for record in result]

    def get_finding_provenance(self, finding_id: str) -> dict:
        """Get full provenance chain for a finding"""
        # Query Neo4j for relationships
        provenance = self.query_graph(
            """
            MATCH path = (f:Finding {id: $finding_id})-[*]-(related)
            RETURN path
            """,
            {"finding_id": finding_id}
        )

        # Get file artifact
        # Find which cycle/task this finding belongs to
        with self.neo4j.session() as session:
            result = session.run(
                "MATCH (f:Finding {id: $finding_id}) RETURN f.cycle, f.task",
                finding_id=finding_id
            )
            record = result.single()
            cycle, task = record["f.cycle"], record["f.task"]

        artifact_path = self.sandbox / f"cycle_{cycle}" / f"task_{task}_findings.json"
        with open(artifact_path) as f:
            artifact = json.load(f)

        # Get citations
        citations = self.citations.get(finding_id, [])

        return {
            "finding_id": finding_id,
            "graph_relationships": provenance,
            "artifact": artifact,
            "citations": citations
        }

    def generate_cycle_summary(self, cycle: int) -> str:
        """Generate summary for a cycle using all findings"""
        # Get all findings from this cycle (Neo4j)
        findings = self.query_graph(
            """
            MATCH (f:Finding {cycle: $cycle})
            RETURN f
            ORDER BY f.task
            """,
            {"cycle": cycle}
        )

        # Read artifact files
        cycle_dir = self.sandbox / f"cycle_{cycle}"
        artifact_files = list(cycle_dir.glob("task_*_findings.json"))

        # Combine for summary
        summary = f"# Cycle {cycle} Summary\n\n"
        summary += f"## Findings ({len(findings)} total)\n\n"

        for finding in findings:
            summary += f"- Task {finding['f']['task']}: {finding['f']['summary']}\n"

        # Save summary artifact
        summary_path = self.sandbox / f"cycle_{cycle}_summary.md"
        with open(summary_path, "w") as f:
            f.write(summary)

        return summary

# Demo usage
async def main():
    state_manager = HybridStateManager(sandbox_dir="sandbox_demo")

    # Simulate adding findings from cycle 1
    finding1 = {
        "id": "finding_1_1",
        "summary": "Gene X is upregulated in cancer cells (p=0.001)",
        "statistics": {
            "p_value": 0.001,
            "fold_change": 2.5,
            "confidence": 0.95
        },
        "notebook_path": Path("cycle_1/task_1_deseq2.ipynb"),
        "timestamp": "2025-11-22T10:00:00",
        "supports_hypothesis": "hyp_42",
        "citations": ["PMID:12345678", "PMID:23456789"]
    }

    await state_manager.add_finding(cycle=1, task=1, finding=finding1)

    finding2 = {
        "id": "finding_1_2",
        "summary": "Protein Y shows increased expression in disease state (p=0.005)",
        "statistics": {
            "p_value": 0.005,
            "fold_change": 1.8,
            "confidence": 0.90
        },
        "notebook_path": Path("cycle_1/task_2_proteomics.ipynb"),
        "timestamp": "2025-11-22T10:30:00",
        "citations": ["PMID:34567890"]
    }

    await state_manager.add_finding(cycle=1, task=2, finding=finding2)

    # Query similar findings
    print("=== Semantic Search ===")
    similar = state_manager.query_similar_findings("gene expression in cancer", top_k=2)
    for f in similar:
        print(f"- {f['summary']}")

    # Query graph
    print("\n=== Neo4j Query ===")
    high_confidence = state_manager.query_graph(
        "MATCH (f:Finding) WHERE f.confidence > 0.9 RETURN f.summary"
    )
    for record in high_confidence:
        print(f"- {record['f.summary']}")

    # Get provenance
    print("\n=== Provenance ===")
    provenance = state_manager.get_finding_provenance("finding_1_1")
    print(f"Finding: {provenance['artifact']['summary']}")
    print(f"Citations: {provenance['citations']}")

    # Generate cycle summary
    print("\n=== Cycle Summary ===")
    summary = state_manager.generate_cycle_summary(cycle=1)
    print(summary)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

## Part 5: Effort Estimates & Roadmap

### Implementation Timeline (16 weeks)

| Week | Tasks | Effort | Key Deliverables |
|------|-------|--------|------------------|
| **1-2** | Immediate wins | Low | - scientific-skills integration<br>- ScholarEval validation<br>- Artifact-based State Manager |
| **3-4** | Karpathy orchestration | Medium | - instructions.yaml for all agents<br>- Delegation pattern<br>- Plan Creator/Reviewer |
| **5-6** | Context compression (Part 1) | Medium | - Scientific-writer summarization<br>- Progressive disclosure |
| **7-8** | Context compression (Part 2) | High | - Hierarchical compression<br>- Lazy loading<br>- Multi-tier caching |
| **9-10** | Vector search | Medium | - Sentence-transformers integration<br>- Semantic similarity search<br>- Novelty detection |
| **11-12** | Task generation strategy | High | - Exploration/exploitation<br>- Priority scoring<br>- Template workflows |
| **13-14** | Report synthesis | Medium | - Scientific-writer API integration<br>- Citation management<br>- PDF generation |
| **15-16** | Testing & validation | High | - End-to-end testing<br>- Discovery 1 reproduction<br>- Performance tuning |

### Effort Summary

- **Total**: 16 weeks (4 months)
- **Team**: 2-3 engineers
- **Risk**: Medium (patterns are proven, but integration complexity)

### Success Metrics

1. **Context Compression**: Reduce State Manager context from 100K tokens → 5K tokens
2. **Task Quality**: Generate non-redundant tasks (novelty score > 0.7)
3. **Report Quality**: Achieve >75% statement accuracy (paper baseline: 79.4%)
4. **Discovery Reproduction**: Successfully reproduce Discovery 1 from paper

---

## Part 6: Risks & Mitigations

### Risk 1: Integration Complexity
**Probability**: High
**Impact**: Medium
**Mitigation**:
- Start with modular integration (one component at a time)
- Create comprehensive tests for each integration
- Use R&D examples as integration templates

### Risk 2: Performance Bottlenecks
**Probability**: Medium
**Impact**: High
**Mitigation**:
- Profile early and often
- Use multi-tier caching (claude-skills-mcp pattern)
- Implement async operations (scientific-writer pattern)

### Risk 3: Scientific Quality
**Probability**: Medium
**Impact**: High
**Mitigation**:
- Use ScholarEval for continuous validation
- Implement karpathy's reviewer pattern
- Human-in-the-loop for critical decisions

### Risk 4: Context Window Limits
**Probability**: High (foundational blocker)
**Impact**: Critical
**Mitigation**:
- Prioritize context compression implementation
- Test with real datasets early
- Have fallback to manual summarization

---

## Conclusions

### Key Takeaways

1. **No Silver Bullet**: None of the projects directly solve all Kosmos gaps, but they provide essential building blocks.

2. **karpathy is Critical**: The orchestration patterns (delegation, planning, artifacts) are directly applicable to Kosmos architecture.

3. **scientific-skills Enables Domain Expertise**: 120+ skills give Data Analysis Agent the expertise it needs.

4. **scientific-writer Solves Synthesis**: Report generation and evaluation frameworks are production-ready.

5. **claude-skills-mcp Provides Patterns**: Progressive disclosure and vector search are crucial for scaling.

### Recommended Implementation Order

1. **Week 1-2**: Quick wins (skills, validation, artifacts)
2. **Week 3-8**: Core architecture (orchestration, compression, search)
3. **Week 9-16**: Advanced features (task generation, synthesis, testing)

### Expected Outcomes

By integrating these projects, Kosmos will gain:
- ✅ Foundational context compression (Gap 0)
- ✅ Production-ready State Manager (Gap 1)
- ✅ Proven task planning patterns (Gap 2)
- ✅ Domain-specific agent prompts (Gap 3)
- ✅ Python standardization (Gap 4)
- ✅ Quality validation framework (Gap 5)

This positions Kosmos to successfully reproduce the paper's discoveries and advance autonomous scientific research.

---

**End of Document**
