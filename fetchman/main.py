#! /usr/bin/python3


import json
from core.client import send_request
from core.validator import validate_request, supported_methods, send_payload_methods


def execute_request(
    url: str,
    method: str,
    raw_payload: str | None = None,
    headers: dict[str, str] | None = None,
) -> dict:
    try:

        request = validate_request(url, method, raw_payload, headers)
    except Exception as validation_error:

        return {
            "ok": False,
            "error": str(validation_error)
        }

    return send_request(request)


def get_response_statistics(response: dict) -> dict:
    raw_size = response.get("response_size_bytes")

    return {
        "status_code": response.get("status_code"),
        "status_text": response.get("status_text"),
        "status_category": _get_status_response(response.get("status_code")),
        "ok": response.get("ok"),
        "method": response.get("method"),
        "url": response.get("url"),
        "elapsed_ms": response.get("elapsed_ms"),
        "response_size_bytes": raw_size,
        "response_size_human_readable": _get_response_size(raw_size),
        "content_type": response.get("content_type"),
        "redirects": response.get("redirects"),
        "timestamp": response.get("timestamp"),
        "error": response.get("error"),
    }


def get_response_body(response: dict) -> str:
    body = response.get("body")

    if isinstance(body, (dict, list)):
        return json.dumps(body, indent=2)

    return str(body) if body else ""


def get_response_headers(response: dict) -> dict[str, str]:
    return response.get("response_headers") or {}


def get_request_headers(response: dict) -> dict[str, str]:
    return response.get("request_headers") or {}


def get_supported_methods() -> list[str]:
    return supported_methods()


def get_payload_methods() -> list[str]:
    return send_payload_methods()


def _get_status_response(status_code: int | None) -> str:
    if status_code is None:
        return "error"
    if status_code < 300:
        return "success"
    if status_code < 400:
        return "redirect"
    return "error"


def _get_response_size(size_bytes: int | None) -> str | None:
    if size_bytes is None:
        return None
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 ** 2:
        return f"{round(size_bytes / 1024, 2)} KB"
    return f"{round(size_bytes / 1024 ** 2, 2)} MB"
