# Dash CRM — manifest re-baseline (Chair ruling, 2026-11-01)

DashRite Advisory LLC · dash-app- · branch `branch` · head `1708ae6` · **this upload holds 3 files**: manifest.json, gate.py, dash-rebaseline-report.md.

## Gate at the open

`gate.py check` exited **1** on two files. Every other listed file matched on both sources.

| File | In the manifest (Pass #298) | Live |
|---|---|---|
| links.html | 39,726 bytes | 12,112 bytes |
| signature.html | 60,388 bytes | 111,190 bytes |

Both files were replaced by an upload at 20:47 on 29 October that came from outside the build’s deliveries.

## The Chair’s condition, measured before adopting them

Both files were opened in Chromium.

**signature.html:**
- Title: “DashRite — Email Signature Installer — TEdick”.
- The mark renders (a 520×223 image) and the text is complete.
- No script errors. The file closes on `</html>`.

**links.html:**
- Title: “DashRite Advisory — Live Links”.
- 35 distinct links, every one answering **200**.
- The footer is present and the file closes on `</html>`.

Neither file is truncated, so both were adopted.

**One content finding, not damage:** links.html’s footer still carries the retired tagline “Built Fast. Built Right.”, which “Built RITE!” replaced on 13 August.

## The re-baseline

`manifest.json` is rewritten with all 158 files and dated 2026-11-01 22:23 UTC. The reason is recorded in its `pass` field. `gate.py check --local .` exits 0 against the folder.

**A writer fault, found and fixed in the same pass.** `gate.py write` stored each file under its basename, so `battery/battery.py` and `battery/control.py` would have entered the manifest as `battery.py` and `control.py` — files that don’t exist at the root. It now stores the relative path. Before and after are both kept.

## The finding (register)

Two delivered files were replaced out of band, and the manifest didn’t know. The gate caught it after the fact; a declared-manifest check at delivery would have caught it before. That is F72 repo recommendation (1), arriving as an incident.

## Dash survival markers

| Marker | Reading |
|---|---|
| Invoices 1004 and 1005 | both Paid |
| portalhome | 1 |
| webleads | 22 |
| fndxcoverage | 10 |
| _lensBoardKeys | 15 |
| Bella with rawSpeak | present |
| Screen ids dashiq, memory, autopilot, cmdxmindset | all present |
| brandmark.py | “Dash · RITE Edition” rendered |

## The encoder, proven before any edit

`json.dumps(s, ensure_ascii=False).replace('</', '<\u002F')` round-trips the template payload byte for byte. It needs the surrounding whitespace captured: `\n` before the payload and `\n  ` after it.

## Build A — not started, and why

The data Build A would read exists:
- a `posts` array (a social calendar with day strings such as “Sun 7 Sep”);
- the `webleads` surface (visits, leads and rate rows).

**What stops it:** Build A means editing a 7 MB decoded source across five anchors (nav, titleMap, flag, view model, template) and then running the full battery. That conversation has become very long, and I can’t carry an edit of that size reliably to the end of it. It starts in a fresh session, on this gate and this encoder.
