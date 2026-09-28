# #191 — Clearing the logged items

**Run:** 28 September 2026, in one session, as one build.
**Base:** 177fbadb, which the gate confirmed.
**Result:** all ten items are closed across two builds: fda20227 (items 1–8, and item 10 measured) and 8d47edd9 (the T3 change and item 9). #191 is closed.

## Pass A — ledger correctness

1. **Email filing and the command bar: fixed.**
   - *Proven on the base:* filing a $45 Figma receipt email recorded "Anthropic $200", whatever the email said, and posted nothing. The command bar also added unposted rows.
   - *After:* both post through the capture path, owner-paid, Dr the category's account / Cr 3000. An email without an amount, vendor or category is refused with the reason.
   - *Trial balance:* $4,555.92 before. On a copy, $4,600.92 after the $45 email and $4,605.92 after a $50 command-bar entry, tied each time.
2. **Operating cash flow and the cash-flow statement: fixed.**
   - *Proven on the base:* the statement's tie check compared begin + net change against end, where net change is defined as end − begin, so it could never fail. It said "Ties" while showing $3,000 of operating cash against a $0 change, and again after a refund and an ACH payment.
   - *After:* operating cash includes refunds and non-draw cash events, owner draws appear as financing (−$3,000), and the tie is a real sum. It held live, after a $100 refund, and after a $78 ACH payment.
   - The KPI scorecard's operating cash flow is corrected the same way, but it feeds only a coverage ratio that reads "Not applicable", so nothing there is displayed.
   - *Trial balance:* no posting; unchanged.
   - **Logged as the finding of this pass.** The tie compared a figure against itself, so it could never fail, and it said "Ties" three times while false. That is the proxy class in its most dangerous form: a check that always passes. It is the fifth instance, after the security control, the vacancy check, the author name and the pair count.
3. **The Paid/AR status proxy: left logged, by ruling.** It is not fixable without deciding, per reader, whether a partially paid invoice counts as paid. One helper (`_invReceived` / `_invBalance`) serves both sides. But only 15 of 121 readers are plain sums; the other 106 are conditions, lists, lookups and counts, where treating a partially paid invoice as paid or open is a judgment per reader. Converting only the sums would leave the book answering the same question two ways. No partial payment exists live, so no figure is wrong today.

## Pass B — labels that did not match their fields

4. **Receipts: fixed by reading the field.** Every row stores the label "Attached", while 17 readers tested for "On file", which nothing writes. The field is the stored image in `state.shots`, and readers now test that. Accepting "Attached" instead would have turned 31 true "missing" readings false, since the seeded rows have no stored file. *Proven on the base:* a capture with a stored photo still read "No receipt". It now reads as on file, and the seeded rows correctly still read as missing.
5. **Owner-paid reconciliation: fixed.** It matched the label "Owner personal", which no row carries, and read $0 / $0. It now compares rows resolving to 3000 ($4,535.93) with owner contributions in 3000 ($4,555.92). That is a true $19.99 difference, the Adobe row whose method is "Not recorded".
6. **The Accrued batch rule: a defect, fixed.** "Accrued" was a label with no accrual behind it: 2100 is $0. An unpaid bill is still payable, so Broward County and Florida Sunbiz now reach the batch. Their debit side is 6090. Sending ACH is refused while no business bank account exists; before, the batch would have pushed cash negative. With a test account, the payment debits 6090 and the trial balance ties.
7. **The mailbox stub: cleared.** A stranger's email no longer writes an invented note onto the Everlast contact, reopens calendar item 2, marks the non-existent invoice 1035, or stamps the audit trail "13 Nov 13:55". Each branch now acts only on what the email carries, and does nothing otherwise.

## Pass C — presentation

8. **Reduced motion: correction and fix.** Screenshots at 40 ms and 1.5 s after opening the expenses screen are pixel-identical on both builds. There was never visible motion, and the earlier log overstated it. The only defect was a dead selector for the `ckfade` rule, which React's style serialisation never matched; it is fixed.
   *Owner's note:* the owner's report of this transition was wrong, and the correction is accepted. The real defect was a reduced-motion selector that never matched.
9. **Contrast, re-derived from scratch by rendered pixel on build fda20227.** Ten screens, about 1,150 text nodes. Every node was also checked for being fully on screen and on top; two early failures were the measurer's own artifacts (a clipped node and a covered node) and were removed.
   - **Found before fixing:**
     - header separators at opacity 0.55, on every screen;
     - the trial balance's Dr/Cr at 0.35;
     - the BD pipeline "0" at 0.5;
     - a placeholder dash at a 66% mix;
     - the 10 px off-pace line, at 4.44.
   - **The BD pipeline "0":** its cause is `dueStyle: … 'opacity:.5'`, applied through a template binding. The sampler ignores opacity, so it could never find it.
   - **Fixed:** 0.55 → 0.8, 0.35 → 0.75 and 0.5 → 0.78, with their order kept; the dash mix 55% → 75% at its 7 sites; the pace line 10 px → 11 px, with no colour change.
   - **After:** 0 failures by pixel on all ten screens.
   - **Not reproduced:** the two Frontier labels at 4.38. No node on either Frontier screen fails by pixel or by sampler.
   - **Sampler artifacts, labelled and not fixed:** "Dash · RITE Edition" and "CEO" (1.0 by sampler, 6.52 and 5.69 by pixel), "$3,000" (2.23 against 5.90) and the gradient hub titles (1.0 against about 11.5).
   - **Accepted as found:** "Owner" and "Plan". No completed-item fade was touched.

## Pass D — leverage (measure only)

10. **Correction:** two of the 42 factors are named for cash. Cash scoreboard holds at 20% whether cash is $3,000 or $0, so it does not respond. Only Grow on collected cash does.

| Treatment | Cash $3,000 | Cash $0 | Swing |
|---|---|---|---|
| T1 as built | 14.3% | 14.2% | 0.1 pt |
| T2 cash weighted (Capital as a factor, ×3) | 14.6% | 11.9% | 2.7 pt |
| T3 cash excluded, stated | 13.7% | 13.6% | 0.1 pt |

**Ruled: T3, built in 8d47edd9 as a change of measurement, not a correction.** The index now uses 41 factors; its method line states that cash is excluded and read by Capital; and the Super screen counts 21 core factors. The index moved from 14.2% to 13.6%, but it still displays as 14% because the council rounds to whole percent. Nothing else moved: verdict, consensus, binding constraint, every lens and the trial balance. The original recommendation read: It keeps the index measuring operating leverage and says plainly, beside the number, that cash is read by Capital. Its honest cost: the headline never reflects the bank, it drops 0.6 points today, and readers must look at Capital for liquidity. T2 makes an empty bank visible, but it turns leverage into a blend whose weight (×3) is a judgment, not a measurement. It would also fall on every owner draw, which is timing, not leverage. Nothing was changed.

## Lenses

No lens reading moved on the live books in any pass.
