from typing import Any

import httpx

from app.core.config import get_settings


class AzureOpenAIClientError(Exception):
    pass


class AzureOpenAIClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def is_configured(self) -> bool:
        return bool(
            self.settings.azure_openai_api_key
            and self.settings.azure_openai_endpoint
            and self.settings.azure_openai_deployment
            and self.settings.azure_openai_api_version
        )

    def chat_completion(
        self,
        *,
        messages: list[dict[str, str]],
        max_completion_tokens: int,
        temperature: float | None = None,
        response_format: dict[str, str] | None = None,
    ) -> str:
        if not self.is_configured:
            raise AzureOpenAIClientError("azure_openai_not_configured")

        payload: dict[str, Any] = {
            "messages": messages,
            "max_completion_tokens": max_completion_tokens,
        }
        if temperature is not None:
            payload["temperature"] = temperature
        if response_format is not None:
            payload["response_format"] = response_format

        headers = {
            "Content-Type": "application/json",
            "api-key": self.settings.azure_openai_api_key or "",
        }

        try:
            with httpx.Client(timeout=self.settings.azure_openai_timeout_seconds) as client:
                response = client.post(self.settings.azure_openai_chat_endpoint, headers=headers, json=payload)
                response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise AzureOpenAIClientError(exc.__class__.__name__) from exc

        if not content:
            raise AzureOpenAIClientError("empty_response")
        return content.strip()

