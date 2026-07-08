import pytest
from core.validator import parse_raw_payload_data
from core.validator import validate_request, supported_methods, send_payload_methods


def test_parse_valid_json():
    result = parse_raw_payload_data('{"name": "Omen"}')
    assert result == {"name": "Omen"}


def test_parse_invalid_json_raises():
    with pytest.raises(ValueError, match="Invalid JSON"):
        parse_raw_payload_data("{not valid}")


def test_parse_json_array_raises():
    with pytest.raises(ValueError, match="JSON object"):
        parse_raw_payload_data("[1, 2, 3]")


def test_parse_json_string_raises():
    with pytest.raises(ValueError, match="JSON object"):
        parse_raw_payload_data('"just a string"')


def test_validate_get_request():
    request = validate_request("http://localhost:5000/users", "GET")
    assert request.method == "GET"
    assert request.payload is None


def test_validate_post_request_with_payload():
    request = validate_request(
        "http://localhost:5000/users",
        "POST",
        '{"name": "Alex", "email": "alex@fetchman.dev"}',
    )
    assert request.method == "POST"
    assert request.payload == {"name": "Alex", "email": "alex@fetchman.dev"}


def test_validate_query_method_with_payload():
    request = validate_request(
        "http://localhost:5000/users",
        "QUERY",
        '{"filter": "admin"}',
    )
    assert request.method == "QUERY"
    assert request.payload == {"filter": "admin"}


def test_validate_get_with_body_raises():
    with pytest.raises(Exception):
        validate_request("http://localhost:5000/users", "GET", '{"name": "Alex"}')


def test_validate_delete_with_body_raises():
    with pytest.raises(Exception):
        validate_request("http://localhost:5000/users/1", "DELETE", '{"confirm": True}')


def test_validate_invalid_url_raises():
    with pytest.raises(Exception):
        validate_request("not-a-url", "GET")


def test_validate_unsupported_method_raises():
    with pytest.raises(Exception):
        validate_request("http://localhost:5000/users", "FLY")


def test_validate_lowercased_method_is_normalised():
    request = validate_request("http://localhost:5000/users", "get")
    assert request.method == "GET"


def test_validate_whitespace_only_payload_treated_as_none():
    request = validate_request("http://localhost:5000/users", "POST", "   ")
    assert request.payload is None


def test_validate_request_with_headers():
    request = validate_request(
        "http://localhost:5000/users",
        "GET",
        headers={"Authorization": "Bearer token123"},
    )
    assert request.headers == {"Authorization": "Bearer token123"}


def test_supported_methods_has_all_six():
    methods = supported_methods()
    for method in ["GET", "POST", "PUT", "PATCH", "DELETE", "QUERY"]:
        assert method in methods


def test_supported_methods_includes_query():
    assert "QUERY" in supported_methods()


def test_body_methods_excludes_get():
    assert "GET" not in send_payload_methods()


def test_body_methods_excludes_delete():
    assert "DELETE" not in send_payload_methods()


def test_body_methods_includes_query():
    assert "QUERY" in send_payload_methods()
