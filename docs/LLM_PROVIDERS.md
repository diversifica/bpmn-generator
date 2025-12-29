# LLM Provider Configuration

## Overview

The BPMN Generator supports **multiple LLM providers** with a privacy-focused switch mechanism:

- **OpenAI** (cloud, requires API key)
- **Ollama** (local, privacy-first) ✅ **Recommended for sensitive data**
- **LMStudio** (local, future support)

## Quick Switch

### Option 1: Environment Variable
```bash
# .env file
LLM_PROVIDER=ollama  # or "openai" or "lmstudio"
```

### Option 2: Programmatic
```python
from bpmn_generator.utils.llm_provider import LLMProvider

# Use Ollama (local)
llm = LLMProvider.get_llm(provider="ollama", model="qwen2.5:32b")

# Use OpenAI (cloud)
llm = LLMProvider.get_llm(provider="openai", model="gpt-4o")
```

---

## Provider Details

### OpenAI (Cloud)

**When to use**: Maximum quality, no local GPU required

**Configuration**:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
```

**Installation**:
```bash
pip install -e .  # Already included
```

**Privacy**: ⚠️ Data sent to OpenAI servers

---

### Ollama (Local) ✅ **Privacy-First**

**When to use**: Sensitive data, no internet required, full privacy

**Prerequisites**:
1. Install Ollama: https://ollama.ai/download
2. Pull model: `ollama pull qwen2.5:32b`

**Configuration**:
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:32b
```

**Installation**:
```bash
pip install -e ".[local]"  # Installs langchain-ollama
```

**Recommended Models**:
- `qwen2.5:32b` - Best quality/speed balance (16GB VRAM)
- `llama3.1:70b` - Maximum quality (40GB+ VRAM)
- `deepseek-r1:32b` - Reasoning-focused (16GB VRAM)

**Privacy**: ✅ 100% local, no data leaves your machine

---

### LMStudio (Local) - Future Support

**When to use**: GUI-based local LLM management

**Configuration**:
```env
LLM_PROVIDER=lmstudio
LMSTUDIO_BASE_URL=http://localhost:1234/v1
LMSTUDIO_MODEL=your-model-name
```

**Installation**:
```bash
pip install -e .  # Uses OpenAI-compatible API
```

**Privacy**: ✅ 100% local

---

## Usage Examples

### Default (from .env)
```python
from bpmn_generator.utils.llm_provider import get_default_llm

# Reads LLM_PROVIDER from .env
llm = get_default_llm()
```

### Explicit Provider
```python
from bpmn_generator.utils.llm_provider import LLMProvider

# Force Ollama for privacy
llm = LLMProvider.get_llm(
    provider="ollama",
    model="qwen2.5:32b",
    temperature=0.1
)
```

### Override in Agents
```python
# src/bpmn_generator/agents/analyst.py
from bpmn_generator.utils.llm_provider import get_default_llm

def analyzer_node(state: AgentState):
    # Uses provider from .env
    llm = get_default_llm()
    
    # Or force specific provider
    # llm = LLMProvider.get_llm(provider="ollama")
    
    result = llm.with_structured_output(ProcessUpdate).invoke(messages)
    return {"last_update": result}
```

---

## Privacy Comparison

| Feature | OpenAI | Ollama | LMStudio |
|---------|--------|--------|----------|
| **Data Privacy** | ⚠️ Cloud | ✅ Local | ✅ Local |
| **Internet Required** | ✅ Yes | ❌ No | ❌ No |
| **GPU Required** | ❌ No | ✅ Yes | ✅ Yes |
| **Cost** | 💰 Pay-per-use | 🆓 Free | 🆓 Free |
| **Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Speed** | ⚡ Fast | 🐢 Depends on GPU | 🐢 Depends on GPU |

---

## Switching Workflow

### Development (Fast Iteration)
```env
LLM_PROVIDER=openai  # Fast, high quality
```

### Production (Sensitive Data)
```env
LLM_PROVIDER=ollama  # Private, local
OLLAMA_MODEL=qwen2.5:32b
```

### Testing (Offline)
```env
LLM_PROVIDER=ollama  # No internet needed
```

---

## Troubleshooting

### Ollama Connection Error
```
Error: Could not connect to Ollama at http://localhost:11434
```

**Solution**:
1. Check Ollama is running: `ollama list`
2. Start Ollama: `ollama serve`
3. Verify model: `ollama pull qwen2.5:32b`

### Model Not Found
```
Error: Model "qwen2.5:32b" not found
```

**Solution**:
```bash
ollama pull qwen2.5:32b
```

### Out of Memory (Ollama)
```
Error: CUDA out of memory
```

**Solution**: Use smaller model
```env
OLLAMA_MODEL=qwen2.5:7b  # Requires only 4GB VRAM
```

---

## Best Practices

1. **Development**: Use OpenAI for speed
2. **Production**: Use Ollama for privacy
3. **Testing**: Use Ollama to avoid API costs
4. **Sensitive Data**: **Always** use Ollama/LMStudio

---

**Last Updated**: 2025-12-29
