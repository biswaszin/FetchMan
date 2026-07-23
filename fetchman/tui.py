#! /usr/bin/python3

import os
import sys
import textwrap

if os.name == "nt":
    import msvcrt
else:
    import termios
    import tty

_FETCHMAN_DIR = os.path.dirname(os.path.abspath(__file__))
if _FETCHMAN_DIR not in sys.path:
    sys.path.insert(0, _FETCHMAN_DIR)

from main import (
    execute_request,
    get_response_statistics,
    get_response_body,
    get_response_headers,
    get_request_headers,
    get_supported_methods,
    get_payload_methods,
)

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
from rich.live import Live

console = Console()


class Theme:
    PRIMARY = "#7B86E8"       # periwinkle/indigo — brand accent (banner, titles, chrome)
    SECONDARY = "#5C6B84"     # slate blue-gray — structural chrome (borders, field labels)
    HIGHLIGHT = "#C98B5E"     # terracotta — emphasis (row labels, validation-error border)

    SUCCESS = "#8FBF6B"       # muted green — status: success
    REDIRECT = "#D9A441"      # warm amber — status: redirect (kept distinct from HIGHLIGHT)
    ERROR = "#E0607E"         # muted rose-red — status: error / real failures
    UNKNOWN = "#9AA5B1"       # cool gray — fallback

    MUTED = "#7A8699"         # dim/secondary text
    VALIDATION_BORDER = HIGHLIGHT
    ERROR_BORDER = ERROR


_BANNER = (
    f"[bold {Theme.PRIMARY}]Fetch[/bold {Theme.PRIMARY}]"
    f"[bold {Theme.SECONDARY}]Man[/bold {Theme.SECONDARY}]  "
    f"[{Theme.HIGHLIGHT}]\U0001F415[/{Theme.HIGHLIGHT}]"
)
_TAGLINE = "fetch first, ask questions later"


def status_category_color(category: str) -> str:
    return {
        "success": Theme.SUCCESS,
        "redirect": Theme.REDIRECT,
        "error": Theme.ERROR,
    }.get(category, Theme.UNKNOWN)


def is_validation_error(response: dict) -> bool:
    return "status_code" not in response


def is_json_content(content_type: str | None) -> bool:
    return bool(content_type) and "json" in content_type.lower()


def _wrap_json_body(body_str: str, width: int) -> str:
    if width <= 0:
        return body_str

    wrapped_lines: list[str] = []
    for line in body_str.splitlines():
        stripped = line.strip()
        if not stripped or len(line) <= width:
            wrapped_lines.append(line)
            continue

        leading_ws = line[: len(line) - len(line.lstrip(" "))]
        wrapped = textwrap.wrap(
            line,
            width=width,
            subsequent_indent=leading_ws,
            break_long_words=False,
            break_on_hyphens=False,
            drop_whitespace=False,
            replace_whitespace=False,
        )
        wrapped_lines.extend(wrapped or [line])

    return "\n".join(wrapped_lines)


_last_method = "GET"

_METHOD_SHORTCUTS = {
    "GET": "g",
    "POST": "p",
    "PUT": "u",
    "PATCH": "a",
    "DELETE": "d",
    "QUERY": "q",
}


class _RawTerminal:
    def __enter__(self):
        self._fd = None
        if os.name != "nt" and sys.stdin.isatty():
            self._fd = sys.stdin.fileno()
            self._old_settings = termios.tcgetattr(self._fd)
            tty.setcbreak(self._fd)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._fd is not None:
            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old_settings)
        return False


def _read_key() -> str:
    if os.name == "nt":
        ch = msvcrt.getch()
        if ch in (b"\x00", b"\xe0"):
            ch2 = msvcrt.getch()
            return {b"K": "LEFT", b"M": "RIGHT"}.get(ch2, "")
        if ch == b"\x03":
            raise KeyboardInterrupt
        if ch in (b"\r", b"\n"):
            return "ENTER"
        return ch.decode("utf-8", errors="ignore").lower()

    ch = sys.stdin.read(1)
    if ch == "\x03":
        raise KeyboardInterrupt
    if ch in ("\r", "\n"):
        return "ENTER"
    if ch == "\x1b":
        seq = sys.stdin.read(2)
        return {"[C": "RIGHT", "[D": "LEFT"}.get(seq, "")
    return ch.lower()


def _render_method_picker(methods: list[str], index: int) -> Table:
    grid = Table.grid(padding=(0, 2), expand=False)
    for _ in methods:
        grid.add_column(justify="center")
    cells = [
        f"[bold {Theme.PRIMARY}]{m}[/bold {Theme.PRIMARY}]" if i == index
        else f"[{Theme.MUTED}]{m}[/{Theme.MUTED}]"
        for i, m in enumerate(methods)
    ]
    grid.add_row(*cells)
    return grid


def _prompt_method_interactive(default: str) -> str:
    methods = get_supported_methods()

    if not sys.stdin.isatty():
        return Prompt.ask("Method", choices=methods, default=default)

    index = methods.index(default) if default in methods else 0
    letter_to_index = {
        _METHOD_SHORTCUTS.get(m, m[0].lower()): i for i, m in enumerate(methods)
    }

    console.print(f"[{Theme.MUTED}]Use ←/→ to cycle, a letter to jump, Enter to confirm[/{Theme.MUTED}]")
    with _RawTerminal():
        with Live(_render_method_picker(methods, index), console=console, auto_refresh=False, transient=True) as live:
            while True:
                key = _read_key()
                if key == "RIGHT":
                    index = (index + 1) % len(methods)
                elif key == "LEFT":
                    index = (index - 1) % len(methods)
                elif key == "ENTER":
                    break
                elif key in letter_to_index:
                    index = letter_to_index[key]
                live.update(_render_method_picker(methods, index), refresh=True)

    selected = methods[index]
    console.print(f"Method: [bold {Theme.PRIMARY}]{selected}[/bold {Theme.PRIMARY}]")
    return selected


def _prompt_method() -> str:
    global _last_method
    method = _prompt_method_interactive(_last_method)
    _last_method = method
    return method


def _prompt_payload(method: str) -> str | None:
    if method not in get_payload_methods():
        return None
    if not Confirm.ask("Add a JSON body?", default=False):
        return None
    return Prompt.ask("JSON payload (single line)")


def _prompt_headers() -> dict[str, str] | None:
    if not Confirm.ask("Add custom headers?", default=False):
        return None
    headers: dict[str, str] = {}
    while True:
        key = Prompt.ask("Header name")
        value = Prompt.ask(f"Value for {key}")
        headers[key] = value
        if not Confirm.ask("Add another header?", default=False):
            break
    return headers or None


def _print_step_header(step: int, total: int, label: str) -> None:
    grid = Table.grid(expand=True)
    grid.add_column(justify="left")
    grid.add_column(justify="right")
    grid.add_row(
        f"[bold {Theme.PRIMARY}]{label}[/bold {Theme.PRIMARY}]",
        f"[{Theme.MUTED}]Step {step}/{total}[/{Theme.MUTED}]",
    )
    console.print(grid)


def _prompt_new_request() -> tuple[str, str, str | None, dict[str, str] | None]:
    _print_step_header(1, 2, "Build Request")
    url = Prompt.ask("URL")
    method = _prompt_method()
    raw_payload = _prompt_payload(method)
    headers = _prompt_headers()
    return url, method, raw_payload, headers


def _build_summary_table(stats: dict) -> Table:
    color = status_category_color(stats["status_category"])
    flavor = "  [dim]— good boy[/dim]" if stats["status_category"] == "success" else ""
    table = Table(
        title=f"{stats['method']} {stats['url']}{flavor}",
        title_style=f"bold {color}",
        border_style=color,
        show_header=False,
        expand=True,
    )
    table.add_column("Field", style=f"bold {Theme.SECONDARY}", justify="right")
    table.add_column("Value")
    table.add_row("Status", f"[{color}]{stats['status_code']} {stats['status_text'] or ''}[/{color}]".strip())
    table.add_row("Elapsed", f"{stats['elapsed_ms']} ms" if stats["elapsed_ms"] is not None else "-")
    table.add_row("Size", stats["response_size_human_readable"] or "-")
    table.add_row("Content-Type", stats["content_type"] or "-")
    table.add_row("Redirects", str(stats["redirects"]) if stats["redirects"] is not None else "-")
    table.add_row("Timestamp", stats["timestamp"] or "-")
    return table


def _build_headers_table(headers: dict, title: str) -> Table:
    table = Table(title=title, title_style=f"bold {Theme.PRIMARY}", border_style=Theme.SECONDARY, expand=True)
    table.add_column("Header", style=f"bold {Theme.HIGHLIGHT}")
    table.add_column("Value")
    for key, value in (headers or {}).items():
        table.add_row(key, value)
    return table


def _render_validation_error(response: dict) -> None:
    console.print(
        Panel(
            f"Woof — that request needs work: {response['error']}",
            title="Validation Error",
            border_style=Theme.VALIDATION_BORDER,
        )
    )


def _render_response(response: dict) -> None:
    stats = get_response_statistics(response)
    color = status_category_color(stats["status_category"])

    console.print(_build_summary_table(stats))
    console.print()

    if stats["error"]:
        console.print(Panel(f"Ruff! {stats['error']}", title="Error", border_style=Theme.ERROR_BORDER))
        console.print()

    body_title = f"[bold {Theme.PRIMARY}]Body[/bold {Theme.PRIMARY}]"
    body_str = get_response_body(response)
    if not body_str:
        console.print("[dim](no response body)[/dim]")
    elif is_json_content(stats["content_type"]):
        wrapped_body = _wrap_json_body(body_str, max(console.width - 4, 20))
        console.print(
            Panel(
                Syntax(wrapped_body, "json", theme="monokai", word_wrap=False, background_color="default"),
                title=body_title,
                border_style=color,
            )
        )
    else:
        console.print(Panel(body_str, title=body_title, border_style=color))
    console.print()

    console.print(_build_headers_table(get_response_headers(response), "Response Headers"))
    console.print()
    console.print(_build_headers_table(get_request_headers(response), "Request Headers"))


def _show_banner() -> None:
    console.print(
        Panel(
            _BANNER,
            subtitle=f"[{Theme.MUTED}]{_TAGLINE}[/{Theme.MUTED}]",
            border_style=Theme.PRIMARY,
            padding=(1, 4),
        )
    )


def _show_main_menu() -> str:
    console.print()
    return Prompt.ask("[1] Fetch  [2] Heel (quit)", choices=["1", "2"], default="1")


def _run_request_flow() -> None:
    try:
        url, method, raw_payload, headers = _prompt_new_request()
        console.print()
        _print_step_header(2, 2, "Fetch")
        with console.status(f"[{Theme.PRIMARY}]Fetching…[/{Theme.PRIMARY}]", spinner="dots"):
            response = execute_request(url, method, raw_payload, headers)
        console.print()
        if is_validation_error(response):
            _render_validation_error(response)
        else:
            _render_response(response)
    except Exception as exc:
        console.print(Panel(f"Ruff! {exc}", title="Unexpected Error", border_style=Theme.ERROR_BORDER))


def main() -> None:
    _show_banner()
    try:
        while True:
            if _show_main_menu() == "2":
                break
            _run_request_flow()
    except KeyboardInterrupt:
        console.print()
        console.print("[bold]Good boy. See you next fetch![/bold]")


if __name__ == "__main__":
    main()
