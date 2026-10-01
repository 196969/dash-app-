# #199a handoff: CEO checklist

Delivered: index.html, SHA-256 afc4855065fcd6c0c0a689518d983b1b5dcc0fa27a3a3bb6356d4b5367cdede2, 9,213,128 bytes.
Built from 2605ddc545d4e4179ff69229b3d8ba3071f9a699a2b965191c3e88aca6abe948 by tests/build.py. The build is deterministic.

## Codec
Split at '<script type="__bundler/template">' ... '</script>'.
Body = newline + JSON + newline + TWO spaces ('\n  ').
Encode with json.dumps(src, ensure_ascii=False).replace('</', '<\\u002F').
See tests/codec.py.

## What #199a added
- State keys: ceoChecks {} (self-report ticks by check id) and ceocArea '' (area filter). Old autosaves without them read safely.
- Screen ceocheck, "CEO checklist", in the CEO nav group just before CEO reporting. Its nav badge is the missed count.
- Method _ceocVM(s): the 108 checks. Kind and state are derived and cached per state object.
- Today (dash): a card showing the top 5 missed checks, after the welcome card (data-ceoc="today").
- CEO reporting (ceo and cmdxceo): a card listing every missed check, before the five reports (data-ceoc="ceo").
- No quarterly CEO letter screen.

## Hooks for #199b
- 10.5, 10.6 and 10.7 return blind with "waits on #199b". Replace their evaluators once quadrant tags and decisions[].circle exist.

## Tests (python3 + playwright, chromium at /opt/pw-browsers)
- gate.py <html> [sha-prefix]: size, SHA, round-trip and the 8 markers.
- build.py <2605ddc5 html> <out>: applies src/ceoc_* at anchors that must each match once.
- views.py <html>: the screen list (titleMap + nav + view literals). That is 505 at 2605ddc5 and 506 now.
- sweep.py <html> <out.json>: the full battery. Run it on base and build, then compare.
- textdiff.py <a> <b> v1,v2: rendered-text diff for triage.
- checklist_dump.py <html>: every check's id, kind, state, value and basis.
- shots.py <html> [dir]: desktop and phone shots of the checklist, Today and CEO reporting, plus the tick round-trip and filter tests.
- dash.py: shared helpers. It finds the live component by walking React fibers to stateNode.logic.
