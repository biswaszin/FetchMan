import json
from fetchman.core.validator import send_payload_methods
import pytest
from main import execute_request, get_response_statistics, get_payload_methods
from main import get_response_body, get_response_headers, get_request_headers, get_supported_methods


@pytest.fixture
def successful_response():
    return {
        "ok": True,
        "status_code": 200,
        "status_text": "OK",
        "method": "GET",
        "url": "http://localhost:5000/users",
        "elapsed_ms": 42.5,
        "response_size_bytes": 1024,
        "content_type": "application/json",
        "redirects": 0,
        "body": {"users": [{"id": 1, "name": "Alex"}]},
        "response_headers": {"Content-Type": "application/json"},
        "request_headers": {"User-Agent": "python-requests"},
        "timestamp": "2024-01-01T00:00:00+00:00",
        "error": None,
    }


@pytest.fixture
def error_response():
    return {
        "ok": False,
        "status_code": None,
        "status_text": None,
        "method": "GET",
        "url": "http://localhost:5000/users",
        "elapsed_ms": None,
        "response_size_bytes": None,
        "content_type": None,
        "redirects": None,
        "body": None,
        "response_headers": None,
        "request_headers": None,
        "timestamp": "2024-01-01T00:00:00+00:00",
        "error": "Could not connect to the server",
    }


def test_execute_request_invalid_url():
    result = execute_request("not-a-url", "GET")
    assert result["ok"] is False
    assert result["error"] is not None


def test_execute_request_unsupported_method():
    result = execute_request("http://localhost:5000", "FLY")
    assert result["ok"] is False


def test_execute_request_invalid_payload_json():
    result = execute_request("http://localhost:5000/users", "POST", "{bad json}")
    assert result["ok"] is False
    assert result["error"] is not None


def test_execute_request_get_with_body_rejected():
    result = execute_request("http://localhost:5000/users", "GET", '{"name": "Alex"}')
    assert result["ok"] is False


def test_get_response_statistics_fields(successful_response):
    stats = get_response_statistics(successful_response)
    assert stats["status_code"] == 200
    assert stats["status_text"] == "OK"
    assert stats["ok"] is True
    assert stats["elapsed_ms"] == 42.5
    assert stats["response_size_human_readable"] == "1.0 KB"
    assert stats["status_category"] == "success"
    assert stats["redirects"] == 0


def test_get_response_statistics_error_category(error_response):
    stats = get_response_statistics(error_response)
    assert stats["status_category"] == "error"
    assert stats["ok"] is False


def test_get_response_statistics_redirect_category(successful_response):
    successful_response["status_code"] = 301
    stats = get_response_statistics(successful_response)
    assert stats["status_category"] == "redirect"


def test_get_response_statistics_4xx_is_error(successful_response):
    successful_response["status_code"] = 404
    stats = get_response_statistics(successful_response)
    assert stats["status_category"] == "error"


def test_get_response_statistics_5xx_is_error(successful_response):
    successful_response["status_code"] = 500
    stats = get_response_statistics(successful_response)
    assert stats["status_category"] == "error"


def test_get_response_body_is_valid_json(successful_response):
    body = get_response_body(successful_response)
    parsed = json.loads(body)
    assert parsed == successful_response["body"]


def test_get_response_body_has_indentation(successful_response):
    body = get_response_body(successful_response)
    assert "\n" in body


def test_get_response_body_empty_string_on_error(error_response):
    assert get_response_body(error_response) == ""


def test_get_response_body_plain_text(successful_response):
    successful_response["body"] = "plain text"
    assert get_response_body(successful_response) == "plain text"


def test_get_response_headers(successful_response):
    assert get_response_headers(successful_response) == {"Content-Type": "application/json"}


def test_get_response_headers_empty_dict_on_error(error_response):
    assert get_response_headers(error_response) == {}


def test_get_request_headers(successful_response):
    assert get_request_headers(successful_response) == {"User-Agent": "python-requests"}


def test_get_request_headers_empty_dict_on_error(error_response):
    assert get_request_headers(error_response) == {}


def test_get_supported_methods_complete():
    assert set(get_supported_methods()) == {"GET", "POST", "PUT", "PATCH", "DELETE", "QUERY"}


def test_get_body_methods_excludes_get_and_delete():
    methods = send_payload_methods()
    assert "GET" not in methods
    assert "DELETE" not in methods


def test_get_body_methods_includes_query():
    assert "QUERY" in send_payload_methods()


def test_human_readable_size_bytes(successful_response):
    successful_response["response_size_bytes"] = 512
    stats = get_response_statistics(successful_response)
    assert stats["response_size_human_readable"] == "512 B"


def test_human_readable_size_kilobytes(successful_response):
    successful_response["response_size_bytes"] = 2048
    stats = get_response_statistics(successful_response)
    assert "KB" in stats["response_size_human_readable"]


def test_human_readable_size_megabytes(successful_response):
    successful_response["response_size_bytes"] = 2 * 1024 * 1024
    stats = get_response_statistics(successful_response)
    assert "MB" in stats["response_size_human_readable"]


def test_human_readable_size_none_on_error(error_response):
    stats = get_response_statistics(error_response)
    assert stats["response_size_human_readable"] is None
