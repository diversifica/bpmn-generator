"""LLM provider configuration and factory.

Supports multiple LLM providers with privacy-focused switching:
- OpenAI (cloud, requires API key)
- Ollama (local, privacy-first)
- LMStudio (local, future support)
"""

import os
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI


class LLMProvider:
    """Factory for creating LLM instances based on configuration."""

    @staticmethod
    def get_llm(
        provider: str | None = None,
        model: str | None = None,
        temperature: float = 0.1,
        **kwargs: Any,
    ) -> BaseChatModel:
        """Get configured LLM instance.

        Args:
            provider: LLM provider ("openai", "ollama", "lmstudio").
                     Defaults to LLM_PROVIDER env var.
            model: Model name. Defaults to provider-specific env var.
            temperature: Sampling temperature (0.0-1.0). Default 0.1 for determinism.
            **kwargs: Additional provider-specific arguments.

        Returns:
            Configured LLM instance.

        Raises:
            ValueError: If provider is unsupported or configuration is invalid.

        Examples:
            >>> # OpenAI (cloud)
            >>> llm = LLMProvider.get_llm(provider="openai")
            
            >>> # Ollama (local)
            >>> llm = LLMProvider.get_llm(provider="ollama", model="qwen2.5:32b")
        """
        provider = provider or os.getenv("LLM_PROVIDER", "openai")
        provider = provider.lower()

        if provider == "openai":
            return LLMProvider._get_openai_llm(model, temperature, **kwargs)
        elif provider == "ollama":
            return LLMProvider._get_ollama_llm(model, temperature, **kwargs)
        elif provider == "lmstudio":
            return LLMProvider._get_lmstudio_llm(model, temperature, **kwargs)
        else:
            raise ValueError(
                f"Unsupported LLM provider: {provider}. "
                f"Supported: openai, ollama, lmstudio"
            )

    @staticmethod
    def _get_openai_llm(
        model: str | None, temperature: float, **kwargs: Any
    ) -> BaseChatModel:
        """Get OpenAI LLM instance."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")

        model = model or os.getenv("OPENAI_MODEL", "gpt-4o")
        base_url = os.getenv("OPENAI_BASE_URL")  # Optional custom endpoint

        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,
            base_url=base_url,
            **kwargs,
        )

    @staticmethod
    def _get_ollama_llm(
        model: str | None, temperature: float, **kwargs: Any
    ) -> BaseChatModel:
        """Get Ollama LLM instance (local/private)."""
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            raise ImportError(
                "langchain-ollama not installed. "
                "Install with: pip install langchain-ollama"
            )

        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = model or os.getenv("OLLAMA_MODEL", "qwen2.5:32b")

        return ChatOllama(
            model=model,
            temperature=temperature,
            base_url=base_url,
            **kwargs,
        )

    @staticmethod
    def _get_lmstudio_llm(
        model: str | None, temperature: float, **kwargs: Any
    ) -> BaseChatModel:
        """Get LMStudio LLM instance (local/private).

        LMStudio exposes an OpenAI-compatible API, so we use ChatOpenAI
        with a custom base_url.
        """
        base_url = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
        model = model or os.getenv("LMSTUDIO_MODEL", "local-model")

        return ChatOpenAI(
            model=model,
            temperature=temperature,
            base_url=base_url,
            api_key="lm-studio",  # LMStudio doesn't require real API key
            **kwargs,
        )


def get_default_llm(**kwargs: Any) -> BaseChatModel:
    """Get default LLM based on environment configuration.

    This is a convenience function that reads LLM_PROVIDER from env
    and returns the appropriate LLM instance.

    Args:
        **kwargs: Additional arguments passed to LLMProvider.get_llm()

    Returns:
        Configured LLM instance.

    Examples:
        >>> # In .env: LLM_PROVIDER=ollama
        >>> llm = get_default_llm()
        >>> # Returns Ollama instance
    """
    return LLMProvider.get_llm(**kwargs)
