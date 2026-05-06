"""Tests for the NVIDIA NIM target model wrapper.

All OpenAI calls are mocked -- no real network traffic. The fitness module
(issue #7) will exercise this in integration; here we cover unit-level
contract: response parsing, retry semantics, error surfacing, and logging.
"""

from __future__ import annotations

import logging
from types import SimpleNamespace
from unittest.mock import MagicMock

import httpx
import openai
import pytest

from src import target_model


def _make_response(content: str) -> SimpleNamespace:
    """Build a fake OpenAI ChatCompletion response object."""
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


def _make_status_error(status_code: int) -> openai.APIStatusError:
    """Construct an APIStatusError with the requested status_code.

    The openai SDK's APIStatusError needs a Response to derive status_code,
    so we build a stub httpx.Response.
    """
    request = httpx.Request("POST", "https://example.test/v1/chat/completions")
    response = httpx.Response(status_code, request=request)
    return openai.APIStatusError(
        message=f"HTTP {status_code}",
        response=response,
        body=None,
    )


@pytest.fixture
def fake_client() -> MagicMock:
    client = MagicMock()
    client.chat.completions.create = MagicMock()
    return client


def test_happy_path_strips_whitespace(fake_client: MagicMock) -> None:
    fake_client.chat.completions.create.return_value = _make_response(
        "  Adds two numbers and returns the result.   \n"
    )
    out = target_model.generate_summary(
        "system instructions", "def add(a,b): return a+b", client=fake_client
    )
    assert out == "Adds two numbers and returns the result."
    assert fake_client.chat.completions.create.call_count == 1


def test_strips_python_fenced_block(fake_client: MagicMock) -> None:
    fake_client.chat.completions.create.return_value = _make_response(
        "```python\nReturns the sum of two integers.\n```"
    )
    out = target_model.generate_summary("p", "c", client=fake_client)
    assert out == "Returns the sum of two integers."


def test_strips_plain_fenced_block(fake_client: MagicMock) -> None:
    fake_client.chat.completions.create.return_value = _make_response(
        "```\nA short summary.\n```"
    )
    out = target_model.generate_summary("p", "c", client=fake_client)
    assert out == "A short summary."


def test_strips_inline_backticks(fake_client: MagicMock) -> None:
    fake_client.chat.completions.create.return_value = _make_response(
        "`inline summary`"
    )
    out = target_model.generate_summary("p", "c", client=fake_client)
    assert out == "inline summary"


def test_messages_use_system_user_split(fake_client: MagicMock) -> None:
    fake_client.chat.completions.create.return_value = _make_response("ok")
    target_model.generate_summary(
        "INSTRUCTIONS", "CODE_BODY", client=fake_client
    )
    kwargs = fake_client.chat.completions.create.call_args.kwargs
    assert kwargs["messages"] == [
        {"role": "system", "content": "INSTRUCTIONS"},
        {"role": "user", "content": "CODE_BODY"},
    ]
    # Determinism check.
    assert kwargs["temperature"] == 0


def test_retry_on_transient_then_succeeds(
    fake_client: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    # No real sleep between retries.
    monkeypatch.setattr(target_model.time, "sleep", lambda _s: None)
    fake_client.chat.completions.create.side_effect = [
        _make_status_error(503),
        _make_response("ok after retry"),
    ]
    out = target_model.generate_summary("p", "c", client=fake_client)
    assert out == "ok after retry"
    assert fake_client.chat.completions.create.call_count == 2


def test_retry_exhausts_then_raises(
    fake_client: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(target_model.time, "sleep", lambda _s: None)
    err = _make_status_error(502)
    fake_client.chat.completions.create.side_effect = [err, err, err]
    with pytest.raises(openai.APIStatusError):
        target_model.generate_summary("p", "c", client=fake_client)
    assert fake_client.chat.completions.create.call_count == 3


def test_4xx_surfaces_immediately(
    fake_client: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(target_model.time, "sleep", lambda _s: None)
    fake_client.chat.completions.create.side_effect = _make_status_error(400)
    with pytest.raises(openai.APIStatusError) as excinfo:
        target_model.generate_summary("p", "c", client=fake_client)
    assert excinfo.value.status_code == 400
    # Only one attempt -- 4xx is non-retryable.
    assert fake_client.chat.completions.create.call_count == 1


def test_connection_error_is_retried(
    fake_client: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(target_model.time, "sleep", lambda _s: None)
    request = httpx.Request("POST", "https://example.test/v1/chat/completions")
    conn_err = openai.APIConnectionError(request=request)
    fake_client.chat.completions.create.side_effect = [
        conn_err,
        _make_response("recovered"),
    ]
    out = target_model.generate_summary("p", "c", client=fake_client)
    assert out == "recovered"
    assert fake_client.chat.completions.create.call_count == 2


def test_latency_logged_at_debug(
    fake_client: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    fake_client.chat.completions.create.return_value = _make_response("ok")
    with caplog.at_level(logging.DEBUG, logger="src.target_model"):
        target_model.generate_summary("p", "c", client=fake_client)
    debug_records = [
        r for r in caplog.records if r.levelno == logging.DEBUG
    ]
    assert any(
        "target_model call succeeded" in r.getMessage() for r in debug_records
    ), f"Expected a success debug log; got: {[r.getMessage() for r in debug_records]}"


def test_missing_api_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    # Stop python-dotenv from re-populating from a real .env on disk.
    monkeypatch.setattr(target_model, "load_dotenv", lambda *a, **kw: None)
    with pytest.raises(ValueError, match="NVIDIA_API_KEY"):
        target_model.generate_summary("p", "c")


def test_model_override_is_respected(fake_client: MagicMock) -> None:
    fake_client.chat.completions.create.return_value = _make_response("ok")
    target_model.generate_summary(
        "p", "c", model="meta/some-other-model", client=fake_client
    )
    kwargs = fake_client.chat.completions.create.call_args.kwargs
    assert kwargs["model"] == "meta/some-other-model"
