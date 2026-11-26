#!/usr/bin/env python3
"""Apply the Cicada RU overlay to a clean upstream checkout."""
import json, pathlib, re, sys

root = pathlib.Path(sys.argv[1]).resolve()
overlay = pathlib.Path(__file__).resolve().parents[1]
common_en = root / "Resources/en.lproj/Localizable.strings"
windows_en = root / "windows/src/Cicada/Strings/en.lproj/Windows.strings"
ru_dir = root / "windows/src/Cicada/Strings/ru.lproj"
ru_dir.mkdir(parents=True, exist_ok=True)

def parse(path):
    text = path.read_text(encoding="utf-8")
    return dict(re.findall(r'^"((?:[^"\\]|\\.)*)"\\s*=\\s*"((?:[^"\\]|\\.)*)";', text, re.M))

def quote(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t") + '";'

translations = json.loads((overlay / "ru_windows.json").read_text(encoding="utf-8"))
common = parse(common_en)
windows = parse(windows_en)
(ru_dir / "Localizable.strings").write_text(
    "/* Russian Cicada RU translation. Untranslated entries fall back to English. */\n" +
    "\n".join(f'"{k}" = {quote(translations.get(k, v))}' for k, v in common.items()) + "\n",
    encoding="utf-8")
(ru_dir / "Windows.strings").write_text(
    "/* Russian Windows-specific Cicada UI. */\n" +
    "\n".join(f'"{k}" = {quote(translations.get(k, v))}' for k, v in windows.items()) + "\n",
    encoding="utf-8")

strings = root / "windows/src/Cicada.Core/Strings.cs"
s = strings.read_text(encoding="utf-8")
s = s.replace('/// Loads the table for language ("en", "ja", "ko"; anything else is Chinese)', '/// Loads the table for language ("en", "ja", "ko", "ru"; anything else is Chinese)')
s = s.replace('Language = head is "en" or "ja" or "ko" ? head : "zh-Hans";',
              'Language = head is "en" or "ja" or "ko" or "ru" ? head : "zh-Hans";')
s = s.replace('"ko" => "ko-KR", _ => "zh-CN" }', '"ko" => "ko-KR", "ru" => "ru-RU", _ => "zh-CN" }')
strings.write_text(s, encoding="utf-8")

settings = root / "windows/src/Cicada/SettingsWindow.cs"
s = settings.read_text(encoding="utf-8")
old = '("ko", "한국어")'
if old not in s:
    raise SystemExit("Could not find language picker insertion point in SettingsWindow.cs")
s = s.replace(old, '("ko", "한국어"), ("ru", "Русский")', 1)
settings.write_text(s, encoding="utf-8")

for rel in ("scripts/strings.py", "windows/scripts/strings.py"):
    p = root / rel
    s = p.read_text(encoding="utf-8")
    if rel == "scripts/strings.py":
        s = s.replace('LANGS = ["en", "ja", "ko"]', 'LANGS = ["en", "ja", "ko", "ru"]')
    else:
        s = s.replace('for lang in ["en", "ja", "ko"]:', 'for lang in ["en", "ja", "ko", "ru"]:')
    p.write_text(s, encoding="utf-8")

print("Applied Cicada RU overlay.")
print(f"Common strings: {len(common)}; Windows strings: {len(windows)}; Russian overrides: {len(translations)}")
