# Kosmos AI Scientist

> Autonomous AI scientist for hypothesis generation, experimental design, and iterative scientific discovery. Supports Claude, OpenAI, and local models.

[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](https://github.com/jimmc414/Kosmos)
[![Status](https://img.shields.io/badge/status-e2e%20testing-yellow.svg)](https://github.com/jimmc414/Kosmos)
[![Tests](https://img.shields.io/badge/tests-in%20development-yellow.svg)](https://github.com/jimmc414/Kosmos)

Kosmos is an open-source implementation of an autonomous AI scientist that conducts research cycles: literature analysis, hypothesis generation, experimental design, execution, analysis, and iterative refinement.

v0.2.0 supports Anthropic Claude, OpenAI GPT, and local models (Ollama, LM Studio) with configuration-driven provider switching. Performance optimizations (20-40x in specific operations) and multi-domain capabilities are implemented.

## Development Status

Kosmos v0.2.0 is in end-to-end testing phase, working toward production readiness.

Current state:
- All 10 development phases implemented
- Core autonomous research workflow functional
- Advanced analytics added (SHAP, pathway enrichment, segmented regression)
- Known issues under investigation ([#7](https://github.com/jimmc414/Kosmos/issues/7), [#11](https://github.com/jimmc414/Kosmos/issues/11))
- Requirements Traceability Matrix in development
- Test coverage being expanded systematically

Implementation status:
- Core infrastructure: Operational
- Data Analysis Agent: Functional, new methods added
- Literature Search Agent: Functional, citation graphs implemented
- World Model: Functional, Neo4j-dependent features require configuration
- Orchestrator: Functional, convergence detection operational
- Multi-domain support: Biology, neuroscience, physics, chemistry, materials science

[View Phase Completion Reports](docs/phase-reports/) | [Implementation Plan](IMPLEMENTATION_PLAN.md)

## Implemented Features

### Core Capabilities
- **Autonomous Research Cycle**: Complete end-to-end scientific workflow
- **Multi-Domain Support**: Biology, physics, chemistry, neuroscience, materials science
- **Multi-Provider LLM Support**: Choose between Anthropic, OpenAI, or local models
- **Persistent Knowledge Graphs**: Automatic research tracking with export/import capabilities
- **Command-line Interface**: Rich terminal interface with 8 commands, interactive mode, and live progress
- **Agent-Based Architecture**: Modular agents for each research task
- **Safety-First Design**: Sandboxed execution, validation, reproducibility checks

### Multi-Provider LLM Support

Kosmos now supports multiple LLM providers, giving you flexibility in cost, privacy, and model selection:

| Provider | Type | Example Models | Privacy | Cost |
|----------|------|----------------|---------|------|
| **Anthropic** | Cloud | Claude 3.5 Sonnet, Opus, Haiku | Cloud | $$ |
| **OpenAI** | Cloud | GPT-4 Turbo, GPT-4, GPT-3.5, O1 | Cloud | $$$ |
| **Ollama** | Local | Llama 3.1, Mistral, Mixtral | **Private** | **Free** |
| **OpenRouter** | Aggregator | 100+ models | Cloud | Varies |
| **LM Studio** | Local | Any GGUF model | **Private** | **Free** |

Provider switching requires only `.env` configuration changes:

```bash
# Use OpenAI instead of Anthropic
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo

# Or run completely local with Ollama (free)
LLM_PROVIDER=openai
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=llama3.1:70b
```

Provider flexibility enables:
- Cost optimization through model mixing or local execution
- Privacy preservation via local-only operation
- Provider independence for availability and pricing management
- Rate limit mitigation through redundancy
- Access to domain-specific or fine-tuned models

[Provider Setup Guide](docs/providers/README.md) provides configuration details for all supported providers.

### Persistent Knowledge Graphs

Kosmos maintains a persistent knowledge graph that captures the research process. Hypotheses, experiments, and findings are stored in a connected graph structure that persists across sessions.

Captured data:
- Research questions and hypotheses
- Experiment protocols and results
- Relationships (SPAWNED_BY, TESTS, SUPPORTS, REFUTES, REFINED_FROM)
- Rich provenance (who, when, why, confidence scores, p-values)

Knowledge graph features:
- Knowledge accumulation over extended periods
- Research provenance tracking (hypothesis evolution, supporting evidence)
- Export and import for collaboration and backup
- Snapshot capability for version control at research milestones

CLI commands:

```bash
# View accumulated knowledge
kosmos graph --stats

# Example output:
# Knowledge Graph Statistics
#
# Entities:        127
# Relationships:   243
#
# Entity Types:
#   Hypothesis: 45
#   ExperimentProtocol: 28
#   ExperimentResult: 23

# Export for backup or sharing
kosmos graph --export my_research.json

# Restore from backup
kosmos graph --import my_research.json
```

Automatic persistence operates without manual intervention. When executing research queries:

```bash
kosmos research "How do transformers learn long-range dependencies?"
```

The system persists:
- ResearchQuestion entity
- Generated Hypothesis entities + SPAWNED_BY relationships
- ExperimentProtocol entities + TESTS relationships
- ExperimentResult entities + SUPPORTS/REFUTES relationships with statistical metadata
- Refined hypotheses + REFINED_FROM relationships

Setup:

```bash
# Docker deployment
docker-compose up -d neo4j

# Manual Neo4j installation
# Ubuntu: sudo apt install neo4j
# macOS: brew install neo4j

# Configure in .env
NEO4J_URI=bolt://localhost:7687
NEO4J_PASSWORD=kosmos-password
WORLD_MODEL_ENABLED=true
```

The system operates without Neo4j through graceful degradation. Graph features are optional.

[Complete Guide](docs/user/world_model_guide.md) provides detailed documentation including use cases, queries, and configuration.

### Performance & Scalability
- 20-40x performance improvement in specific operations through combined optimizations
- Parallel execution via ProcessPoolExecutor (4-16x faster experiments)
- Concurrent operations using async patterns (2-4x faster research cycles)
- Multi-tier caching system (30%+ API cost reduction)
- Database query optimization through strategic indexing
- Kubernetes HorizontalPodAutoscaler support for scaling

### Deployment Features
- Health monitoring via Prometheus metrics with configurable alerts
- Performance profiling for CPU, memory, and bottleneck detection
- Docker deployment through docker-compose with multi-service stack
- Kubernetes manifests for orchestrated deployment
- Cloud deployment documentation for AWS, GCP, Azure
- Test suite under active development (requirements traceability matrix in progress)

### Integration Capabilities
- Multiple LLM provider support (Anthropic Claude, OpenAI GPT, local models via Ollama/LM Studio)
- Statistical analysis methods from validated patterns
- Automated literature search, summarization, and novelty checking
- Comprehensive documentation across user guides, API references, and examples

## Performance & Optimization

### Caching System

Kosmos implements a multi-tier caching system that reduces API costs by 30-40%:

```bash
# View cache performance
kosmos cache --stats

# Example output:
# Overall Cache Performance:
#   Total Requests: 500
#   Cache Hits: 175 (35%)
#   Estimated Cost Savings: $15.75
```

Cache types:
- LLM Response Cache: API response caching (25-35% hit rate with Anthropic prompt caching)
- Experiment Cache: Computational result caching (40-50% hit rate)
- Embedding Cache: Vector embedding caching (in-memory)
- General Cache: Miscellaneous data caching

Benefits:
- API cost reduction (30%+ savings observed)
- Faster response times (90%+ improvement on cache hits)
- Availability through cached responses
- Reduced compute resource usage

Note: Prompt caching with substantial cost savings is available when using Anthropic Claude. OpenAI and local providers use in-memory response caching only.

### Automatic Model Selection (Anthropic Only)

When using Anthropic as your LLM provider, Kosmos intelligently selects between Claude models based on task complexity:

- **Claude Sonnet 4.5**: Complex reasoning, hypothesis generation, analysis
- **Claude Haiku 4**: Simple tasks, data extraction, formatting

This reduces costs by 15-20% while maintaining output quality.

Note: This feature is specific to Anthropic Claude. OpenAI and other providers use a single configured model.

### Expected Performance

Typical research run characteristics (using Anthropic Claude):

- Duration: 30 minutes to 2 hours
- Iterations: 5-15 iterations
- API Calls: 50-200 calls
- Cost: $5-$50 with caching, $8-$75 without (Anthropic pricing)
- Cache Hit Rate: 30-40% on subsequent runs (Anthropic prompt caching)

Note: Costs vary by provider. OpenAI pricing differs. Local models (Ollama/LM Studio) have no API costs.

## Quick Start

### Prerequisites

- Python 3.11 or 3.12
- LLM Provider (choose one):
  - Anthropic Claude (default): API key (pay-per-use) or Claude Code CLI (Max subscription)
  - OpenAI GPT: API key for GPT models
  - Ollama: Local models (no API key required)
  - Other providers: See [Provider Setup Guide](docs/providers/README.md)

### Installation

#### Option A: Automated Setup

Single-command installation handling all setup steps:

```bash
# Clone the repository
git clone https://github.com/jimmc414/Kosmos.git
cd Kosmos

# Run automated setup (creates venv, installs deps, configures environment)
make install

# Or step-by-step:
./scripts/setup_environment.sh  # Setup Python environment
./scripts/setup_docker_wsl2.sh  # Install Docker (WSL2 only, one-time)
./scripts/setup_neo4j.sh        # Setup Neo4j for knowledge graphs
```

Automated setup performs:
- Python 3.11+ version check
- Virtual environment creation
- Dependency installation
- .env file creation from template
- Data directory initialization
- Database migrations
- Installation verification

See [Automated Setup Guide](docs/user/automated-setup.md) for details.

#### Option B: Manual Installation

```bash
# Clone the repository
git clone https://github.com/jimmc414/Kosmos.git
cd Kosmos

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# For Claude Code CLI support
pip install -e ".[router]"
```

### Configuration

#### Option A: Using Anthropic API

```bash
# Copy example config
cp .env.example .env

# Edit .env and set your API key
# ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
```

Get your API key from [console.anthropic.com](https://console.anthropic.com/)

#### Option B: Using Claude Code CLI (Recommended)

```bash
# 1. Install Claude Code CLI
# Follow instructions at https://claude.ai/download

# 2. Authenticate Claude CLI
claude auth

# 3. Copy example config
cp .env.example .env

# 4. Edit .env and set API key to all 9s (triggers CLI routing)
# ANTHROPIC_API_KEY=999999999999999999999999999999999999999999999999
```

This routes all API calls to your local Claude Code CLI, using your Max subscription with no per-token costs.

### Initialize Database

```bash
# Run database migrations
alembic upgrade head

# Verify database created
ls -la kosmos.db
```

### Verify Installation

Confirm your installation is working correctly:

```bash
# Check system status
kosmos doctor

# Expected output:
# Python version 3.11+ detected
# All required packages installed
# API key configured (Anthropic/OpenAI)
# Database accessible
# Cache directory writable

# View version and configuration
kosmos version

# Expected output:
# Kosmos v0.2.0
# Python 3.11.x
# LLM Provider: anthropic (or openai)
# Status: Ready

# Quick system info
kosmos info

# Shows configuration, cache status, API key status, enabled domains
```

System is operational when all checks pass.

### Run Your First Research Project

#### Using the CLI

```bash
# Interactive mode with guided prompts
kosmos run --interactive

# Or provide a question directly
kosmos run "What is the relationship between sleep deprivation and memory consolidation?" \
  --domain neuroscience \
  --max-iterations 5

# Monitor progress in another terminal
kosmos status <run_id> --watch

# View research history
kosmos history --limit 10
```

#### Using Python API

```python
from kosmos import ResearchDirectorAgent

# Initialize the research director
director = ResearchDirectorAgent()

# Pose a research question
question = "What is the relationship between sleep deprivation and memory consolidation?"

# Run autonomous research
results = director.conduct_research(
    question=question,
    domain="neuroscience",
    max_iterations=5
)

# View results
print(results.summary)
print(results.key_findings)
```

## CLI Commands

Kosmos provides a command-line interface powered by [Typer](https://typer.tiangolo.com/) and [Rich](https://rich.readthedocs.io/).

### Core Commands

#### `kosmos run` - Execute Research

Run autonomous research on a scientific question:

```bash
# Interactive mode (guided prompts)
kosmos run --interactive

# Direct mode with options
kosmos run "Your research question here" \
  --domain biology \
  --max-iterations 10 \
  --budget 50 \
  --output results.json

# Options:
#   --interactive          Launch interactive configuration mode
#   --domain TEXT          Scientific domain (biology, neuroscience, etc.)
#   --max-iterations INT   Maximum research iterations (default: 10)
#   --budget FLOAT         Budget limit in USD
#   --no-cache            Disable caching
#   --output PATH         Export results (JSON or Markdown)
```

#### `kosmos status` - Monitor Research

View research run status and progress:

```bash
# Show current status
kosmos status run_12345

# Watch mode (live updates every 5 seconds)
kosmos status run_12345 --watch

# Detailed view
kosmos status run_12345 --details

# Options:
#   --watch, -w    Live status updates
#   --details, -d  Show detailed information
```

#### `kosmos history` - Browse Past Research

Browse and search research history:

```bash
# Show recent runs
kosmos history

# Filter by domain
kosmos history --domain neuroscience --limit 20

# Filter by status
kosmos history --status completed --days 7

# Detailed view
kosmos history --details

# Options:
#   --limit INT     Number of runs to show (default: 10)
#   --domain TEXT   Filter by scientific domain
#   --status TEXT   Filter by state (completed, running, failed)
#   --days INT      Show runs from last N days
#   --details       Show detailed information for each run
```

#### `kosmos cache` - Manage Caching

View cache statistics and manage cached data:

```bash
# Show cache statistics
kosmos cache --stats

# Health check
kosmos cache --health

# Optimize (cleanup expired entries)
kosmos cache --optimize

# Clear specific cache
kosmos cache --clear-type claude

# Clear all caches
kosmos cache --clear

# Options:
#   --stats, -s           Show cache statistics
#   --health, -h          Run health check
#   --optimize, -o        Optimize and cleanup caches
#   --clear, -c           Clear all caches (requires confirmation)
#   --clear-type TEXT     Clear specific cache type
```

### Utility Commands

#### `kosmos config` - Configuration Management

View and validate configuration:

```bash
# Show current configuration
kosmos config --show

# Validate configuration
kosmos config --validate

# Show config file locations
kosmos config --path

# Options:
#   --show, -s       Display current configuration
#   --validate, -v   Validate configuration and check requirements
#   --path, -p       Show configuration file paths
```

#### `kosmos doctor` - System Diagnostics

Run diagnostic checks:

```bash
kosmos doctor

# Checks:
#   - Python version
#   - Required packages
#   - API key configuration
#   - Cache directory permissions
#   - Database connectivity
```

#### `kosmos version` - Version Information

Show version and system information:

```bash
kosmos version

# Displays:
#   - Kosmos version
#   - Python version
#   - Platform information
#   - LLM provider and SDK version
```

#### `kosmos info` - System Status

Show system status and configuration:

```bash
kosmos info

# Displays:
#   - Configuration settings
#   - Cache status and size
#   - API key status
#   - Enabled domains
```

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                          CLI Layer                              │
│  (Typer + Rich: Interactive UI, Commands, Progress)            │
└─────────────────────┬──────────────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────────────┐
│                    Research Director                            │
│  (Orchestrates workflow, manages state, coordinates agents)    │
└───┬───────────┬───────────┬──────────────┬───────────┬─────────┘
    │           │           │              │           │
    ▼           ▼           ▼              ▼           ▼
┌────────┐ ┌────────┐ ┌──────────┐ ┌─────────┐ ┌───────────────┐
│Hypoth  │ │Experi  │ │   Data   │ │Litera   │ │  Other        │
│esis    │ │ment    │ │ Analyst  │ │ture     │ │  Specialized  │
│Generat │ │Designer│ │          │ │Analyzer │ │  Agents       │
└────┬───┘ └────┬───┘ └────┬─────┘ └────┬────┘ └───────┬───────┘
     │          │          │             │             │
     └──────────┴──────────┴─────────────┴─────────────┘
                           │
          ┌────────────────┴────────────────────┐
          │                                     │
      ┌───▼───────┐                    ┌────────▼──────┐
      │ LLM Client│                    │   Execution   │
      │Multi-Provider│                 │    Engine     │
      └───┬───────┘                    └────────┬──────┘
          │                                     │
      ┌───▼──────────────┐              ┌──────▼────────┐
      │  Cache Manager   │              │Docker Sandbox │
      │ (30%+ savings)   │              │ (Code Safety) │
      └──────────────────┘              └───────────────┘
                           │
          ┌────────────────┴──────────────────┐
          │                                   │
      ┌───▼──────┐                    ┌───────▼─────┐
      │Neo4j KB  │                    │SQLite/Postgres│
      │  Graph   │                    │   Database    │
      └──────────┘                    └───────────────┘
```

### Core Components

- **CLI Layer**: Terminal UI with Rich and Typer for interactive research
- **Research Director**: Master orchestrator managing research workflow
- **Literature Analyzer**: Searches and analyzes scientific papers (arXiv, Semantic Scholar, PubMed)
- **Hypothesis Generator**: Uses configured LLM to generate testable hypotheses
- **Experiment Designer**: Designs computational experiments
- **Execution Engine**: Runs experiments using proven statistical methods
- **Data Analyst**: Interprets results using configured LLM
- **Cache Manager**: Multi-tier caching system for cost optimization
- **Feedback Loop**: Iteratively refines hypotheses based on results

## Anthropic Usage Modes

*For setup instructions for OpenAI, Ollama, OpenRouter, and LM Studio, see [Provider Setup Guide](docs/providers/README.md)*

### Mode 1: Claude Code CLI (Max Subscription)

**Pros:**
- No per-token costs
- Unlimited usage
- Latest Claude model
- Local execution

**Cons:**
- Requires Claude CLI installation
- Requires Max subscription

**Setup:**
```bash
pip install -e ".[router]"
# Set ANTHROPIC_API_KEY=999999999999999999999999999999999999999999999999
```

### Mode 2: Anthropic API

**Pros:**
- Pay-as-you-go
- No CLI installation needed
- Works anywhere

**Cons:**
- Per-token costs
- Rate limits apply

**Setup:**
```bash
# Set ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

## Configuration

All configuration is via environment variables (see `.env.example`):

### LLM Provider Settings
- `LLM_PROVIDER`: Provider to use (`anthropic` or `openai`, default: `anthropic`)

### Anthropic Settings (when LLM_PROVIDER=anthropic)
- `ANTHROPIC_API_KEY`: API key or `999...` for CLI mode
- `CLAUDE_MODEL`: Model to use (default: `claude-3-5-sonnet-20241022`)
- `CLAUDE_MAX_TOKENS`: Max tokens per request (default: 4096)
- `CLAUDE_TEMPERATURE`: Sampling temperature 0.0-1.0 (default: 0.7)
- `CLAUDE_ENABLE_CACHE`: Enable prompt caching (default: true)

### OpenAI Settings (when LLM_PROVIDER=openai)
- `OPENAI_API_KEY`: OpenAI API key (required)
- `OPENAI_MODEL`: Model name (default: `gpt-4-turbo`)
- `OPENAI_MAX_TOKENS`: Max tokens per request (default: 4096)
- `OPENAI_TEMPERATURE`: Sampling temperature 0.0-2.0 (default: 0.7)
- `OPENAI_BASE_URL`: Custom base URL for compatible APIs (optional, for Ollama/OpenRouter/LM Studio)
- `OPENAI_ORGANIZATION`: OpenAI organization ID (optional)

### Core Settings
- `DATABASE_URL`: Database connection string
- `LOG_LEVEL`: Logging verbosity

### Research Settings
- `MAX_RESEARCH_ITERATIONS`: Max autonomous iterations
- `ENABLED_DOMAINS`: Which scientific domains to support
- `ENABLED_EXPERIMENT_TYPES`: Types of experiments allowed
- `MIN_NOVELTY_SCORE`: Minimum novelty threshold

### Safety Settings
- `ENABLE_SAFETY_CHECKS`: Code safety validation
- `MAX_EXPERIMENT_EXECUTION_TIME`: Timeout for experiments
- `ENABLE_SANDBOXING`: Sandbox code execution
- `REQUIRE_HUMAN_APPROVAL`: Manual approval gates

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=kosmos --cov-report=html

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

### Code Quality

```bash
# Format code
black kosmos/ tests/

# Lint
ruff check kosmos/ tests/

# Type check
mypy kosmos/
```

### Project Structure

```
kosmos/
├── core/           # Core infrastructure (LLM, config, logging)
├── agents/         # Agent implementations
├── db/             # Database models and operations
├── execution/      # Experiment execution engine
├── analysis/       # Result analysis and visualization
├── hypothesis/     # Hypothesis generation and management
├── experiments/    # Experiment templates
├── literature/     # Literature search and analysis
├── knowledge/      # Knowledge graph and semantic search
├── domains/        # Domain-specific tools (biology, physics, etc.)
├── safety/         # Safety checks and validation
└── cli/            # Command-line interface

tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
└── e2e/            # End-to-end tests

docs/
├── kosmos-figures-analysis.md  # Analysis patterns from kosmos-figures
├── integration-plan.md         # Integration strategy
└── domain-roadmaps/            # Domain-specific guides
```

## Documentation

- [Architecture Overview](docs/architecture.md) - System design and components
- [Integration Plan](docs/integration-plan.md) - How we integrate kosmos-figures patterns
- [Domain Roadmaps](docs/domain-roadmaps/) - Domain-specific implementation guides
- [API Reference](docs/api/) - API documentation
- [Contributing Guide](CONTRIBUTING.md) - How to contribute

## Development History

Kosmos was developed in 10 phases from November 2024, currently in end-to-end testing:

### Phase 0-1: Foundation
- Project structure and repository setup
- Claude integration (API + CLI routing)
- Configuration system with Pydantic validation
- Agent framework and base classes
- Database setup (SQLite/PostgreSQL with Alembic migrations)

### Phase 2: Knowledge & Literature
- Literature APIs: arXiv, Semantic Scholar, PubMed integration
- Literature analyzer agent with citation tracking
- Vector database (ChromaDB) for semantic search
- Neo4j knowledge graph for concept relationships

### Phase 3: Hypothesis Generation
- Hypothesis generator agent powered by Claude Sonnet 4
- Novelty checking against existing literature
- Hypothesis prioritization and ranking

### Phase 4: Experimental Design
- Experiment designer agent for protocol generation
- Validated experiment templates from kosmos-figures
- Resource estimation and feasibility analysis

### Phase 5: Execution
- Sandboxed execution environment with Docker
- Integration of kosmos-figures analysis patterns
- Statistical analysis methods (t-tests, ANOVA, regression)

### Phase 6: Analysis & Interpretation
- Data analyst agent for result interpretation
- Automated visualization generation (matplotlib, seaborn, plotly)
- Result summarization and insight extraction

### Phase 7: Iterative Learning
- Research director agent orchestrating workflow
- Feedback loops for hypothesis refinement
- Convergence detection and stopping criteria

### Phase 8: Safety & Validation
- Safety validation and code analysis
- Sandboxing and execution limits
- Reproducibility checks and validation

### Phase 9: Multi-Domain Support
- Domain-specific tools: Biology, neuroscience, physics, chemistry, materials science
- API integrations: KEGG, UniProt, Materials Project, FlyWire
- Domain-specific experiment templates

### Phase 10: Testing & Deployment
- Test suite development (requirements traceability matrix in progress)
- Performance optimizations (20-40x in specific operations: parallel execution, caching)
- Docker and Kubernetes deployment infrastructure
- Health monitoring with Prometheus metrics
- Documentation across user guides, API references, deployment procedures

[View Detailed Phase Reports](docs/phase-reports/) | [Implementation Plan](IMPLEMENTATION_PLAN.md)

## Based On

This project is inspired by:
- **Paper**: [Kosmos: An AI Scientist for Autonomous Discovery](https://arxiv.org/pdf/2511.02824) (Nov 2025)
- **Analysis Patterns**: [kosmos-figures repository](https://github.com/EdisonScientific/kosmos-figures)
- **Claude Router**: [claude_n_codex_api_proxy](https://github.com/jimmc414/claude_n_codex_api_proxy)

## Contributing

Contributions are accepted. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas We Need Help

- Domain-specific tools and APIs
- Experiment templates for different domains
- Literature API integrations
- Safety validation
- Documentation
- Testing

## Open Implementation Questions

Kosmos v0.2.0 implements the full autonomous research cycle, but several critical architectural challenges remain unsolved. We've documented these gaps and are seeking community input.

### Critical Gaps

**Gap 0: Context Compression Architecture** - How to compress accumulated research state across 200+ agent rollouts while preserving causal relationships and enabling coherent task planning.

**Gap 1: State Manager Schema & Query Design** - Data structure and indexing strategy for sub-second context retrieval with 200+ concurrent agent accesses while maintaining referential integrity.

**Gap 2: Task Generation Strategy** - Synthesis mechanism for identifying discovery narratives from accumulated findings and proposing high-value next tasks.

For detailed technical analysis including severity assessments, implementation roadmap, and risk analysis, see [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md).

### Seeking Expertise In:

- Large-scale knowledge graph query optimization
- Incremental summarization with provenance preservation
- Multi-agent task coordination patterns
- Production Neo4j deployment at scale

**Contribute:** [GitHub Issues](https://github.com/jimmc414/Kosmos/issues) | [Discussions](https://github.com/jimmc414/Kosmos/discussions)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Citation

If you use Kosmos in your research, please cite:

```bibtex
@software{kosmos_ai_scientist,
  title={Kosmos AI Scientist: Multi-Provider Autonomous Scientific Discovery},
  author={Kosmos Contributors},
  year={2025},
  url={https://github.com/jimmc414/Kosmos}
}
```

## Acknowledgments

- **Anthropic** for Claude and Claude Code CLI
- **OpenAI** for GPT models and API
- **Ollama** for local model infrastructure
- **Edison Scientific** for kosmos-figures analysis patterns
- **Open science community** for literature APIs and tools

## Troubleshooting

### "Database fails" Error

If `kosmos doctor` shows database issues:

```bash
# Check Docker containers are running
docker-compose ps

# Should show all services as "Up (healthy)"
# If not, restart services:
docker-compose restart neo4j postgres redis

# Re-run diagnostics
kosmos doctor
```

Note: Minor warnings about missing indexes are expected and do not block functionality. See issues [#7](https://github.com/jimmc414/Kosmos/issues/7) and [#11](https://github.com/jimmc414/Kosmos/issues/11) for known database-related issues.

### "Sandbox errors" When Running Experiments

If experiments fail with Docker/sandbox errors:

```bash
# Rebuild sandbox image with latest dependencies
docker build -t kosmos-sandbox:latest docker/sandbox/

# Verify image exists
docker images | grep kosmos-sandbox

# Test sandbox
docker run --rm kosmos-sandbox:latest python3 --version
```

### "Neo4j connection" Issues

If knowledge graph features fail:

```bash
# Check Neo4j is running
docker logs kosmos-neo4j

# Restart Neo4j if needed
docker-compose restart neo4j

# Verify Neo4j is accessible
curl http://localhost:7474  # Should return HTTP 200

# Access Neo4j browser (optional)
# Open http://localhost:7474 in browser
# Login: neo4j / kosmos-password
```

### "Import errors" for Advanced Analytics

If you see `ModuleNotFoundError` for new features:

```bash
# Reinstall with latest dependencies
pip install -e . --upgrade

# Verify advanced analytics packages
pip list | grep -E "shap|gseapy|pwlf|nbformat"

# Should show:
# gseapy       1.1.11
# shap         0.49.1
# pwlf         2.5.2
# nbformat     5.10.4
```

### More Help

- New users: See [Quick Start Guide](docs/setup/QUICK_START.md)
- Upgrading: See [Upgrade Guide](docs/setup/UPGRADE_GUIDE.md)
- Bug reports: Open an [issue](https://github.com/jimmc414/Kosmos/issues) with `kosmos doctor` output and known issues ([#7](https://github.com/jimmc414/Kosmos/issues/7), [#11](https://github.com/jimmc414/Kosmos/issues/11))

## Support

- **Issues**: [GitHub Issues](https://github.com/jimmc414/Kosmos/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jimmc414/Kosmos/discussions)

---

Version: v0.2.0
Development: All 10 phases implemented (Phase 0-10)
Status: End-to-end testing, pre-production validation
Test Coverage: Under development (requirements traceability matrix in progress)
Performance: 20-40x improvement in specific operations relative to baseline
Release Date: 2025-11-13

Recent milestones:
- Phase 10 implementation tasks completed
- Multi-provider support implemented (Anthropic, OpenAI, Ollama, OpenRouter, LM Studio)
- Deployment infrastructure implemented (Docker, Kubernetes, health monitoring, Prometheus metrics)
- Test suite expansion in progress
- Performance optimizations deployed (parallel execution, caching, optimization)
- Documentation completed (user guides, API references, deployment procedures)

Known issues being addressed: [#7](https://github.com/jimmc414/Kosmos/issues/7), [#11](https://github.com/jimmc414/Kosmos/issues/11)

[View All Phase Reports](docs/phase-reports/) | [Implementation Plan](IMPLEMENTATION_PLAN.md)

Last Updated: 2025-11-20
