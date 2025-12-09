"""
LLM Provider Abstraction Layer

Supports multiple LLM providers:
- Anthropic (Claude)
- OpenAI (GPT-4)
- Google (Gemini)

Environment Variables:
- CODE_GEN_PROVIDER: "anthropic" | "openai" | "gemini" (default: "gemini")
- ANTHROPIC_API_KEY: For Claude
- OPENAI_API_KEY: For GPT-4
- GEMINI_API_KEY: For Gemini
"""
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider"""
    text: str
    input_tokens: int
    output_tokens: int
    model: str
    finish_reason: Optional[str] = None


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> LLMResponse:
        """Generate a response from the LLM"""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Return the model name being used"""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name"""
        pass


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider"""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        super().__init__(api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model = model

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for Claude provider")

        from anthropic import Anthropic
        self.client = Anthropic(api_key=self.api_key)
        logger.info(f"Initialized Anthropic provider with model: {model}")

    async def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> LLMResponse:
        """Generate using Claude"""
        try:
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "You are a helpful AI assistant.",
                messages=messages
            )

            return LLMResponse(
                text=response.content[0].text,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                model=self.model,
                finish_reason=response.stop_reason
            )
        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            raise

    def get_model_name(self) -> str:
        return self.model

    @property
    def provider_name(self) -> str:
        return "anthropic"


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT-4 provider"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        super().__init__(api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for GPT provider")

        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)
        logger.info(f"Initialized OpenAI provider with model: {model}")

    async def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> LLMResponse:
        """Generate using GPT-4"""
        try:
            # Prepend system message if provided
            full_messages = []
            if system_prompt:
                full_messages.append({"role": "system", "content": system_prompt})
            full_messages.extend(messages)

            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=full_messages
            )

            choice = response.choices[0]
            return LLMResponse(
                text=choice.message.content or "",
                input_tokens=response.usage.prompt_tokens if response.usage else 0,
                output_tokens=response.usage.completion_tokens if response.usage else 0,
                model=self.model,
                finish_reason=choice.finish_reason
            )
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise

    def get_model_name(self) -> str:
        return self.model

    @property
    def provider_name(self) -> str:
        return "openai"


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash-lite"):
        super().__init__(api_key or os.getenv("GEMINI_API_KEY"))
        self.model = model

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required for Gemini provider")

        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        self.genai = genai

        # Configure model with safety settings
        self.generation_config = {
            "temperature": 0.7,
            "max_output_tokens": 4000,
        }
        logger.info(f"Initialized Gemini provider with model: {model}")

    async def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> LLMResponse:
        """Generate using Gemini"""
        try:
            # Create model with system instruction
            model = self.genai.GenerativeModel(
                model_name=self.model,
                system_instruction=system_prompt or "You are a helpful AI assistant."
            )

            # Convert messages to Gemini format
            gemini_messages = []
            for msg in messages:
                role = "user" if msg["role"] == "user" else "model"
                gemini_messages.append({
                    "role": role,
                    "parts": [msg["content"]]
                })

            # Generate response
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }

            response = await asyncio.to_thread(
                model.generate_content,
                gemini_messages,
                generation_config=generation_config
            )

            # Extract text and token counts
            text = response.text if response.text else ""

            # Gemini doesn't always provide token counts in the same way
            input_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0) if hasattr(response, 'usage_metadata') else 0
            output_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0) if hasattr(response, 'usage_metadata') else 0

            return LLMResponse(
                text=text,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=self.model,
                finish_reason="stop"
            )
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise

    def get_model_name(self) -> str:
        return self.model

    @property
    def provider_name(self) -> str:
        return "gemini"


# Provider registry
PROVIDERS = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
}

# Default models for each provider
DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-20250514",
    "openai": "gpt-4o",
    "gemini": "gemini-2.5-flash-lite",
}


def get_llm_provider(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    api_key: Optional[str] = None
) -> BaseLLMProvider:
    """
    Factory function to get an LLM provider instance

    Args:
        provider: Provider name ("anthropic", "openai", "gemini")
                  Defaults to CODE_GEN_PROVIDER env var or "gemini"
        model: Model name. Defaults to provider's default model
        api_key: Optional API key (otherwise uses env vars)

    Returns:
        Configured LLM provider instance
    """
    # Get provider from env if not specified
    provider = provider or os.getenv("CODE_GEN_PROVIDER", "gemini")
    provider = provider.lower()

    if provider not in PROVIDERS:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(f"Unknown provider '{provider}'. Available: {available}")

    # Get default model if not specified
    model = model or os.getenv("CODE_GEN_MODEL") or DEFAULT_MODELS.get(provider)

    # Create provider instance
    provider_class = PROVIDERS[provider]
    return provider_class(api_key=api_key, model=model)


def get_available_providers() -> List[str]:
    """Return list of available providers based on configured API keys"""
    available = []

    if os.getenv("ANTHROPIC_API_KEY"):
        available.append("anthropic")
    if os.getenv("OPENAI_API_KEY"):
        available.append("openai")
    if os.getenv("GEMINI_API_KEY"):
        available.append("gemini")

    return available


def get_default_provider() -> str:
    """
    Get the default provider based on available API keys
    Priority: CODE_GEN_PROVIDER env var > gemini > openai > anthropic
    """
    configured = os.getenv("CODE_GEN_PROVIDER")
    if configured and configured.lower() in PROVIDERS:
        return configured.lower()

    # Auto-detect based on available keys
    available = get_available_providers()

    # Prefer Gemini (usually free tier available), then OpenAI, then Anthropic
    for preferred in ["gemini", "openai", "anthropic"]:
        if preferred in available:
            return preferred

    raise ValueError(
        "No LLM provider configured. Set one of: "
        "GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY"
    )
