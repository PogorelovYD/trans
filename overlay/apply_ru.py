#!/usr/bin/env python3
"""Apply Russian UI translations and locale support to an upstream Cicada checkout."""
import json
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1]).resolve()
overlay = pathlib.Path(__file__).resolve().parent


def parse(path):
    text = path.read_text(encoding="utf-8")
    return dict(re.findall(
        r'^"((?:[^"\\]|\\.)*)"\s*=\s*"((?:[^"\\]|\\.)*)";',
        text,
        re.M,
    ))


def quote(value):
    escaped = (value.replace("\\", "\\\\").replace('"', '\\"')
               .replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t"))
    return '"' + escaped + '";'


translations = json.loads((overlay / "ru_windows.json").read_text(encoding="utf-8"))

# Shared UI resources are embedded from Resources/**/Localizable.strings.
# Windows-only text is embedded separately from Strings/**/Windows.strings.
common_dir = root / "Resources/ru.lproj"
windows_dir = root / "windows/src/Cicada/Strings/ru.lproj"
common_dir.mkdir(parents=True, exist_ok=True)
windows_dir.mkdir(parents=True, exist_ok=True)

common = parse(root / "Resources/en.lproj/Localizable.strings")
windows = parse(root / "windows/src/Cicada/Strings/en.lproj/Windows.strings")

(common_dir / "Localizable.strings").write_text(
    "/* Russian shared UI translation. Remaining entries fall back to English. */\n"
    + "\n".join(f'"{key}" = {quote(translations.get(key, value))}' for key, value in common.items())
    + "\n",
    encoding="utf-8",
)
(windows_dir / "Windows.strings").write_text(
    "/* Russian Windows-only UI translation. Remaining entries fall back to English. */\n"
    + "\n".join(f'"{key}" = {quote(translations.get(key, value))}' for key, value in windows.items())
    + "\n",
    encoding="utf-8",
)

# Allow Windows to select Russian automatically or from Settings.
p = root / "windows/src/Cicada.Core/Strings.cs"
s = p.read_text(encoding="utf-8")
s = s.replace(
    'Language = head is "en" or "ja" or "ko" ? head : "zh-Hans";',
    'Language = head is "en" or "ja" or "ko" or "ru" ? head : "zh-Hans";',
)
s = s.replace(
    '"ko" => "ko-KR", _ => "zh-CN" }',
    '"ko" => "ko-KR", "ru" => "ru-RU", _ => "zh-CN" }',
)
if '"ru" ? head' not in s or '"ru" => "ru-RU"' not in s:
    raise SystemExit("Failed to add Russian culture support in Strings.cs")
p.write_text(s, encoding="utf-8")

p = root / "windows/src/Cicada/SettingsWindow.cs"
s = p.read_text(encoding="utf-8")
if '("ko", "한국어"), ("ru", "Русский")' not in s:
    if '("ko", "한국어")' not in s:
        raise SystemExit("Language picker not found in SettingsWindow.cs")
    s = s.replace('("ko", "한국어")', '("ko", "한국어"), ("ru", "Русский")', 1)
p.write_text(s, encoding="utf-8")

# Include Russian in the source-level translation completeness checkers.
for rel in ("scripts/strings.py", "windows/scripts/strings.py"):
    p = root / rel
    s = p.read_text(encoding="utf-8")
    s = s.replace('LANGS = ["en", "ja", "ko"]', 'LANGS = ["en", "ja", "ko", "ru"]')
    s = s.replace('for lang in ["en", "ja", "ko"]:', 'for lang in ["en", "ja", "ko", "ru"]:')
    p.write_text(s, encoding="utf-8")

# This RU build intentionally uses a version newer than the pinned upstream release.
# SetupPlan then upgrades the existing installation instead of reopening the old copy.
version = root / "VERSION"
upstream_version = version.read_text(encoding="utf-8").strip()
if upstream_version != "1.10.1":
    raise SystemExit(f"Unexpected upstream VERSION {upstream_version}; review RU version bump.")
version.write_text("1.10.2\n", encoding="utf-8")

# Check for Cicada RU releases rather than offering an unlocalized upstream update.
update_checker = root / "windows/src/Cicada.Core/UpdateChecker.cs"
s = update_checker.read_text(encoding="utf-8")
old_feed = "https://api.github.com/repos/wquguru/cicada/releases?per_page=20"
new_feed = "https://api.github.com/repos/PogorelovYD/trans/releases?per_page=20"
if old_feed not in s:
    raise SystemExit("Upstream update feed URL changed; review it before building.")
update_checker.write_text(s.replace(old_feed, new_feed), encoding="utf-8")

print(
    f"Applied Russian UI: {len(translations)} translated keys; "
    f"{len(common)} shared and {len(windows)} Windows keys included."
)
