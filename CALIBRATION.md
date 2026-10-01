# pixelsweep.py calibration (accepted 1 Oct 2026)

Rebuilt to the #206 spec after #197's sweep was lost with its container: animation wait, seven-point
covered-node guard, clipped-node skipping, tour dismissed first, 1440x900 at device scale 2.

Runs: b10f1fd6 (508 screens, 64,820 nodes) and e523c98 (504 screens, 63,542 nodes; the last 504-screen
build in branch history, taken as #197's close-out). Both give 260 other-text failures on #197's
screens with identical nodes and causes, so #198-#205 changed none of the counted screens.

Against #197's 228: total similar (+14%); fades 0.45, 0.6 and 0.3 match exactly, 0.55 and 0.5 close
(47 vs 42, 34 vs 27). The ranking shifts by raw node count only because qbxtools (45 accent "Read-only" /
"Opens in Dash", 35 amber "Activates on connect") and connxhub (41 "Connect" at a 50% mix) carry many
identical nodes: a counting difference, not a measurement difference. Ruled accepted.

#197's "60% mix" and "55% mix" do not appear here and are not inside the fade counts (no failing
fade node carries a color-mix). Ruled a #197 naming artifact: #197 named by token definition, this
sweep names by computed colour. Logged; no action.

New screens (never measured by #197), reported separately: ceocheck 22 and hrokr 1, all from the
blind-row fade at 0.78 (ruled: keep the fade; if a row fails, change the blind rows' colour, not the
opacity); timematrix 0; fndxblakely 0.

Also on #197's screens: 14 money/percentage failures; accepted "Plan" x3 and "Owner" x1; 2 coloured-emoji
artifacts, excluded.
