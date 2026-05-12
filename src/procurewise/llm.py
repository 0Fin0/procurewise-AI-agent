from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any

from .config import OPENAI_API_KEY, OPENAI_MODEL, USE_LLM
from .prompts import SYSTEM_PROMPT
from .schemas import ToolResult


class RecommendationDrafter:
    def __init__(
        self,
        use_llm: bool | None = None,
        model: str | None = None,
        client: Any | None = None,
    ) -> None:
        self.use_llm = USE_LLM if use_llm is None else use_llm
        self.model = model or OPENAI_MODEL
        self.client = client

    def draft(self, state: dict[str, Any], fallback: str) -> tuple[str, ToolResult]:
        if not self.use_llm:
            return fallback, ToolResult(
                name="response_drafter",
                status="completed",
                details={"mode": "deterministic", "reason": "PROCUREWISE_USE_LLM is false"},
            )

        if self.client is None and not OPENAI_API_KEY:
            return fallback, ToolResult(
                name="response_drafter",
                status="completed_with_fallback",
                details={"mode": "deterministic", "reason": "OPENAI_API_KEY is not set"},
            )

        try:
            recommendation = self._draft_with_openai(state).strip()
        except Exception as exc:
            return fallback, ToolResult(
                name="response_drafter",
                status="completed_with_fallback",
                details={
                    "mode": "deterministic",
                    "attempted_model": self.model,
                    "error": type(exc).__name__,
                },
            )

        if not recommendation:
            return fallback, ToolResult(
                name="response_drafter",
                status="completed_with_fallback",
                details={"mode": "deterministic", "reason": "empty LLM response"},
            )

        return recommendation, ToolResult(
            name="response_drafter",
            status="completed",
            details={"mode": "llm", "model": self.model},
        )

    def _draft_with_openai(self, state: dict[str, Any]) -> str:
        client = self.client
        if client is None:
            from openai import OpenAI

            client = OpenAI(api_key=OPENAI_API_KEY)

        prompt = self._build_prompt(state)
        if hasattr(client, "responses"):
            response = client.responses.create(**self._responses_kwargs(prompt))
            text = self._extract_text(response)
            if text:
                return text

        if not hasattr(client, "chat"):
            return ""

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT.strip()},
                {"role": "user", "content": prompt},
            ],
            max_completion_tokens=1200,
        )
        return self._extract_chat_text(response)

    def _responses_kwargs(self, prompt: str) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "instructions": SYSTEM_PROMPT.strip(),
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt,
                        }
                    ],
                }
            ],
            "max_output_tokens": 3000,
        }
        if self.model.startswith("gpt-5"):
            kwargs["reasoning"] = {"effort": "minimal"}
            kwargs["text"] = {"verbosity": "low"}
        return kwargs

    def _build_prompt(self, state: dict[str, Any]) -> str:
        payload = {
            "request": state["request"],
            "facts": self._clean(state["facts"]),
            "vendor": self._clean(state.get("vendor")),
            "risk_level": state["risk_level"],
            "approval_path": state["approval_path"],
            "missing_intake_fields": state.get("missing_intake_fields", []),
            "policy_bypass_attempt": state.get("policy_bypass_attempt", False),
            "decision_status": state.get("decision_status", ""),
            "recommended_human_action": state.get("recommended_human_action", ""),
            "policy_evidence": self._clean(state["evidence"]),
            "tool_results": self._clean(state["tool_results"]),
        }
        return (
            "Draft the final procurement recommendation as one concise paragraph. "
            "Use only the facts, policy evidence, and tool outputs below. Do not change "
            "the risk level or approval path. Mention the main next action. Return visible "
            "plain text only.\n\n"
            + json.dumps(payload, indent=2)
        )

    def _clean(self, value: Any) -> Any:
        if is_dataclass(value):
            return asdict(value)
        if isinstance(value, list):
            return [self._clean(item) for item in value]
        if isinstance(value, dict):
            return {key: self._clean(item) for key, item in value.items()}
        return value

    def _extract_text(self, response: Any) -> str:
        output_text = getattr(response, "output_text", None)
        if output_text:
            return str(output_text)

        response_data = self._to_mapping(response)
        if response_data:
            output_text = response_data.get("output_text")
            if output_text:
                return str(output_text)
            output = response_data.get("output", [])
        else:
            output = getattr(response, "output", [])

        parts: list[str] = []
        for item in output or []:
            item_data = self._to_mapping(item)
            content = item_data.get("content", []) if item_data else getattr(item, "content", [])
            for block in content or []:
                block_data = self._to_mapping(block)
                text = block_data.get("text") if block_data else getattr(block, "text", None)
                if text:
                    parts.append(self._string_value(text))
        return "\n".join(parts)

    def _extract_chat_text(self, response: Any) -> str:
        choices = getattr(response, "choices", [])
        if not choices and isinstance(response, dict):
            choices = response.get("choices", [])
        if not choices:
            return ""

        choice = choices[0]
        choice_data = self._to_mapping(choice)
        message = choice_data.get("message") if choice_data else getattr(choice, "message", None)
        message_data = self._to_mapping(message)
        content = message_data.get("content") if message_data else getattr(message, "content", None)
        return self._string_value(content)

    def _to_mapping(self, value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return value
        for method_name in ("model_dump", "to_dict", "dict"):
            method = getattr(value, method_name, None)
            if callable(method):
                try:
                    data = method()
                except Exception:
                    continue
                if isinstance(data, dict):
                    return data
        return {}

    def _string_value(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return "\n".join(self._string_value(item) for item in value if self._string_value(item))
        if isinstance(value, dict):
            for key in ("text", "value", "content"):
                if key in value:
                    return self._string_value(value[key])
            return ""
        text = getattr(value, "text", None)
        if text:
            return self._string_value(text)
        value_attr = getattr(value, "value", None)
        if value_attr:
            return self._string_value(value_attr)
        return str(value)
