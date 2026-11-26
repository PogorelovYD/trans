#!/usr/bin/env python3
"""Apply Russian UI translations and locale support to an upstream Cicada checkout."""
import json, pathlib, re, sys
root = pathlib.Path(sys.argv[1]).resolve()
overlay = pathlib.Path(__file__).resolve().parent
def parse(path):
    text = path.read_text(encoding="utf-8")
    return dict(re.findall(r'^"((?:[^"\\]|\\.)*)"\s*=\s*"((?:[^"\\]|\\.)*)";', text, re.M))
def quote(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t") + '";'
translations = json.loads((overlay / "ru_windows.json").read_text(encoding="utf-8"))
ru_common = root / "Resources/ru.lproj"
ru_windows = root / "windows/src/Cicada/Strings/ru.lproj"
ru_common.mkdir(parents=True, exist_ok=True)
ru_windows.mkdir(parents=True, exist_ok=True)
common = parse(root / "Resources/en.lproj/Localizable.strings")
windows = parse(root / "windows/src/Cicada/Strings/en.lproj/Windows.strings")
for name, table in (("Localizable.strings", common), ("Windows.strings", windows)):
    (ru_dir / name).write_text(
        "/* Russian translation; untranslated entries use English fallback. */\n" +
        "\n".join(f'"{k}" = {quote(translations.get(k, v))}' for k, v in table.items()) + "\n",
        encoding="utf-8")
p = root / "windows/src/Cicada.Core/Strings.cs"
s = p.read_text(encoding="utf-8")
s = s.replace('Language = head is "en" or "ja" or "ko" ? head : "zh-Hans";',
              'Language = head is "en" or "ja" or "ko" or "ru" ? head : "zh-Hans";')
s = s.replace('"ko" => "ko-KR", _ => "zh-CN" }', '"ko" => "ko-KR", "ru" => "ru-RU", _ => "zh-CN" }')
p.write_text(s, encoding="utf-8")
p = root / "windows/src/Cicada/SettingsWindow.cs"
s = p.read_text(encoding="utf-8")
if '("ko", "한국어"), ("ru", "Русский")' not in s:
    if '("ko", "한국어")' not in s: raise SystemExit("Language picker not found")
    s = s.replace('("ko", "한국어")', '("ko", "한국어"), ("ru", "Русский")', 1)
p.write_text(s, encoding="utf-8")
for rel in ("scripts/strings.py", "windows/scripts/strings.py"):
    p = root / rel
    s = p.read_text(encoding="utf-8")
    s = s.replace('LANGS = ["en", "ja", "ko"]', 'LANGS = ["en", "ja", "ko", "ru"]')
    s = s.replace('for lang in ["en", "ja", "ko"]:', 'for lang in ["en", "ja", "ko", "ru"]:')
    p.write_text(s, encoding="utf-8")
print(f"Applied Russian UI: {len(translations)} translated keys; {len(common)} shared and {len(windows)} Windows keys included.")
