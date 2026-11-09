#!/usr/bin/env python3
"""Stop hook (Build Stack v4 ch.41 item 2), flat at the repository root. Runs the gate and the item's evals named in the state file's config
(BUILD_STATE; falls back to build-config.json) on the bytes as they stand. Any non-zero exit blocks the stop (exit 2); every exit code is read from the program."""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.abspath(__file__)); sp = os.environ.get('BUILD_STATE')
cfg = json.load(open(os.path.normpath(os.path.join(ROOT, sp))))['config'] if sp else json.load(open(os.path.join(ROOT, 'build-config.json')))
bad = []
for cmd in [cfg['gate']] + cfg['evals']:
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    tail = (r.stdout.strip().splitlines() or r.stderr.strip().splitlines() or ['no output'])[-1]
    print(f'{" ".join(cmd)} -> exit {r.returncode} · {tail[:160]}', file=sys.stderr)
    if r.returncode != 0: bad.append(' '.join(cmd))
if bad: print('STOP REFUSED: ' + '; '.join(bad), file=sys.stderr); sys.exit(2)
sys.exit(0)
