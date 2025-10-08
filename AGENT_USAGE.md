# Multi-Agent Code Generation - Quick Usage Guide

## 🚀 Quick Start (2 minutes)

### 1. Setup

```bash
cd backend
pip install -r requirements-agents.txt
export ANTHROPIC_API_KEY=your_key_here
```

### 2. Test

```bash
# Generate code from a paper
python test_agent_system.py --paper-id 2010.11929

# View results
ls test_outputs/2010_11929_code/
```

### 3. Done!

You now have:
- ✅ Working implementation in `model.py`
- ✅ Hyperparameters in `config.py`
- ✅ Example usage in `example.py`
- ✅ Tests in the system
- ✅ README with documentation

---

## 📖 Common Usage Patterns

### Pattern 1: Research → Implementation

**Use case**: You found an interesting paper and want working code

```bash
# Step 1: Find paper on arXiv
# Example: https://arxiv.org/abs/2010.11929 (CLIP)

# Step 2: Extract paper ID (2010.11929)

# Step 3: Generate code
python test_agent_system.py --paper-id 2010.11929

# Step 4: Use generated code
cd test_outputs/2010_11929_code/
python example.py
```

**Expected time**: 60-120 seconds

### Pattern 2: Compare Multiple Approaches

**Use case**: Compare different papers/methods for your problem

```bash
# Generate implementations for competing approaches
python test_agent_system.py --paper-id 2010.11929  # CLIP
python test_agent_system.py --paper-id 2106.09685  # LoRA
python test_agent_system.py --paper-id 2304.10592  # LLaVA

# Compare generated code in test_outputs/
```

### Pattern 3: Benchmark Papers

**Use case**: Test system performance on multiple papers

```bash
# Run built-in benchmark
python test_agent_system.py --benchmark

# Or create custom benchmark
python -c "
import asyncio
from test_agent_system import run_benchmark

papers = ['2010.11929', '2106.09685', '2303.08774']
asyncio.run(run_benchmark(papers))
"
```

### Pattern 4: API Integration

**Use case**: Generate code from your web app

```bash
# Start server
uvicorn app.main:app --reload

# Call from your frontend
fetch('http://localhost:8000/api/v1/papers/2010.11929/generate-code', {
  method: 'POST'
})
.then(r => r.json())
.then(result => {
  console.log('Code:', result.code.main);
  console.log('Tests passed:', result.tests.passed);
});
```

### Pattern 5: Custom Agent Workflow

**Use case**: Fine-grained control over generation

```python
import asyncio
from app.agents import (
    get_orchestrator,
    PaperAnalyzerAgent,
    TestDesignerAgent,
    CodeGeneratorAgent
)
from app.agents.config import orchestrator_config

async def custom_generation():
    # Get agents
    config = orchestrator_config.agent_config
    memory = get_orchestrator().memory

    analyzer = PaperAnalyzerAgent(config, memory)
    test_designer = TestDesignerAgent(config, memory)
    code_gen = CodeGeneratorAgent(config, memory)

    # Custom workflow
    analysis = await analyzer.execute(
        paper_title="My Paper",
        paper_abstract="...",
        paper_summary={},
        paper_category="cs.AI"
    )

    tests = await test_designer.execute(
        analysis=analysis,
        paper_title="My Paper",
        paper_domain="cs.AI"
    )

    code = await code_gen.execute(
        analysis=analysis,
        test_suite=tests,
        paper_title="My Paper"
    )

    return code

result = asyncio.run(custom_generation())
```

---

## 🎯 Best Practices

### Choosing Papers

**✅ Good candidates:**
- Papers with clear algorithms
- Implementation-focused papers
- Moderate complexity (5-7/10)
- Recent papers (2020+)
- Papers with pseudocode

**❌ Difficult papers:**
- Purely theoretical
- Require proprietary datasets
- Need expensive compute (e.g., requires 100 GPUs)
- Too complex (9-10/10 complexity)

### Interpreting Results

**100% success (`tests_passed === tests_total`):**
- Code is likely production-ready
- Tests verify core functionality
- Review code for your specific use case

**80-99% success:**
- Core algorithm works
- Some edge cases may fail
- Review failed tests in output
- Often good enough for prototyping

**<80% success:**
- Partial implementation
- May need manual fixes
- Check `debug_iterations` and `stderr`
- Consider simpler paper or re-run

### Working with Generated Code

```bash
# 1. Review generated code
cd test_outputs/2010_11929_code/
cat model.py

# 2. Check hyperparameters
cat config.py

# 3. Run example
python example.py

# 4. Run tests (if you have pytest)
pip install pytest
pytest  # Note: tests run during generation, this re-runs them

# 5. Customize for your use case
# Edit model.py, config.py as needed
```

### Handling Failures

If generation fails:

```bash
# 1. Run with verbose output
python test_agent_system.py --paper-id YOUR_ID --verbose

# 2. Check the results JSON
cat test_outputs/YOUR_ID_result.json

# 3. Review stderr
grep -A 10 "stderr" test_outputs/YOUR_ID_result.json

# 4. Try simpler paper first
python test_agent_system.py --paper-id 2106.09685  # LoRA is simpler
```

---

## 🔧 Configuration Examples

### Fast Generation (Speed Priority)

```python
# In app/agents/config.py

class AgentConfig(BaseModel):
    temperature: float = 0.5           # Lower = faster
    max_tokens: int = 2000            # Shorter responses
    timeout_seconds: int = 20         # Faster timeout

class OrchestratorConfig(BaseModel):
    max_debug_iterations: int = 1     # Don't debug much
    enable_reflection: bool = False   # Skip learning
```

**Expected speedup**: 30-40% faster (~40-70s per paper)

### High Quality (Quality Priority)

```python
# In app/agents/config.py

class AgentConfig(BaseModel):
    llm_model: str = "claude-opus-4-20250514"  # Most capable
    temperature: float = 0.7
    max_tokens: int = 8000            # Detailed responses
    timeout_seconds: int = 60         # More test time

class OrchestratorConfig(BaseModel):
    max_debug_iterations: int = 5     # Try harder
    enable_reflection: bool = True    # Learn from attempts
```

**Expected impact**: Higher success rate, 50-100% slower

### Balanced (Default)

```python
# Current defaults are balanced for production
llm_model: str = "claude-sonnet-4-20250514"
temperature: float = 0.7
max_tokens: int = 4000
max_debug_iterations: int = 3
```

---

## 📊 Example Outputs

### Successful Generation

```bash
$ python test_agent_system.py --paper-id 2010.11929

================================================================================
🧪 Testing Multi-Agent Code Generation System
================================================================================

📄 Step 1: Fetching paper 2010.11929 from arXiv...
✅ Found: Learning Transferable Visual Models From Natural Language...
   Authors: Alec Radford, Jong Wook Kim, Chris Hallacy...
   Category: cs.CV

🤖 Step 2: Generating AI analysis...
✅ AI analysis complete

🎭 Step 3: Initializing multi-agent orchestrator...
✅ Orchestrator ready with 5 agents

💻 Step 4: Generating code (this may take 60-120 seconds)...
   Pipeline: Analyze → Design Tests → Generate Code → Execute → Debug

================================================================================
📊 RESULTS
================================================================================

✅ SUCCESS - All tests passing!

⏱️  Total Time: 87.3s
🔄 Debug Iterations: 1

🧪 Tests:
   Total: 15
   Passed: 15
   Failed: 0

💾 Generated Code:
   Main code: 2847 chars
   Config: 891 chars
   Framework: pytorch
   Dependencies: torch, transformers, numpy, pillow

💾 Results saved to: test_outputs/2010_11929_result.json
💾 Code saved to: test_outputs/2010_11929_code/
```

### Partial Success

```bash
================================================================================
📊 RESULTS
================================================================================

⚠️  PARTIAL SUCCESS - Some tests failed

⏱️  Total Time: 134.7s
🔄 Debug Iterations: 3

🧪 Tests:
   Total: 18
   Passed: 15
   Failed: 3

💾 Generated Code:
   Main code: 3241 chars
   Config: 1024 chars
   Framework: pytorch
   Dependencies: torch, einops, transformers
```

---

## 🎓 Advanced Usage

### Custom Prompts

Edit agent prompts in `backend/app/agents/`:

```python
# In paper_analyzer.py
def _get_system_prompt(self) -> str:
    return """You are an expert at analyzing ML papers.

Your approach:
1. Extract the core algorithm
2. Identify implementation challenges
3. Predict common bugs

[Add your custom instructions here]
"""
```

### Agent Subclassing

Create specialized agents:

```python
from app.agents.base import BaseAgent

class CustomPaperAnalyzer(BaseAgent):
    """Specialized analyzer for NLP papers"""

    def _get_system_prompt(self) -> str:
        return """Expert in NLP papers..."""

    async def execute(self, **kwargs):
        # Custom analysis logic
        pass
```

### Memory Integration

Access temporal memory:

```python
from app.agents import get_orchestrator

orchestrator = get_orchestrator()
memory = orchestrator.memory

# Store custom reflection
await memory.add_reflection(
    agent="MyAgent",
    reflection="Learned that attention mechanisms need careful initialization",
    task_type="code_generation",
    context={"paper_type": "transformer"}
)

# Retrieve learnings
learnings = await memory.get_reflections(
    agent="MyAgent",
    task_type="code_generation",
    max_age_days=30
)
```

---

## 💡 Tips & Tricks

### Tip 1: Batch Processing

Generate code for multiple papers overnight:

```bash
# Create batch script
cat > batch_generate.sh << 'EOF'
#!/bin/bash
for paper_id in 2010.11929 2106.09685 2303.08774; do
  echo "Processing $paper_id..."
  python test_agent_system.py --paper-id $paper_id
  sleep 10  # Rate limiting
done
EOF

chmod +x batch_generate.sh
./batch_generate.sh
```

### Tip 2: Filter by Success Rate

```python
import json
from pathlib import Path

# Find successful generations
outputs = Path("test_outputs")
for result_file in outputs.glob("*_result.json"):
    with open(result_file) as f:
        result = json.load(f)
        if result["success"]:
            print(f"✅ {result['paper_id']}: {result['paper_title']}")
```

### Tip 3: Code Diff for Similar Papers

Compare implementations of related papers:

```bash
# Generate code for two similar papers
python test_agent_system.py --paper-id 2010.11929  # CLIP
python test_agent_system.py --paper-id 2304.10592  # LLaVA

# Compare implementations
diff test_outputs/2010_11929_code/model.py \
     test_outputs/2304_10592_code/model.py
```

### Tip 4: Template for Your Domain

Generate once, then use as template:

```bash
# Generate from representative paper
python test_agent_system.py --paper-id YOUR_DOMAIN_PAPER

# Use as starting point for similar papers
cp -r test_outputs/YOUR_PAPER_code/ my_template/
# Edit my_template/ to generalize
```

---

## 🆘 Quick Troubleshooting

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: anthropic` | `pip install anthropic` |
| `API key not found` | `export ANTHROPIC_API_KEY=your_key` |
| `Test timeout` | Increase `timeout_seconds` in config |
| `All tests failed` | Check paper complexity, try `--verbose` |
| `Out of memory` | Reduce `max_tokens` in config |
| Generation too slow | Reduce `max_debug_iterations`, disable reflection |
| Success rate low | Increase `max_debug_iterations`, use Opus model |

---

## 📚 See Also

- **AGENT_SETUP.md**: Detailed setup and configuration guide
- **AGENT_SYSTEM_STATUS.md**: Architecture and research details
- **backend/app/agents/**: Agent source code

---

## ✨ Examples

### Example 1: CLIP Implementation

```bash
python test_agent_system.py --paper-id 2010.11929
cd test_outputs/2010_11929_code/
cat example.py
```

Generated code:
```python
from model import CLIPModel
from config import CLIPConfig

# Initialize model
config = CLIPConfig(
    embed_dim=512,
    image_resolution=224,
    vision_layers=12,
    text_context_length=77
)
model = CLIPModel(config)

# Use for zero-shot classification
image = load_image("cat.jpg")
text = ["a cat", "a dog", "a bird"]
logits = model(image, text)
print(f"Predictions: {logits.softmax(dim=-1)}")
```

### Example 2: LoRA Fine-tuning

```bash
python test_agent_system.py --paper-id 2106.09685
cd test_outputs/2106_09685_code/
cat example.py
```

Generated code:
```python
from model import LoRALinear
from config import LoRAConfig

# Add LoRA to existing model
config = LoRAConfig(rank=4, alpha=32)
lora_layer = LoRALinear(
    in_features=768,
    out_features=768,
    config=config
)

# Use as drop-in replacement for nn.Linear
output = lora_layer(input)
```

---

**That's it! You're ready to turn any AI paper into working code. 🚀**
