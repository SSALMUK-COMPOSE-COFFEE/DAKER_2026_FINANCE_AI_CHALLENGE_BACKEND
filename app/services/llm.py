import json
import re
from typing import Any

import httpx

from app.config import get_settings


class LLMUnavailable(RuntimeError):
    pass


def configured() -> bool:
    return bool(get_settings().llm_api_key)


def user_block(label: str, text: str) -> str:
    cleaned = text.replace("<<<", "＜＜＜").replace(">>>", "＞＞＞").strip()
    return f"<<<{label}>>>\n{cleaned}\n<<</{label}>>>"


async def complete(
    messages: list[dict[str, str]],
    max_tokens: int = 4096,
    temperature: float = 0.3,
    json_mode: bool = False,
) -> str:
    settings = get_settings()
    if not settings.llm_api_key:
        raise LLMUnavailable("llm_api_key is not configured")

    payload: dict[str, Any] = {
        "model": settings.llm_model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    try:
        async with httpx.AsyncClient(
            base_url=settings.llm_base_url,
            timeout=settings.llm_timeout_seconds,
            headers={
                "Authorization": f"Bearer {settings.llm_api_key}",
                "HTTP-Referer": "https://pullim.hajin.xyz",
                "X-Title": "pullim",
            },
        ) as client:
            res = await client.post("/chat/completions", json=payload)
            res.raise_for_status()
            body = res.json()
    except httpx.HTTPError as exc:
        raise LLMUnavailable(str(exc)) from exc
    except ValueError as exc:
        raise LLMUnavailable(f"non-JSON response: {exc}") from exc

    try:
        content = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMUnavailable(f"unexpected response: {body}") from exc
    if not isinstance(content, str) or not content.strip():
        raise LLMUnavailable("empty completion")
    return content


def parse_json(text: str) -> dict[str, Any]:
    stripped = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", stripped, re.S)
    if fence:
        stripped = fence.group(1).strip()
    try:
        data = json.loads(stripped)
    except json.JSONDecodeError:
        start, end = stripped.find("{"), stripped.rfind("}")
        if start < 0 or end < 0:
            raise LLMUnavailable("completion is not JSON") from None
        try:
            data = json.loads(stripped[start : end + 1])
        except json.JSONDecodeError as exc:
            raise LLMUnavailable("completion is not JSON") from exc
    if not isinstance(data, dict):
        raise LLMUnavailable("completion JSON is not an object")
    return data


async def complete_json(messages: list[dict[str, str]], max_tokens: int = 4096) -> dict[str, Any]:
    text = await complete(messages, max_tokens=max_tokens, temperature=0.2, json_mode=True)
    return parse_json(text)


async def embed(texts: list[str]) -> list[list[float]]:
    settings = get_settings()
    if not settings.embedding_key:
        raise LLMUnavailable("embedding key is not configured")

    payload = {
        "model": settings.embedding_model,
        "input": texts,
        "dimensions": settings.embedding_dimension,
    }
    try:
        async with httpx.AsyncClient(
            base_url=settings.embedding_base_url,
            timeout=settings.embedding_timeout_seconds,
            headers={"Authorization": f"Bearer {settings.embedding_key}"},
        ) as client:
            res = await client.post("/embeddings", json=payload)
            res.raise_for_status()
            body = res.json()
    except httpx.HTTPError as exc:
        raise LLMUnavailable(str(exc)) from exc
    except ValueError as exc:
        raise LLMUnavailable(f"non-JSON response: {exc}") from exc

    try:
        return [item["embedding"] for item in sorted(body["data"], key=lambda d: d["index"])]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMUnavailable(f"unexpected embedding response: {exc}") from exc
