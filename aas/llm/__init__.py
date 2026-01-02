"""
LLM Integration Layer for Agentic Analytics Studio.

This module provides a unified interface for multiple LLM providers and
manages prompt templates for consistent AI-generated content.
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any

# Import providers
try:
    from .providers.anthropic import AnthropicProvider
    from .providers.gemini import GeminiProvider
except ImportError:
    AnthropicProvider = None
    GeminiProvider = None


class LLMRouter:
    """
    Routes LLM requests to the appropriate provider based on configuration.
    
    Supports: openai, ollama, anthropic, gemini, none (rule-based)
    """
    
    def __init__(self, provider: Optional[str] = None):
        """
        Initialize LLM router.
        
        Args:
            provider: Provider name (openai, ollama, anthropic, gemini, none)
                     If not provided, uses LLM_PROVIDER env var
        """
        self.provider_name = (provider or os.getenv("LLM_PROVIDER", "none")).lower()
        self.provider = None
        self.prompts = self._load_prompts()
        
        # Initialize the appropriate provider
        if self.provider_name == "openai":
            self.provider = self._init_openai()
        elif self.provider_name == "ollama":
            self.provider = self._init_ollama()
        elif self.provider_name == "anthropic":
            self.provider = self._init_anthropic()
        elif self.provider_name == "gemini":
            self.provider = self._init_gemini()
        elif self.provider_name == "none":
            self.provider = None  # Use rule-based fallback
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider_name}")
    
    def _load_prompts(self) -> Dict[str, str]:
        """Load prompt templates from prompts.yaml."""
        prompts_path = Path(__file__).parent / "prompts.yaml"
        
        if prompts_path.exists():
            with open(prompts_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            print(f"Warning: prompts.yaml not found at {prompts_path}")
            return {}
    
    def _init_openai(self):
        """Initialize OpenAI provider."""
        try:
            import openai
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                openai.api_key = api_key
                return "openai"  # Simplified for now
            else:
                print("Warning: OPENAI_API_KEY not set. Falling back to rule-based mode.")
                return None
        except ImportError:
            print("Warning: openai library not installed. Falling back to rule-based mode.")
            return None
    
    def _init_ollama(self):
        """Initialize Ollama provider."""
        # Ollama uses HTTP API, no special client needed
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/api")
        model = os.getenv("OLLAMA_MODEL", "llama3")
        return {"type": "ollama", "base_url": base_url, "model": model}
    
    def _init_anthropic(self):
        """Initialize Anthropic provider."""
        if AnthropicProvider:
            return AnthropicProvider()
        else:
            print("Warning: Anthropic provider not available. Falling back to rule-based mode.")
            return None
    
    def _init_gemini(self):
        """Initialize Gemini provider."""
        if GeminiProvider:
            return GeminiProvider()
        else:
            print("Warning: Gemini provider not available. Falling back to rule-based mode.")
            return None
    
    def generate(self, prompt_key: str, context: Dict[str, Any]) -> str:
        """
        Generate text using the configured provider.
        
        Args:
            prompt_key: Key for prompt template in prompts.yaml
            context: Dictionary of variables to fill in the template
        
        Returns:
            Generated text
        """
        # Get prompt template
        prompt_template = self.prompts.get(prompt_key, "")
        
        if not prompt_template:
            # Fallback to generic template
            prompt_template = self.prompts.get("rationale_template", "")
        
        # Fill in template
        try:
            prompt = prompt_template.format(**context)
        except KeyError as e:
            print(f"Warning: Missing context variable {e}. Using partial prompt.")
            prompt = prompt_template
        
        # Generate using provider
        if self.provider_name == "anthropic" and isinstance(self.provider, AnthropicProvider):
            return self.provider.generate(prompt)
        
        elif self.provider_name == "gemini" and isinstance(self.provider, GeminiProvider):
            return self.provider.generate(prompt)
        
        elif self.provider_name == "openai" and self.provider:
            return self._generate_openai(prompt)
        
        elif self.provider_name == "ollama" and self.provider:
            return self._generate_ollama(prompt)
        
        else:
            # Rule-based fallback
            return self._generate_fallback(context)
    
    def _generate_openai(self, prompt: str) -> str:
        """Generate using OpenAI."""
        try:
            import openai
            model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            return self._generate_fallback({})
    
    def _generate_ollama(self, prompt: str) -> str:
        """Generate using Ollama."""
        try:
            import httpx
            
            base_url = self.provider["base_url"]
            model = self.provider["model"]
            
            response = httpx.post(
                f"{base_url}/generate",
                json={"model": model, "prompt": prompt},
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                print(f"Ollama API error: {response.status_code}")
                return self._generate_fallback({})
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return self._generate_fallback({})
    
    def _generate_fallback(self, context: Dict[str, Any]) -> str:
        """Generate using rule-based fallback."""
        priority = context.get("priority", "medium")
        impact_score = context.get("impact_score", 0)
        
        # Use priority-based fallback prompts
        if priority == "high":
            template = self.prompts.get("fallback_rationale_high_priority", "")
        elif priority == "low":
            template = self.prompts.get("fallback_rationale_low_priority", "")
        else:
            template = self.prompts.get("fallback_rationale_medium_priority", "")
        
        try:
            return template.format(impact_score=impact_score)
        except:
            return (f"This action has an estimated impact of {impact_score} and should be "
                   f"prioritized accordingly based on data-driven analysis.")
    
    def get_provider_name(self) -> str:
        """Return the current provider name."""
        return self.provider_name
    
    def is_available(self) -> bool:
        """Check if the provider is available and configured."""
        if self.provider_name == "none":
            return True  # Fallback always available
        return self.provider is not None


# Global instance
_router = None


def get_llm_router() -> LLMRouter:
    """Get or create global LLM router instance."""
    global _router
    if _router is None:
        _router = LLMRouter()
    return _router


def generate_rationale(prompt_key: str, context: Dict[str, Any]) -> str:
    """
    Convenience function to generate rationale using global router.
    
    Args:
        prompt_key: Key for prompt template
        context: Context variables
    
    Returns:
        Generated rationale text
    """
    router = get_llm_router()
    return router.generate(prompt_key, context)
