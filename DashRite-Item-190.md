# #190 — Account 1000's stored balance field carried two meanings

**Logged:** 28 September 2026, in the #186 close-out.
**Resolved:** 28 September 2026, with Option B (one source of truth, rows as the record).
**Class:** Bookkeeping defect, not a display issue.

## What was proven before the fix

The logged double count was a derivation, so it was exercised before anything was fixed. On a disposable copy of the live build, one $1,000 payment through the app's own Confirm payment raised effective cash from $3,000 to $5,000 when it should have reached $4,000. The trial balance went from $7,555.92 = $7,555.92 to $9,555.92 against $8,555.92, out by exactly the payment. The payment entered cash twice: once through the stored field, and once through the invoice's Paid status, which `computeTB` already counts.

A second misposting was also observed. Filing a card-paid expense credited cash instead of a card payable, so cash was understated and the liability was missing.

## What Option B changed

**One formula.** `computeTB` is the only definition of cash: the opening balance, plus collected invoices, less checking expenses, less refunds, plus recorded cash events. A single accessor, `_cashEff(s)`, returns it for any state, including snapshots and simulator projections.

**The stored field is the opening balance, and nothing writes it.** It is $0 as of 10 Aug 2026. Eight writers were changed:

- Confirm payment no longer writes the field; the paid invoice carries the cash.
- Filing an expense credits the card payable its payment method resolves to, or refuses to post.
- Removing an expense reverses the original credit, or refuses when that credit cannot be identified.
- Refunds count through their own rows.
- Batch payments, card payoffs, adjusting entries, prepaid releases and posted anomaly fixes record a cash event instead of writing the field.

**Current-cash readers.** Every reader that treated the field as current cash now reads effective cash. That covers Coverage, the anomaly and fraud scans, the period snapshot, the Founders mindset view, the supply decision layer, the Alert center, the four Council-action views, the self-audit and the simulator.

**The account 1000 drill.** It lists refunds and cash events, so it foots to effective cash.

**The simulator.** It now projects from the whole state on the same cash basis as the books. Previously it cloned 13 state keys, so most lenses read empty inputs, and it credited a projected payment to every income account.

**Load guard.** If the stored field ever differs from the recorded opening balance, the anomaly scan shows "Ledger drift" with the difference. It is held for the owner's ruling and is never normalised.

## Result

The live figures did not move. Effective cash is $3,000.00 and the trial balance ties at $7,555.92, before and after. The same $1,000 payment now takes cash to $4,000 and the trial balance ties at $8,555.92. The three Coverage readings that asserted $0 as fact now read $3,000.

The drift check on the owner's saved state found no drift. Account 1000 showed $3,000.00, with the trial balance tying at $7,555.92.

## Follow-on, 28 September 2026 — batch and partial payments

Both open defects were exercised before they were fixed, and both broke the trial balance.

- **Batch payments.** A $120 ACH item took cash from $3,000 to $2,880 with nothing on the other side, so the trial balance ran $7,435.92 against $7,555.92. An $80 card item vanished with nothing booked. Now every queued item must carry a ledger account to debit, or the whole batch is refused and nothing is paid or recorded. Card items also need the batch card, "AMEX Business ••1005", mapped to the chart; until then they are refused.
- **Partial payments.** $400 against a $1,000 invoice marked the invoice Paid, counted $1,000 as cash, left AR at $0, and ran the trial balance $8,555.92 against $7,955.92. Now a payment records the amount received on the invoice; the invoice reads "Partially paid" with the remainder due until it is covered; cash counts what was received; and the paid date is the real date (it was hard-coded to August).
- **Three more writers**, proven before fixing: tap to pay (both actions) and the mailbox "Payment" intent marked invoices Paid without crediting income, breaking the trial balance by the full amount. All payments now go through one helper, `_applyPayment`. The mailbox applies a payment only when the email names an invoice (it had marked a hard-coded invoice "1038").
- **Disproved:** the booking deposit credits 2100 Accrued liabilities, and the trial balance ties. Whether 2200 Deferred revenue is the better account is a separate question.
- **Two more gaps in the #190 reader enumeration, found by searching for the shape of the cash formula rather than its names:** the render-wide `glCash` (152 references) still used the old formula, and three views (pipeline flow, the Founders supply lens, the Books ribbon) defined "cash" as collected invoices. All now read the one formula.

On live data nothing moved: cash $3,000, trial balance $7,555.92, AR $0, and no lens changed.

## Mappings applied, 28 September 2026

The owner ruled on all six payment methods and five payable accounts. They are applied as two owner-ruling tables in code, so they take effect whatever state the browser has saved.

- **Payment methods.** "Cash" and the Home Depot gift card post to 3000 Owner equity (book). Cards ••4417 and ••1005 are the one business AMEX and post to 2210. All 31 expense rows now resolve (23 to 3000, 8 to 2210). Expense capture now records a card expense as Dr 6110 / Cr 2210, where before it was refused.
- **Payable accounts.** Anthropic debits 6110, Hiscox 6020, and Bookkeeper 6080 "Professional fees (CPA & legal)", the chart's professional-fees account (the ruling named it "Legal & professional fees"). Broward County and Florida Sunbiz stay unmapped, because the chart has no taxes-and-licenses account.

Nothing on the live books moved: trial balance $7,555.92, cash $3,000.00, AR $0, 2210 −$2,572.66, 3000 −$1,983.26, and no lens changed.

## Still open, for the owner

1. **Reclass the Adobe $19.99, held.** The Adobe row on ••4417 was originally credited to 3000, not the card: the ••2002 rows sum to exactly the 2210 balance, and 3000 includes the $19.99. Under the ruling that ••4417 is the AMEX, 2210 is understated and 3000 overstated by $19.99. The correction is Dr 3000 / Cr 2210 $19.99, and the trial balance total would not move. Until it is posted, removing the Adobe row would reverse 2210 while the original credit sits in 3000, which was demonstrated on a copy. The app's own payments profile also labels the business checking account "••4417", which is worth confirming before posting.
2. **Taxes and licenses.** Broward County ($78) and Florida Sunbiz ($138) need a chart account before they can carry one. That is a separate chart decision.
3. **Batch exclusion, no change.** None of the five payables can reach the batch. Broward and Sunbiz are excluded as "Accrued". Anthropic, Hiscox and Bookkeeper are dropped by a hard-coded vendor-and-amount list in `_payablesLive`, not by their state.
4. **Known proxy: invoice status as a stand-in for money received.** It cuts both ways. The 91 "Paid" readers understate collected revenue after a partial payment, and the 32 "not Paid" readers overstate AR (the Books ribbon showed $1,000 against the cockpit's true $600). Neither occurs until a partial payment exists.
5. **Operating cash flow** on the KPI scorecard omits refunds and cash events. It is deferred and latent.
6. **The mailbox stub** still hard-codes invoice "1035", calendar item 2 and one client in its other branches.
7. **Receipt label.** Expense capture stores its receipt as "Attached", but the receipt check accepts only "On file", so captured expenses with receipts are listed as missing one.

## Standing rule this item evidences

A number reads the thing it describes, never a proxy that looks close enough. This is the fifth instance, and the first where the proxy error lived in the books rather than in a report.
