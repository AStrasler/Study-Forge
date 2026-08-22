"""
Mullama provider implementation.

Mullama runs models directly inside your Python process — no separate
server, no HTTP calls. Useful for in-process inference and embeddings.

Docs: https://github.com/mullama/mullama
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from providers.base import BaseProvider, ProviderResponse, ProviderError
from utils.logging import get_logger

logger = get_logger(__name__)

try:
    import mullama
    MULLAMA_AVAILABLE = True
except ImportError:
    MULLAMA_AVAILABLE = False
    logger.warning("Mullama not installed. Run: pip install mullama")


class MullamaProvider(BaseProvider):
    """Mullama in-process inference provider."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Mullama provider.

        Args:
            config: Configuration dict with keys:
                - mullama_model: str (default: llama3.2:3b)
                - mullama_gpu_layers: int (default: 32)
                - mullama_context_size: int (default: 2048)
                - mullama_embedding_model: str (optional)
        """
        if not MULLAMA_AVAILABLE:
            raise ImportError(
                "Mullama is not installed. Run: pip install mullama"
            )

        self.model_name = config.get("mullama_model", "llama3.2:3b")
        self.gpu_layers = config.get("mullama_gpu_layers", 32)
        self.context_size = config.get("mullama_context_size", 2048)
        self.embedding_model = config.get("mullama_embedding_model")
        self._model = None
        self._available = None

    def _load_model(self):
        """Lazy-load the model when first needed."""
        if self._model is None:
            try:
                self._model = mullama.Model.load(
                    self.model_name,
                    n_gpu_layers=self.gpu_layers,
                )
                self._available = True
                logger.info("Mullama loaded model: %s", self.model_name)
            except Exception as e:
                self._available = False
                raise ProviderError(f"Failed to load Mullama model: {e}")

    def is_available(self) -> bool:
        """Check if Mullama is available and the model can be loaded."""
        if self._available is not None:
            return self._available

        if not MULLAMA_AVAILABLE:
            self._available = False
            return False

        try:
            self._load_model()
            self._available = True
        except Exception as e:
            logger.warning("Mullama unavailable: %s", e)
            self._available = False

        return self._available

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> ProviderResponse:
        """
        Generate a response using Mullama.

        Args:
            prompt: The user prompt.
            system_prompt: Optional system prompt (Mullama may handle differently).
            **kwargs: Additional generation parameters.

        Returns:
            ProviderResponse containing the generated text.

        Raises:
            ProviderError: If generation fails.
        """
        if not self.is_available():
            raise ProviderError("Mullama is not available")

        try:
            self._load_model()

            # Combine system and user prompt if both provided
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            # Create context
            context = mullama.Context(
                self._model,
                n_ctx=kwargs.get("context_size", self.context_size),
            )

            # Generate
            result = context.generate(
                full_prompt,
                max_tokens=kwargs.get("max_tokens", 512),
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 0.9),
            )

            return ProviderResponse(
                text=result.strip(),
                model=self.model_name,
                provider="mullama",
                raw_response={"text": result},
            )

        except Exception as e:
            raise ProviderError(f"Mullama generation failed: {e}")

    def get_embeddings(self, text: str) -> list[float]:
        """
        Generate embeddings using Mullama.

        Requires an embedding model to be configured.

        Args:
            text: Text to embed.

        Returns:
            List of float embeddings.

        Raises:
            ProviderError: If embedding fails or no embedding model is configured.
        """
        if not self.embedding_model:
            raise ProviderError("No embedding model configured for Mullama")

        if not self.is_available():
            raise ProviderError("Mullama is not available")

        try:
            self._load_model()
            # Mullama may use a different method for embeddings
            # This is a placeholder — adjust based on actual Mullama API
            raise NotImplementedError(
                "Mullama embeddings not yet implemented. "
                "Check mullama documentation for the correct API."
            )
        except Exception as e:
            raise ProviderError(f"Mullama embedding failed: {e}")

    def get_config(self) -> Dict[str, Any]:
        """Return provider configuration."""
        return {
            "provider": "mullama",
            "model": self.model_name,
            "gpu_layers": self.gpu_layers,
            "context_size": self.context_size,
            "embedding_model": self.embedding_model,
        }

    def __repr__(self) -> str:
        return f"MullamaProvider(model={self.model_name})"