from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

from app.agents.base import AgentResult, IAgent


class AgentV001:
    """Minimal agent: single model call using Gemini via google-generativeai.

    Reads a short system prompt from `app/prompts/agent/v001.txt` and formats
    the user input with company and question. Returns the model's text.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_name: str = str(self.config.get("model", "gemini-1.5-pro-latest"))
        self.temperature: float = float(self.config.get("temperature", 0.2))
        self.top_p: float = float(self.config.get("top_p", 0.95))
        self.max_output_tokens: int = int(self.config.get("max_output_tokens", 1024))

        # Lazy import so other parts of the app don't require the dependency
        import google.generativeai as genai  # type: ignore

        api_key = self.config.get("google_api_key") or os.getenv("GOOGLE_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY is not set; required for V001 model calls."
            )
        genai.configure(api_key=api_key)

        self._genai = genai
        self._model = genai.GenerativeModel(self.model_name)

    def _load_system_prompt(self) -> str:
        prompt_path = (
            Path(__file__).resolve().parents[2] / "prompts" / "agent" / "v001.txt"
        )
        try:
            return prompt_path.read_text(encoding="utf-8").strip()
        except Exception:
            return "You are a helpful assistant. Answer the user's question concisely."

    def run(self, company: str, question: str) -> AgentResult:
        system_prompt = self._load_system_prompt()
        user_content = (
            f"{system_prompt}\n\n"
            f"Company: {company}\n"
            f"Question: {question}\n"
            "Please answer concisely and factually."
        )

        try:
            response = self._model.generate_content(
                user_content,
                generation_config={
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "max_output_tokens": self.max_output_tokens,
                },
            )
            text = getattr(response, "text", None) or ""
            answer = text.strip() or "(no response)"
            return AgentResult(answer=answer)
        except Exception as e:  # pragma: no cover - transient network/api
            return AgentResult(answer=f"[V001] Error: {e}")
