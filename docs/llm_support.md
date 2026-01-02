# LLM Provider Support - Agentic Analytics Studio

## Overview

AAS supports multiple Large Language Model (LLM) providers for generating AI-powered rationales and recommendations. The system uses a unified router architecture that allows seamless switching between providers.

---

## Supported Providers

| Provider | Status | API Required | Local/Cloud | Best For |
|----------|--------|--------------|-------------|----------|
| **OpenAI** | ✅ Production | Yes | Cloud | High-quality rationales, GPT-3.5/4 |
| **Ollama** | ✅ Production | No | Local | Privacy, no API costs, offline |
| **Anthropic** | ✅ Stub/Production | Yes | Cloud | Claude models, nuanced analysis |
| **Gemini** | ✅ Stub/Production | Yes | Cloud | Google's latest models |
| **Rule-Based** | ✅ Production | No | Local | No dependencies, deterministic |

---

## Configuration

### Environment Variables

Set `LLM_PROVIDER` to choose your provider:

```env
# Choose one: openai, ollama, anthropic, gemini, none
LLM_PROVIDER=openai
```

### Provider-Specific Configuration

#### OpenAI
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key
OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4
```

**Installation:**
```bash
pip install openai
```

#### Ollama (Local)
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434/api
OLLAMA_MODEL=llama3  # or mistral, codellama, etc.
```

**Installation:**
1. Install Ollama: https://ollama.ai
2. Pull model: `ollama pull llama3`
3. Start server: `ollama serve`

#### Anthropic (Claude)
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-api-key
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

**Installation:**
```bash
pip install anthropic
```

**Stub Mode:** Works without API key, returns intelligent fallback responses.

#### Google Gemini
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-pro
```

**Installation:**
```bash
pip install google-generativeai
```

**Stub Mode:** Works without API key, returns intelligent fallback responses.

#### Rule-Based (No LLM)
```env
LLM_PROVIDER=none
```

No additional configuration needed. Uses deterministic keyword-based rationales.

---

## Centralized Prompts

All prompt templates are defined in `aas/llm/prompts.yaml`. This allows:
- Consistent messaging across plays
- Easy customization without code changes
- Version control for prompts
- A/B testing different prompt strategies

### Prompt Structure

```yaml
rationale_template: |
  You are an expert business analyst...
  Context: {context}
  Action: {action}
  Provide a clear rationale...

pipeline_leakage_rationale: |
  Deal Information:
  - Deal: {deal_name}
  - Stage: {stage}
  ...
```

### Using Prompts in Code

```python
from aas.llm import generate_rationale

rationale = generate_rationale(
    prompt_key="pipeline_leakage_rationale",
    context={
        "deal_name": "Acme Corp",
        "stage": "Negotiation",
        "amount": 250000,
        "days_in_stage": 45
    }
)
```

---

## Architecture

### LLM Router

The `LLMRouter` class provides a unified interface:

```python
from aas.llm import LLMRouter

router = LLMRouter(provider="anthropic")
response = router.generate("rationale_template", context)
```

### Provider Classes

Each provider implements:
- `generate(prompt, max_tokens)` - Generate text
- `get_provider_name()` - Return provider name
- `is_available()` - Check if configured

### Fallback Logic

1. Try configured provider
2. If error, fall back to rule-based
3. Always return a response (never crash)

---

## Stub Mode

Anthropic and Gemini providers include intelligent stub modes that work without API keys:

**Features:**
- Context-aware responses based on prompt content
- Different responses for each play type
- Deterministic (same input = same output)
- No API calls or costs

**Use Cases:**
- Demos without API keys
- Testing without rate limits
- Offline development
- Cost control

**Example:**
```python
# No API key set
provider = AnthropicProvider()

# Still works!
response = provider.generate("Explain why this deal is at risk...")
# Returns: "This deal shows signs of stagnation..."
```

---

## Adding a New Provider

### 1. Create Provider Class

```python
# aas/llm/providers/my_provider.py

class MyProvider:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("MY_PROVIDER_API_KEY")
        self.client = None
        # Initialize client if API key provided
    
    def generate(self, prompt, max_tokens=500):
        if self.client:
            # Real API call
            return self.client.generate(prompt)
        else:
            # Stub fallback
            return self._generate_stub(prompt)
    
    def get_provider_name(self):
        return "my_provider"
    
    def is_available(self):
        return self.client is not None
```

### 2. Register in Router

```python
# aas/llm/__init__.py

def _init_my_provider(self):
    from .providers.my_provider import MyProvider
    return MyProvider()
```

### 3. Update Configuration

```env
# .env.example
LLM_PROVIDER=my_provider
MY_PROVIDER_API_KEY=your-api-key
```

### 4. Add Documentation

Update this file with provider details.

---

## Best Practices

### 1. Use Appropriate Provider for Use Case

- **Production:** OpenAI (reliable, high quality)
- **Privacy-sensitive:** Ollama (local, no data leaves server)
- **Cost-conscious:** Rule-based or Ollama
- **Demos:** Anthropic/Gemini stub mode

### 2. Handle Errors Gracefully

```python
try:
    rationale = generate_rationale(key, context)
except Exception as e:
    logger.error(f"LLM error: {e}")
    rationale = "Action recommended based on data analysis."
```

### 3. Monitor Costs

- Set `max_tokens` appropriately
- Use caching for repeated prompts
- Consider rate limits

### 4. Customize Prompts

Edit `prompts.yaml` to:
- Match your brand voice
- Add domain-specific context
- Improve response quality

### 5. Test All Providers

```bash
# Test each provider
LLM_PROVIDER=openai pytest tests/test_llm.py
LLM_PROVIDER=anthropic pytest tests/test_llm.py
LLM_PROVIDER=gemini pytest tests/test_llm.py
LLM_PROVIDER=none pytest tests/test_llm.py
```

---

## Troubleshooting

### "Provider not available"
- Check API key is set correctly
- Verify library is installed (`pip install anthropic`)
- Check network connectivity

### "Stub mode activated"
- API key not provided or invalid
- Library not installed
- This is expected behavior - stub mode works fine for demos

### "Prompt template not found"
- Check `prompts.yaml` exists in `aas/llm/`
- Verify YAML syntax is valid
- Ensure prompt key matches exactly

### "Rate limit exceeded"
- Reduce request frequency
- Use caching
- Consider switching to Ollama for development

---

## Performance

### Response Times (Approximate)

| Provider | Avg Response Time | Notes |
|----------|------------------|-------|
| OpenAI | 1-3s | Depends on model and load |
| Ollama | 2-10s | Depends on hardware and model size |
| Anthropic | 1-3s | Similar to OpenAI |
| Gemini | 1-3s | Google's infrastructure |
| Rule-Based | <10ms | Instant, deterministic |

### Cost Comparison

| Provider | Cost per 1K Tokens | Monthly (1M tokens) |
|----------|-------------------|---------------------|
| OpenAI GPT-3.5 | $0.002 | $2 |
| OpenAI GPT-4 | $0.03 | $30 |
| Anthropic Claude | $0.008 | $8 |
| Gemini Pro | $0.00025 | $0.25 |
| Ollama | $0 | $0 (hardware costs) |
| Rule-Based | $0 | $0 |

---

## Future Enhancements

- [ ] Prompt versioning and A/B testing
- [ ] Response caching layer
- [ ] Streaming responses for long-form content
- [ ] Multi-provider ensemble (combine responses)
- [ ] Fine-tuned models for specific plays
- [ ] Prompt optimization based on feedback

---

**Last Updated:** 2026-01-02  
**Version:** 1.0
