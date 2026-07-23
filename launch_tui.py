#! /usr/bin/python3

import os
import platform
import shlex
import shutil
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))


def _linux_command() -> str:
    activate = os.path.join(REPO_ROOT, ".venv", "bin", "activate")
    return f"cd {shlex.quote(REPO_ROOT)} && source {shlex.quote(activate)} && python -m fetchman.tui"


def _windows_command() -> str:
    return f'cd /d "{REPO_ROOT}" && call ".venv\\Scripts\\activate.bat" && python -m fetchman.tui'


def _linux_ancestor_names(max_depth=8) -> list:
    names = []
    pid = os.getppid()
    for _ in range(max_depth):
        try:
            with open(f"/proc/{pid}/status") as f:
                content = f.read()
            name = ppid = None
            for line in content.splitlines():
                if line.startswith("Name:"):
                    name = line.split(":", 1)[1].strip()
                elif line.startswith("PPid:"):
                    ppid = int(line.split(":", 1)[1].strip())
            if name:
                names.append(name)
            if not ppid or ppid <= 1:
                break
            pid = ppid
        except (FileNotFoundError, PermissionError, ValueError):
            break
    return names


def _detect_linux_terminal():
    names = [n.lower() for n in _linux_ancestor_names()]
    if any("kitty" in n for n in names):
        return "kitty"
    if any("konsole" in n for n in names):
        return "konsole"
    if any("alacritty" in n for n in names):
        return "alacritty"
    return None


def _windows_ancestor_names(max_depth=6) -> list:
    start_pid = os.getppid()
    script = f"""
$targetPid = {start_pid}
$names = @()
for ($i = 0; $i -lt {max_depth}; $i++) {{
    $p = Get-CimInstance Win32_Process -Filter "ProcessId=$targetPid" -ErrorAction SilentlyContinue
    if (-not $p) {{ break }}
    $names += $p.Name
    $targetPid = $p.ParentProcessId
    if ($targetPid -eq 0) {{ break }}
}}
$names -join ','
"""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return [n.strip() for n in result.stdout.strip().split(",") if n.strip()]
    except Exception:
        return []


def _detect_windows_shell():
    names = [n.lower() for n in _windows_ancestor_names()]
    if any(n in ("pwsh.exe", "powershell.exe") for n in names):
        return "powershell"
    if any(n == "cmd.exe" for n in names):
        return "cmd"
    return None


def _launch_linux() -> bool:
    cmd = _linux_command()
    preferred = _detect_linux_terminal()
    order = ([preferred] if preferred else []) + [
        t for t in ("konsole", "alacritty", "kitty") if t != preferred
    ]
    for terminal in order:
        if not shutil.which(terminal):
            continue
        if terminal == "kitty":
            subprocess.Popen(["kitty", "bash", "-c", cmd])
        else:
            subprocess.Popen([terminal, "-e", "bash", "-c", cmd])
        return True
    return False


def _launch_windows() -> bool:
    cmd = _windows_command()
    shell = _detect_windows_shell()
    if shell == "powershell":
        subprocess.Popen(
            ["powershell", "-NoProfile", "-Command", cmd],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        return True
    subprocess.Popen(["cmd.exe", "/c", cmd], creationflags=subprocess.CREATE_NEW_CONSOLE)
    return True


def main() -> None:
    launched = _launch_windows() if platform.system() == "Windows" else _launch_linux()
    if not launched:
        print(
            "No supported terminal emulator found (looked for konsole, alacritty, kitty). "
            "Run `python -m fetchman.tui` directly instead.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
