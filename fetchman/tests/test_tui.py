from tui import status_category_color, is_validation_error, is_json_content, _wrap_json_body, Theme


def test_status_category_color_success():
    assert status_category_color("success") == Theme.SUCCESS


def test_status_category_color_redirect():
    assert status_category_color("redirect") == Theme.REDIRECT


def test_status_category_color_error():
    assert status_category_color("error") == Theme.ERROR


def test_status_category_color_unknown_defaults_safely():
    assert status_category_color("bogus") == Theme.UNKNOWN


def test_is_validation_error_true_for_short_dict():
    assert is_validation_error({"ok": False, "error": "bad url"}) is True


def test_is_validation_error_false_for_full_response():
    assert is_validation_error({"ok": True, "status_code": 200, "error": None}) is False


def test_is_validation_error_false_when_status_code_is_none():
    assert is_validation_error({"ok": False, "status_code": None, "error": "timeout"}) is False


def test_is_json_content_true():
    assert is_json_content("application/json; charset=utf-8") is True


def test_is_json_content_false_for_plain_text():
    assert is_json_content("text/plain") is False


def test_is_json_content_false_for_none():
    assert is_json_content(None) is False


def test_wrap_json_body_leaves_short_lines_untouched():
    body = '{\n  "a": 1\n}'
    assert _wrap_json_body(body, 40) == body


def test_wrap_json_body_wraps_long_line_with_matching_indent():
    line = '        "notes": "This is a fairly long note field that will likely need to wrap"'
    wrapped = _wrap_json_body(line, 60)
    lines = wrapped.splitlines()
    assert len(lines) > 1
    assert all(l.startswith("        ") for l in lines[1:])


def test_wrap_json_body_preserves_blank_lines():
    body = "line one\n\nline two"
    assert _wrap_json_body(body, 20) == body


def test_wrap_json_body_zero_width_returns_input_unchanged():
    body = '{\n  "a": 1\n}'
    assert _wrap_json_body(body, 0) == body
