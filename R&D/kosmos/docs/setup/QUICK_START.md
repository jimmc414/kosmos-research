# Kosmos AI Scientist - Quick Start Guide

**For New Users** | Get up and running in 10 minutes

---

## Prerequisites

Before installing Kosmos, ensure you have:

- ✅ **Python 3.11 or 3.12** (`python --version`)
- ✅ **Docker** installed and running (`docker --version`)
- ✅ **Git** for cloning the repository
- ✅ **4GB+ RAM** available for Docker containers
- ✅ **Anthropic API key** (sign up at https://console.anthropic.com/)

### Quick Prerequisites Check

```bash
# Check Python version
python --version  # Should show 3.11 or 3.12

# Check Docker
docker --version
docker ps  # Should list running containers without error

# Check available memory
free -h  # Linux
# or
vm_stat  # macOS
```

---

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/jimmc414/Kosmos.git
cd Kosmos
```

### 2. Install Kosmos

```bash
# Install in editable mode with all dependencies
pip install -e .

# This installs:
# - Core Kosmos package
# - All required Python libraries
# - Advanced analytics (SHAP, gseapy, pwlf)
# - Jupyter notebook support
# - Scientific computing stack
```

**Installation time**: ~2-3 minutes (depending on internet speed)

### 3. Configure Environment

```bash
# Create .env file from template
cp .env.example .env

# Edit .env and add your API key
nano .env  # or use your preferred editor
```

Add to `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...your-key-here...
```

**Save and close the file.**

### 4. Start Services

Kosmos requires three backend services: Neo4j (knowledge graph), PostgreSQL (database), and Redis (caching).

```bash
# Start all services in the background
docker-compose up -d neo4j postgres redis

# Wait ~30 seconds for services to initialize
```

**Verify services are running:**
```bash
docker-compose ps

# Should show:
# NAME              STATUS
# kosmos-neo4j      Up (healthy)
# kosmos-postgres   Up (healthy)
# kosmos-redis      Up (healthy)
```

### 5. Build Sandbox Image (Optional but Recommended)

For safe code execution in isolated containers:

```bash
# Build the sandbox Docker image
docker build -t kosmos-sandbox:latest docker/sandbox/

# This includes all scientific libraries needed for analysis
```

**Build time**: ~3-5 minutes (one-time setup)

---

## Verification

### Run Diagnostics

```bash
kosmos doctor
```

**Expected output** (all PASS):
```
                    Diagnostic Results
╭─────────────────────┬─────────────────────────┬────────╮
│ Check               │ Status                  │ Result │
├─────────────────────┼─────────────────────────┼────────┤
│ Python Version      │ 3.11                    │ ✓ PASS │
│ Package: anthropic  │ Installed               │ ✓ PASS │
│ Package: numpy      │ Installed               │ ✓ PASS │
│ Package: pandas     │ Installed               │ ✓ PASS │
│ Package: scipy      │ Installed               │ ✓ PASS │
│ Anthropic API Key   │ Configured              │ ✓ PASS │
│ Cache Directory     │ /home/user/.kosmos_cache│ ✓ PASS │
│ Database Connection │ Connected               │ ✓ PASS │
│ Database Schema     │ Complete                │ ✓ PASS │
╰─────────────────────┴─────────────────────────┴────────╯
```

### Test Components

```bash
# Test Data Analysis Agent
python -c "from kosmos.execution.data_analysis import DataAnalyzer; print('Data Analysis: OK')"

# Test Literature Agent
python -c "from kosmos.agents.literature_analyzer import get_literature_analyzer; print('Literature Agent: OK')"

# Test World Model
python -c "from kosmos.world_model import get_world_model; wm = get_world_model(); print(f'World Model: OK - {wm.get_statistics()}'); "
```

**All three should print "OK" without errors.**

---

## First Research Query

Now you're ready to run your first autonomous research cycle!

```bash
# Run a simple research query
kosmos research "How do neural networks learn long-range dependencies?"

# Kosmos will:
# 1. Search scientific literature (arXiv, PubMed, Semantic Scholar)
# 2. Generate hypotheses based on papers found
# 3. Design experiments to test hypotheses
# 4. Execute analyses in sandboxed environment
# 5. Interpret results using Claude
# 6. Store all findings in knowledge graph
# 7. Generate a research report
```

**Expected behavior:**
- Progress bar showing literature search
- Hypothesis generation with confidence scores
- Experiment execution with results
- Final report with cited sources

**Runtime**: 5-15 minutes (depending on query complexity)

---

## Common Commands

```bash
# View knowledge graph statistics
kosmos graph --stats

# Export knowledge graph for backup
kosmos graph --export my_research.json

# Import previously exported graph
kosmos graph --import my_research.json

# Run diagnostics anytime
kosmos doctor

# Get help
kosmos --help
```

---

## Troubleshooting

### "Database fails" Error

```bash
# Check Docker containers are running
docker-compose ps

# Restart services if needed
docker-compose restart

# Re-run diagnostics
kosmos doctor
```

### "Sandbox errors" When Running Experiments

```bash
# Rebuild sandbox image
docker build -t kosmos-sandbox:latest docker/sandbox/

# Verify image exists
docker images | grep kosmos-sandbox
```

### "Neo4j connection" Issues

```bash
# Check Neo4j is healthy
docker logs kosmos-neo4j

# Access Neo4j browser (optional)
# Open http://localhost:7474
# Login: neo4j / kosmos-password
```

### "Import errors" for Advanced Analytics

```bash
# Reinstall with latest dependencies
pip install -e . --upgrade

# Verify SHAP, gseapy, pwlf are installed
pip list | grep -E "shap|gseapy|pwlf"
```

---

## What's Next?

- 📖 **Read the docs**: `docs/user/world_model_guide.md`
- 🔬 **Try different domains**: Biology, physics, materials science
- 🧪 **Explore examples**: `examples/` directory
- 🛠️ **Customize**: Edit hypothesis templates, experiment protocols
- 📊 **Visualize**: Export data, generate publication plots
- 🌐 **Share**: Export knowledge graphs for collaboration

---

## Need Help?

- **Documentation**: `docs/` directory
- **GitHub Issues**: https://github.com/jimmc414/Kosmos/issues
- **Discord**: (Coming soon)
- **Email**: (See GitHub profile)

---

**Congratulations!** You're now running an autonomous AI scientist! 🎉

For upgrading an existing installation, see [UPGRADE_GUIDE.md](./UPGRADE_GUIDE.md).
