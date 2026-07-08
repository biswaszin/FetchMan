import pytest
import requests
from core.client import send_request
from unittest.mock import patch, MagicMock
from core.validator import validate_request

@pytest.fixture
def get_request():
    return validate_request("http://localhost:5000/users", "GET")


@pytest.fixture
def post_request():
    return validate_request(
        "http://localhost:5000/users",
        "POST",
        '{"name": "Harbor", "email": "harbor@fetchman.dev"}',
    )


@pytest.fixture
def mock_json_response():
    mock = MagicMock()
    mock.ok = True
    mock.status_code = 200
    mock.reason = "OK"
    mock.url = "http://localhost:5000/users"
    mock.elapsed.total_seconds.return_value = 0.042
    mock.content = b'{"users": []}'
    mock.headers = {"Content-Type": "application/json"}
    mock.history = []
    mock.request.headers = {"User-Agent": "python-requests/2.31.0"}
    mock.json.return_value = {"users": []}
    return mock


def test_successful_get_request(get_request, mock_json_response):
    with patch("core.client.requests.request", return_value=mock_json_response):
        result = send_request(get_request)
    assert result["ok"] is True
    assert result["status_code"] == 200
    assert result["body"] == {"users": []}
    assert result["error"] is None


def test_successful_post_returns_201(post_request, mock_json_response):
    mock_json_response.ok = True
    mock_json_response.status_code = 201
    mock_json_response.reason = "Created"
    mock_json_response.json.return_value = {"id": 4, "name": "Harbor"}
    with patch("core.client.requests.request", return_value=mock_json_response):
        result = send_request(post_request)
    assert result["status_code"] == 201
    assert result["body"]["name"] == "Harbor"


def test_response_stats_are_populated(get_request, mock_json_response):
    with patch("core.client.requests.request", return_value=mock_json_response):
        result = send_request(get_request)
    assert result["elapsed_ms"] == 42.0
    assert result["response_size_bytes"] == len(b'{"users": []}')
    assert result["content_type"] == "application/json"
    assert result["redirects"] == 0
    assert result["timestamp"] is not None


def test_connection_error_returns_error_dict(get_request):
    with patch("core.client.requests.request", side_effect=requests.exceptions.ConnectionError):
        result = send_request(get_request)
    assert result["ok"] is False
    assert "connect" in result["error"].lower()


def test_timeout_returns_error_dict(get_request):
    with patch("core.client.requests.request", side_effect=requests.exceptions.Timeout):
        result = send_request(get_request)
    assert result["ok"] is False
    assert "timed out" in result["error"].lower()


def test_plain_text_body_is_returned_as_string(get_request):
    mock = MagicMock()
    mock.ok = True
    mock.status_code = 200
    mock.reason = "OK"
    mock.url = "http://localhost:5000/healthz"
    mock.elapsed.total_seconds.return_value = 0.01
    mock.content = b"ok"
    mock.headers = {"Content-Type": "text/plain"}
    mock.history = []
    mock.request.headers = {}
    mock.json.side_effect = ValueError("not json")
    mock.text = "ok"
    with patch("core.client.requests.request", return_value=mock):
        result = send_request(get_request)
    assert result["body"] == "ok"


def test_error_response_contains_all_expected_keys(get_request):
    with patch("core.client.requests.request", side_effect=requests.exceptions.ConnectionError):
        result = send_request(get_request)
    for key in ["ok", "status_code", "status_text", "method", "url",
                "elapsed_ms", "response_size_bytes", "body", "error", "timestamp"]:
        assert key in result
