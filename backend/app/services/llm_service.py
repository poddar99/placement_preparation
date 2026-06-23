import json
import logging
import re
from typing import Any, Dict, List, Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMService:
    """Ollama-based LLM service for all AI generation."""

    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model
        self.timeout = httpx.Timeout(120.0, connect=10.0)

    async def _request(self, endpoint: str, payload: dict) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}{endpoint}", json=payload)
            response.raise_for_status()
            return response.json()

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        json_mode: bool = False,
    ) -> str:
        full_prompt = prompt
        if system:
            full_prompt = f"System: {system}\n\nUser: {prompt}"

        if json_mode:
            full_prompt += "\n\nRespond with valid JSON only. No markdown, no explanation outside JSON."

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }

        try:
            result = await self._request("/api/generate", payload)
            return result.get("response", "").strip()
        except httpx.HTTPError as e:
            logger.error("Ollama generate error: %s", e)
            raise RuntimeError(f"LLM service unavailable: {e}") from e

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
    ) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }

        try:
            result = await self._request("/api/chat", payload)
            message = result.get("message", {})
            return message.get("content", "").strip()
        except httpx.HTTPError as e:
            logger.error("Ollama chat error: %s", e)
            raise RuntimeError(f"LLM service unavailable: {e}") from e

    async def generate_json(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.5,
    ) -> Dict[str, Any]:
        raw = await self.generate(prompt, system=system, temperature=temperature, json_mode=True)
        return self._parse_json(raw)

    def _parse_json(self, text: str) -> Dict[str, Any]:
        text = text.strip()
        # Remove markdown code fences if present
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON object from response
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            logger.warning("Failed to parse JSON from LLM: %s", text[:200])
            return {"raw_response": text, "parse_error": True}

    async def get_embedding(self, text: str) -> List[float]:
        """Get embeddings from Ollama."""
        payload = {"model": settings.ollama_embedding_model, "prompt": text}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/api/embeddings", json=payload)
                response.raise_for_status()
                result = response.json()
                return result.get("embedding", [])
        except httpx.HTTPError as e:
            logger.error("Ollama embedding error: %s", e)
            raise RuntimeError(f"Embedding service unavailable: {e}") from e


llm_service = LLMService()