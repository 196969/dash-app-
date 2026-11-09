#!/usr/bin/env python3
"""PreToolUse hook (Build Stack v4 ch.41 item 3), flat at the repository root. Configuration is read from the item's state file, whose path
is the BUILD_STATE environment variable (set in claude-settings.json); the state file lives outside the repository (Item 381).
Refuses (exit 2) any Edit, Write or MultiEdit: before the Founders 72 verdict on the brief is in the state file; or on a path outside the
state file's config.allowed_paths (the locked paths). Exempt patterns, if any, are permitted without a verdict. Exit 0 permits.
Falls back to build-config.json beside this file when BUILD_STATE is unset (the hotleads-repo layout of Item 422)."""
import fnmatch, json, os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
def refuse(why, path=''): print(f'REFUSED by hook_require_ballot: {why}' + (f'. Target: {path}' if path else ''), file=sys.stderr); sys.exit(2)
sp = os.environ.get('BUILD_STATE')
if sp: sp = os.path.normpath(os.path.join(ROOT, sp))
elif os.path.exists(os.path.join(ROOT, 'build-config.json')): sp = os.path.normpath(os.path.join(ROOT, json.load(open(os.path.join(ROOT, 'build-config.json')))['state_file']))
else: refuse('BUILD_STATE is not set and no build-config.json exists, so no state file can be read')
ev = json.load(sys.stdin)
if ev.get('tool_name') not in ('Edit', 'Write', 'MultiEdit', 'NotebookEdit'): sys.exit(0)
path = os.path.relpath(os.path.abspath(os.path.join(ROOT, (ev.get('tool_input') or {}).get('file_path', ''))), ROOT).replace(os.sep, '/')
if not os.path.exists(sp): refuse(f'no state file at {sp}', path)
try: st = json.load(open(sp))
except Exception as e: refuse(f'state file does not parse ({e})', path)
cfg = st.get('config') or {}
if any(fnmatch.fnmatch(path, p) for p in cfg.get('exempt_patterns', [])): sys.exit(0)
b = (st.get('ballots') or {}).get('brief') or {}
if not (b.get('revision') and b.get('clock') and isinstance(b.get('seats'), list) and b.get('seat_count') == 72 and b['seats']):
    refuse(f'the Founders 72 verdict on the brief of Item {st.get("item")} is not in the state file', path)
if cfg.get('allowed_paths') is not None and path not in cfg['allowed_paths']: refuse(f'{path} is a locked path for Item {st.get("item")}', path)
sys.exit(0)
