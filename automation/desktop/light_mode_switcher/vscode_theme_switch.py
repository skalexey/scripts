#!/usr/bin/env python3
"""Cross-platform VS Code theme switcher.

Updates workbench.colorTheme in settings.json while preserving JSONC comments.
"""

from __future__ import annotations

import json
import os
import platform
import re
import sys
from pathlib import Path


THEME_KEY_PATTERN = re.compile(r'"workbench\.colorTheme"\s*:\s*"(?:[^"\\]|\\.)*"')


def is_wsl() -> bool:
    if platform.system().lower() != "linux":
        return False
    try:
        release = platform.release().lower()
        if "microsoft" in release:
            return True
        return "microsoft" in Path("/proc/version").read_text(encoding="utf-8").lower()
    except OSError:
        return False


def windows_path_to_wsl(path_value: str) -> Path | None:
    match = re.match(r"^([A-Za-z]):\\(.*)$", path_value)
    if not match:
        return None

    drive = match.group(1).lower()
    tail = match.group(2).replace("\\", "/")
    return Path(f"/mnt/{drive}/{tail}")


def get_default_settings_paths() -> list[Path]:
    system = platform.system().lower()

    if system == "windows":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return [Path(appdata) / "Code" / "User" / "settings.json"]
        return [Path.home() / "AppData" / "Roaming" / "Code" / "User" / "settings.json"]

    if system == "darwin":
        return [
            Path.home() / "Library" / "Application Support" / "Code" / "User" / "settings.json",
            Path.home() / "Library" / "Application Support" / "Code - Insiders" / "User" / "settings.json",
        ]

    if is_wsl():
        wsl_candidates: list[Path] = []
        appdata = os.environ.get("APPDATA")
        userprofile = os.environ.get("USERPROFILE")

        if appdata:
            appdata_wsl = windows_path_to_wsl(appdata)
            if appdata_wsl is not None:
                wsl_candidates.append(appdata_wsl / "Code" / "User" / "settings.json")

        if userprofile:
            userprofile_wsl = windows_path_to_wsl(userprofile)
            if userprofile_wsl is not None:
                wsl_candidates.append(userprofile_wsl / "AppData" / "Roaming" / "Code" / "User" / "settings.json")

        wsl_candidates.extend(
            [
                Path.home() / ".config" / "Code" / "User" / "settings.json",
                Path.home() / ".config" / "Code - OSS" / "User" / "settings.json",
                Path.home() / ".config" / "VSCodium" / "User" / "settings.json",
            ]
        )
        return wsl_candidates

    return [
        Path.home() / ".config" / "Code" / "User" / "settings.json",
        Path.home() / ".config" / "Code - OSS" / "User" / "settings.json",
        Path.home() / ".config" / "VSCodium" / "User" / "settings.json",
    ]


def resolve_settings_path() -> Path:
    override = os.environ.get("VSCODE_SETTINGS_PATH")
    if override:
        return Path(override).expanduser()

    candidates = get_default_settings_paths()
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


def update_theme(raw_settings: str, theme_name: str) -> str:
    theme_value = json.dumps(theme_name)
    replacement = f'"workbench.colorTheme": {theme_value}'

    if not raw_settings.strip():
        return "{\n  " + replacement + "\n}\n"

    if THEME_KEY_PATTERN.search(raw_settings):
        return THEME_KEY_PATTERN.sub(replacement, raw_settings, count=1)

    open_brace = raw_settings.find("{")
    if open_brace < 0:
        return "{\n  " + replacement + "\n}\n"

    before = raw_settings[: open_brace + 1]
    after = raw_settings[open_brace + 1 :]
    has_entries = after.strip() and not after.lstrip().startswith("}")
    separator = "," if has_entries else ""
    insertion = f"\n  {replacement}{separator}"

    return before + insertion + after


def main() -> int:
    if len(sys.argv) < 2:
        print("No VS Code theme specified", file=sys.stderr)
        return 1

    theme_name = " ".join(sys.argv[1:]).strip()
    if not theme_name:
        print("No VS Code theme specified", file=sys.stderr)
        return 1

    settings_path = resolve_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    raw_settings = ""
    if settings_path.exists():
        raw_settings = settings_path.read_text(encoding="utf-8")

    updated_settings = update_theme(raw_settings, theme_name)
    settings_path.write_text(updated_settings, encoding="utf-8")

    print(f"VS Code theme set to '{theme_name}' in {settings_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
