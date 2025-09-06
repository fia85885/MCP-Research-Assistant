# src/mcp_server/embeddings.py
import os
from typing import List

class Embeddings:
    def __init__(self, backend: str = "openai", model_name: str = "text-embedding-3-small"):
        self.backend = backend
        self.model_name = model_name

        if backend != "openai":
            raise ValueError("This wrapper currently supports only the OpenAI backend.")

        # Ensure API key present (better to set it in environment or Claude config)
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY not set in environment")

        # Try to import the new client API first
        try:
            # openai >= 1.0
            from openai import OpenAI
            self._client = OpenAI()
            self._mode = "client"   # modern client mode
        except Exception:
            # If this fails, try to import legacy module (rare if you upgraded)
            try:
                import openai as _openai
                self._client = _openai
                self._mode = "legacy"
            except Exception as e:
                raise RuntimeError("Could not import OpenAI client library") from e

    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Return list of embeddings (one list of floats per input text).
        Works with modern OpenAI client (1.x).
        """
        if self._mode == "client":
            # Modern client: resp.data is a sequence of objects/dicts with 'embedding'
            resp = self._client.embeddings.create(model=self.model_name, input=texts)
            out = []
            for d in getattr(resp, "data", resp.get("data") if isinstance(resp, dict) else []):
                # d may be dict or object with attribute
                if isinstance(d, dict):
                    emb = d.get("embedding")
                else:
                    emb = getattr(d, "embedding", None)
                if emb is None:
                    raise RuntimeError("Unexpected embedding response shape from OpenAI client")
                out.append(emb)
            return out

        else:
            # Legacy (old openai <1.0)
            # Keep for backward compatibility — but if openai>=1.0 is installed this branch likely won't run.
            resp = self._client.Embedding.create(model=self.model_name, input=texts)
            data = resp.get("data", [])
            return [item.get("embedding") for item in data]

    # convenience alias for code that expects .encode()
    def encode(self, texts: List[str]) -> List[List[float]]:
        return self.embed(texts)
