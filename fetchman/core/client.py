#! /usr/bin/python3

import requests
from datetime import datetime, timezone
from core.validator import RequestModel

def send_request(request: RequestModel) -> dict:
    request_timestamp = datetime.now(timezone.utc).isoformat()

    try:
        response = requests.request(
            method=request.method,
            url=str(request.url),
            json=request.payload,
            headers=request.headers or {},
            allow_redirects=True,
            timeout=30,
        )

        try:
            raw_body = response.json()
        except Exception:
            raw_body = response.text

        return {
            "ok": response.ok,
            "status_code": response.status_code,
            "status_text": response.reason,
            "method": request.method,
            "url": str(response.url),
            "elapsed_ms": round(response.elapsed.total_seconds() * 1000, 2),
            "response_size_bytes": len(response.content),
            "content_type": response.headers.get("Content-Type", ""),
            "redirects": len(response.history),
            "body": raw_body,
            "response_headers": dict(response.headers),
            "request_headers": dict(response.request.headers),
            "timestamp": request_timestamp,
            "error": None,
        }

    except requests.exceptions.ConnectionError:
        return _error_message(request, "Could not connect to the server", request_timestamp)
    except requests.exceptions.Timeout:
        return _error_message(request, "Request timed out after 30 seconds", request_timestamp)
    except requests.exceptions.InvalidURL:
        return _error_message(request, "Invalid URL", request_timestamp)
    except requests.exceptions.RequestException as request_error:
        return _error_message(request, str(request_error), request_timestamp)

def _error_message(fetch_request: RequestModel, error_message: str, timestamp: str) -> dict:
    return {
        "ok": False,
        "status_code": None,
        "status_text": None,
        "method": fetch_request.method,
        "url": str(fetch_request.url),
        "elapsed_ms": None,
        "response_size_bytes": None,
        "content_type": None,
        "redirects": None,
        "body": None,
        "response_headers": None,
        "request_headers": None,
        "timestamp": timestamp,
        "error": error_message,
    }
