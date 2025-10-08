# Multi-Agent Code Generation System - Setup Guide

## 🎯 Overview

This system generates working code implementations from AI research papers using a multi-agent architecture based on the latest research (AgentCoder 2024, Reflexion 2023, SAGE 2024).

**What it does**: Takes any arXiv paper → produces working code + tests + documentation in 60-120 seconds.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Code Generation Orchestrator              │
│                                                              │
│  Pipeline: Analyze → Design Tests → Generate → Execute → Debug
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼─────────┐   ┌──────▼──────────┐
│ Paper Analyzer │   │  Test Designer   │   │ Code Generator  │
│                │   │                  │   │                 │
│ • Deep analysis│   │ • AI-designed    │   │ • TDD approach  │
│ • Failure pred │   │   tests (key!)   │   │ • Pass tests    │
│ • Reflection   │   │ • 4 test types   │   │ • Reflection    │
└────────────────┘   └──────────────────┘   └─────────────────┘
                              │
                 ┌────────────┼────────────┐
                 │                         │
        ┌────────▼──────────┐    ┌────────▼────────┐
        │  Test Executor    │    │    Debugger     │
        │                   │    │                 │
        │ • Sandbox exec    │    │ • Reflexion     │
        │ • Pytest parsing  │    │ • Max 3 iters   │
        │ • Safety          │    │ • Learning      │
        └───────────────────┘    └─────────────────┘
                              │
                 ┌────────────▼────────────┐
                 │   Temporal Memory       │
                 │                         │
                 │ • Reflections storage   │
                 │ • Success patterns      │
                 │ • Ebbinghaus decay      │
                 └─────────────────────────┘
```

## 📋 Prerequisites

- Python 3.9+
- Anthropic API key (Claude Sonnet 4)
- 4GB+ RAM recommended
- Optional: Neo4j for advanced memory (in-memory fallback available)

## 🚀 Installation

### Step 1: Install Dependencies

```bash
cd backend

# Install agent system dependencies
pip install -r requirements-agents.txt

# Or install individually:
pip install anthropic crewai pytest
```

### Step 2: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Add your API key
echo "ANTHROPIC_API_KEY=your_key_here" >> .env
```

Required environment variables:
```bash
ANTHROPIC_API_KEY=sk-ant-...        # Required
GEMINI_API_KEY=...                  # Already configured for AI analysis
MAX_PAPERS_PER_BATCH=5              # Already configured
```

### Step 3: Verify Installation

```bash
# Test imports
python -c "from app.agents import get_orchestrator; print('✅ Agents ready')"
```

## 🧪 Testing

### Option 1: Test Script (Recommended)

The easiest way to test the system:

```bash
# Test with a single paper
python test_agent_system.py --paper-id 2010.11929

# Test with verbose output
python test_agent_system.py --paper-id 2303.08774 --verbose

# Run benchmark on multiple papers
python test_agent_system.py --benchmark
```

**Recommended test papers:**
- `2010.11929` - CLIP (moderate complexity, ~60s)
- `2106.09685` - LoRA (low complexity, ~45s)
- `2303.08774` - GPT-4 (high complexity, ~120s)

**Output:**
- Results saved to `test_outputs/{paper_id}_result.json`
- Code files saved to `test_outputs/{paper_id}_code/`

### Option 2: API Endpoint

Start the API server:

```bash
# From backend directory
uvicorn app.main:app --reload --port 8000
```

Test the endpoint:

```bash
# Generate code for a paper
curl -X POST "http://localhost:8000/api/v1/papers/2010.11929/generate-code" \
  -H "Content-Type: application/json"
```

**Response format:**
```json
{
  "success": true,
  "generation_time": 87.3,
  "paper": {
    "id": "2010.11929",
    "title": "Learning Transferable Visual Models...",
    "analysis_summary": "Core algorithm: Contrastive learning..."
  },
  "code": {
    "main": "# model.py\nimport torch...",
    "config": "# config.py\nclass Config...",
    "utils": "# utils.py...",
    "example": "# example.py\nfrom model import...",
    "dependencies": ["torch", "transformers", ...],
    "framework": "pytorch"
  },
  "tests": {
    "total": 15,
    "passed": 14,
    "failed": 1,
    "execution_time": 2.3
  },
  "debug": {
    "iterations": 1,
    "total_attempts": 2
  },
  "readme": "# Quick Start Implementation\n\n...",
  "reflection": "Generation successful!\n- Paper complexity: 7/10..."
}
```

### Option 3: Python Integration

Use the system programmatically:

```python
import asyncio
from app.agents import get_orchestrator
from app.services.arxiv_service import arxiv_service
from app.services.ai_analysis_service import ai_analysis_service

async def generate_code_for_paper(paper_id: str):
    # Fetch paper
    paper = await arxiv_service.get_paper_by_id(paper_id)

    # Generate AI summary
    ai_summary = await ai_analysis_service.generate_comprehensive_analysis(
        paper['summary'],
        paper['title']
    )

    # Generate code
    orchestrator = get_orchestrator()
    result = await orchestrator.generate_quick_start(
        paper_title=paper['title'],
        paper_abstract=paper['summary'],
        paper_summary=ai_summary,
        paper_id=paper_id,
        paper_category=paper.get('category', 'cs.AI')
    )

    return result

# Run
result = asyncio.run(generate_code_for_paper("2010.11929"))
print(f"Success: {result.success}")
print(f"Code: {result.code.main_code[:200]}...")
```

## 📊 Understanding Results

### Success Metrics

- **success**: `true` = all tests passing, `false` = some tests failed
- **generation_time**: Total time in seconds (typically 60-120s)
- **debug_iterations**: Number of debugging cycles (0-3)
- **tests.passed/total**: Test success rate

### Code Quality Indicators

**Good signs:**
- ✅ All tests passing (`success: true`)
- ✅ 0-1 debug iterations
- ✅ Generation time < 90s
- ✅ 10+ tests created

**Needs review:**
- ⚠️ 2+ debug iterations (complex paper)
- ⚠️ Some tests failing (partial implementation)
- ⚠️ Generation time > 120s (very complex)

### Generated Files

```
test_outputs/
  2010_11929_code/
    ├── model.py         # Main implementation
    ├── config.py        # Hyperparameters from paper
    ├── utils.py         # Helper functions
    ├── example.py       # Quick start example
    └── README.md        # Documentation
```

## 🎛️ Configuration

### Agent Configuration

Edit `backend/app/agents/config.py`:

```python
class AgentConfig(BaseModel):
    llm_provider: str = "anthropic"
    llm_model: str = "claude-sonnet-4-20250514"  # Model to use
    temperature: float = 0.7                      # Creativity (0.0-1.0)
    max_tokens: int = 4000                       # Response length
    timeout_seconds: int = 30                    # Test execution timeout
```

### Memory Configuration

```python
class MemoryConfig(BaseModel):
    enable_memory: bool = True                   # Enable/disable learning
    max_reflections_per_agent: int = 100        # Memory capacity
    reflection_retention_days: int = 30         # How long to keep learnings
    use_neo4j: bool = False                     # Use Neo4j (or in-memory)
```

### Orchestrator Configuration

```python
class OrchestratorConfig(BaseModel):
    max_debug_iterations: int = 3               # Max debugging attempts
    parallel_agent_execution: bool = True       # Run agents in parallel
    enable_reflection: bool = True              # Enable learning
```

## 🐛 Troubleshooting

### Common Issues

**1. "ModuleNotFoundError: No module named 'anthropic'"**
```bash
pip install anthropic
```

**2. "API key not found"**
```bash
# Add to .env file
echo "ANTHROPIC_API_KEY=your_key_here" >> .env

# Or export directly
export ANTHROPIC_API_KEY=your_key_here
```

**3. "Test execution timeout"**

Increase timeout in config:
```python
# In app/agents/config.py
timeout_seconds: int = 60  # Increase from 30
```

**4. "Failed to install dependencies"**

The system tries to install paper dependencies. If this fails:
- Check your internet connection
- Try running test with `--verbose` to see error details
- Some papers require GPU libraries (torch+cuda) which may fail on CPU-only systems

**5. "All tests failed"**

This can happen for very complex papers. Check:
- `debug_iterations`: Should be attempting fixes
- `stderr` in results: Shows actual error
- Paper complexity: 8+/10 may not generate working code on first try

### Debug Mode

Enable verbose logging:

```python
# In your test script
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or use the test script with `--verbose`:

```bash
python test_agent_system.py --paper-id 2010.11929 --verbose
```

### Memory Issues

If you run out of memory:

```python
# In config.py
max_tokens: int = 2000  # Reduce from 4000
```

## 🔒 Security Notes

### Current Sandbox

The system uses **simple sandboxing** with temporary directories:
- ✅ Code runs in temp directories
- ✅ Subprocess isolation
- ✅ Timeout protection
- ⚠️ Not suitable for untrusted code in production

### Production Recommendations

For production deployment:

1. **Upgrade to Docker sandbox**
```python
# TODO: Implement in app/agents/test_executor.py
class DockerSandbox:
    """Run tests in isolated Docker containers"""
```

2. **Use E2B Code Interpreter**
```bash
pip install e2b-code-interpreter
# Provides secure, scalable sandboxing
```

3. **Rate limiting**
- Limit concurrent generations
- Queue system for multiple requests

4. **Resource limits**
- CPU/memory limits per execution
- Timeout enforcement

## 📈 Performance Optimization

### For Faster Generation

1. **Reduce test count**
```python
# In app/agents/test_designer.py
# Modify generate_tests() to create fewer tests
```

2. **Use GPT-4 for simple papers only**
```python
# In config.py
llm_model: str = "claude-sonnet-4-20250514"  # Fast
# vs
llm_model: str = "claude-opus-4-20250514"   # More capable but slower
```

3. **Disable reflection for speed**
```python
# In config.py
enable_reflection: bool = False  # 10-15% faster
```

4. **Parallel execution**
```python
# In config.py
parallel_agent_execution: bool = True  # Already enabled
```

### For Better Quality

1. **Increase max tokens**
```python
max_tokens: int = 8000  # More detailed code
```

2. **More debug iterations**
```python
max_debug_iterations: int = 5  # Try harder to fix
```

3. **Enable memory learning**
```python
enable_memory: bool = True  # Learn from past generations
```

## 🔄 Upgrading

### To Neo4j Memory (Optional)

For production-grade memory with temporal features:

```bash
# Install Neo4j
brew install neo4j  # macOS
# or use Docker
docker run -p 7474:7474 -p 7687:7687 neo4j

# Update config
# In app/agents/config.py
use_neo4j: bool = True
neo4j_uri: str = "bolt://localhost:7687"
neo4j_user: str = "neo4j"
neo4j_password: str = "your_password"
```

## 📚 Next Steps

1. **Test with your papers**: Try papers relevant to your domain
2. **Customize agents**: Modify prompts in `app/agents/*.py` for your use case
3. **Add to frontend**: Integrate the API endpoint into your UI
4. **Monitor performance**: Track success rates by paper complexity
5. **Contribute learnings**: Share successful patterns with the community

## 🆘 Support

If you encounter issues:

1. Check this guide's Troubleshooting section
2. Run with `--verbose` to see detailed logs
3. Check `test_outputs/` for generated code and results
4. Review agent logs for specific errors

## 🎓 Research References

This system is based on:

- **AgentCoder** (2024): Test-driven multi-agent programming
- **Reflexion** (2023): Verbal reinforcement learning for agents
- **SAGE** (2024): Self-evolving agents with memory
- **Graphiti** (2024): Temporal knowledge graphs

See `AGENT_SYSTEM_STATUS.md` for detailed research citations.
