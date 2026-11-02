#!/usr/bin/env python3
"""Optionally pre-fill {{PLACEHOLDERS}} in the kit for a specific customer.

Usage:  python3 setup/render.py setup/placeholders.env out/<customer>
Only keys present in the env file are replaced; anything left as {{...}} is listed
so the agent (or you) can fill it later. {REPORT_NONCE} (single braces) is never touched.
"""
import pathlib, re, shutil, sys

if len(sys.argv) != 3:
    sys.exit(__doc__)
env_file, out_dir = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
kit = pathlib.Path(__file__).resolve().parent.parent
values = {}
for line in env_file.read_text().splitlines():
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, v = line.split('=', 1)
        if v.strip():
            values[k.strip()] = v.strip()

if out_dir.exists():
    shutil.rmtree(out_dir)
shutil.copytree(kit, out_dir, ignore=shutil.ignore_patterns('setup', '*.zip'))
left = set()
for f in out_dir.rglob('*'):
    if f.suffix in ('.md', '.html'):
        s = f.read_text()
        for k, v in values.items():
            s = s.replace('{{' + k + '}}', v)
        left |= set(re.findall(r'\{\{([A-Z_]+)\}\}', s))
        f.write_text(s)
print('Rendered to', out_dir)
if left:
    print('Still unfilled (agent fills these at import time):', ', '.join(sorted(left)))
