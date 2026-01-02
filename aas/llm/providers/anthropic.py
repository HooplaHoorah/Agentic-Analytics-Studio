"""
Anthropic/Claude LLM Provider for AAS.

This module provides integration with Anthropic's Claude API for generating
AI-powered rationales and recommendations.
"""

import os
from typing import Optional


class AnthropicProvider:
    """
    Anthropic/Claude LLM provider.
    
    Supports both real API calls (if credentials provided) and stub mode
    for demonstration purposes.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key. If not provided, uses ANTHROPIC_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
        self.client = None
        
        if self.api_key:
            try:
                # Try to import anthropic library
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                print("Warning: anthropic library not installed. Running in stub mode.")
                print("Install with: pip install anthropic")
                self.client = None
        else:
            print("Info: No Anthropic API key provided. Running in stub mode.")
    
    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generate text using Claude.
        
        Args:
            prompt: The prompt to send to Claude
            max_tokens: Maximum tokens in response
        
        Returns:
            Generated text response
        """
        if self.client:
            try:
                # Real API call
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return message.content[0].text
            except Exception as e:
                print(f"Error calling Anthropic API: {e}")
                return self._generate_stub_response(prompt)
        else:
            # Stub mode
            return self._generate_stub_response(prompt)
    
    def _generate_stub_response(self, prompt: str) -> str:
        """
        Generate a deterministic stub response based on prompt content.
        
        Args:
            prompt: The original prompt
        
        Returns:
            Stub response text
        """
        # Extract key information from prompt
        prompt_lower = prompt.lower()
        
        # Detect context
        if "pipeline" in prompt_lower or "deal" in prompt_lower:
            return ("This deal shows signs of stagnation with extended time in current stage. "
                   "Immediate follow-up is critical to prevent pipeline leakage and maintain "
                   "revenue momentum. The recommended action addresses the root cause and "
                   "provides a clear path to re-engagement.")
        
        elif "churn" in prompt_lower or "customer" in prompt_lower:
            return ("Customer health indicators suggest elevated churn risk based on declining "
                   "engagement and support patterns. Proactive retention efforts now will be "
                   "more cost-effective than customer acquisition later. This action targets "
                   "the specific pain points identified in the analysis.")
        
        elif "spend" in prompt_lower or "budget" in prompt_lower or "anomaly" in prompt_lower:
            return ("Spending pattern deviates significantly from historical norms and budget "
                   "expectations. This anomaly requires investigation to ensure proper cost "
                   "controls and prevent budget overruns. The recommended action provides "
                   "immediate visibility and accountability.")
        
        elif "revenue" in prompt_lower or "forecast" in prompt_lower:
            return ("Revenue forecast analysis indicates a gap between current pipeline and "
                   "targets. Proactive intervention now can accelerate deals and improve "
                   "conversion rates. This action addresses the highest-impact opportunities "
                   "to close the revenue gap.")
        
        else:
            # Generic business rationale
            return ("Analysis indicates this action will have significant positive impact on "
                   "business outcomes. The recommendation is based on data-driven insights "
                   "and industry best practices. Timely execution will maximize value and "
                   "minimize risk.")
    
    def get_provider_name(self) -> str:
        """Return provider name."""
        return "anthropic"
    
    def is_available(self) -> bool:
        """Check if provider is available (has API key and client)."""
        return self.client is not None


# Example usage
if __name__ == "__main__":
    # Test stub mode
    provider = AnthropicProvider()
    
    test_prompt = "Explain why this deal is at risk: Deal stuck in negotiation for 45 days"
    response = provider.generate(test_prompt)
    
    print(f"Provider: {provider.get_provider_name()}")
    print(f"Available: {provider.is_available()}")
    print(f"Response: {response}")
