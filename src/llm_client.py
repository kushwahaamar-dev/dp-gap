"""LLM client with OpenAI and Ollama backends; structured JSON + retry."""

from __future__ import annotations

import json
import logging
import os
import re
import time
from typing import TypeVar

from dotenv import load_dotenv
from openai import OpenAI, APITimeoutError, APIConnectionError, RateLimitError
from pydantic import BaseModel, ValidationError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

load_dotenv()
logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


def _make_client():
    """OpenAI-compatible client: Ollama if OLLAMA_BASE_URL set, else OpenAI."""
    base = os.getenv("OLLAMA_BASE_URL", "").strip()
    if base:
        return OpenAI(base_url=base, api_key=os.getenv("OLLAMA_API_KEY", "ollama"), timeout=120.0)
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=60.0)


client = _make_client()


def _extract_json(raw: str) -> str:
    """Extract a JSON object from model output (for Ollama which may wrap in markdown)."""
    raw = raw.strip()
    # Try direct parse
    try:
        json.loads(raw)
        return raw
    except json.JSONDecodeError:
        pass
    # Try ```json ... ```
    m = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", raw)
    if m:
        return m.group(1).strip()
    # First { to last }
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        return raw[start : end + 1]
    return raw


class LLMClient:
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.0, max_tokens: int = 2048):
        self.model_name = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.total_tokens_used: int = 0
        self.total_prompt_tokens: int = 0
        self.total_completion_tokens: int = 0
        self.call_count: int = 0
        self._is_ollama = bool(os.getenv("OLLAMA_BASE_URL", "").strip())

    def _request_kwargs(self):
        """Request kwargs: no response_format for Ollama."""
        kw = {
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if not self._is_ollama:
            kw["response_format"] = {"type": "json_object"}
        return kw

    @retry(
        retry=retry_if_exception_type((ValidationError, json.JSONDecodeError, APITimeoutError, APIConnectionError, RateLimitError)),
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        reraise=True,
    )
    def call(self, system_prompt: str, user_prompt: str, response_model: type[T]) -> T:
        """Call LLM and parse response into a Pydantic model."""
        start = time.time()
        kwargs = self._request_kwargs()
        messages = [
            {"role": "system", "content": system_prompt + "\nRespond with valid JSON only. No other text."},
            {"role": "user", "content": user_prompt},
        ]
        response = client.chat.completions.create(messages=messages, **kwargs)
        raw = response.choices[0].message.content or ""
        if self._is_ollama:
            raw = _extract_json(raw)
        self._track(response, time.time() - start)
        return response_model.model_validate_json(raw)

    @retry(
        retry=retry_if_exception_type((APITimeoutError, APIConnectionError, RateLimitError)),
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        reraise=True,
    )
    def call_raw(self, system_prompt: str, user_prompt: str) -> str:
        """Call LLM and return raw text."""
        start = time.time()
        response = client.chat.completions.create(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        self._track(response, time.time() - start)
        return response.choices[0].message.content or ""

    def _track(self, response, elapsed: float) -> None:
        if getattr(response, "usage", None):
            self.total_tokens_used += response.usage.total_tokens or 0
            self.total_prompt_tokens += response.usage.prompt_tokens or 0
            self.total_completion_tokens += response.usage.completion_tokens or 0
        self.call_count += 1
        logger.debug("LLM call #%d  %.2fs", self.call_count, elapsed)

    def reset_tracking(self) -> None:
        self.total_tokens_used = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.call_count = 0

    @property
    def usage_summary(self) -> dict:
        return {
            "total_tokens": self.total_tokens_used,
            "prompt_tokens": self.total_prompt_tokens,
            "completion_tokens": self.total_completion_tokens,
            "api_calls": self.call_count,
        }
