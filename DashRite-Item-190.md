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

## Invented digits cleared, 28 September 2026

The owner ruled that ••4417 and ••1005 are not the last four digits of any real account or card; the app invented them. Both Everlast payments landed in the owner's personal checking account, and no business bank account has ever been opened.

This pass was built on the live build, ce1ee200. The closing build 522004fc was never uploaded, so the Adobe reclass (je-r190) was never posted to the live book and has not been posted now. Carried forward from that pass: the restore fix, account 6090 with Broward County and Florida Sunbiz mapped to it, and the state-based payables filter.

- **Mapping tables.** ••4417 and ••1005 are gone from them entirely.
- **Expense captures.** Expense capture, the command bar and email filing now record Owner-paid, which posts to 3000. The capture dialog states it: "Paid by — the default while no business bank account or company card is on file". Entering a real card on the profile overrides it.
- **Corrections to the owner's saved book.** These are applied once after load, without touching the seed fingerprint, and each is written to the audit trail:
  - the Adobe row reads "Not recorded";
  - the owner draw account is cleared;
  - je-5's memo reads "Tommys Express (payment method not recorded)", and its posting to 3000 stands;
  - the profile's bank name, account label, routing number and card ••1005 are cleared.
- **Only where the evidence exists:**
  - a book carrying je-r190 gets a reversal, je-r190r, with both entries kept in the journal;
  - a capture credited to 2210 under the void ruling, found by its own audit line, is moved to 3000 with a journal entry.
- **Card reconciliation** now counts rows that resolve to 2210 (AMEX ••2002, $2,572.66, difference $0.00). Previously it counted the invented "Card ••4417" label.
- **ACH files** are refused when no business bank account is on file.

Nothing on the live book moved: trial balance $7,555.92, 2210 −$2,572.66, 3000 −$1,983.26, and no lens changed.

## Owner draw and receipt destination, 28 September 2026

The owner ruled that both Everlast payments were an owner draw, and that no payment should be counted as business cash while no business account exists.

- **Owner draw posted.** Dr 3000 / Cr 1000, $3,000, as journal entry je-r190d. It is applied once after load and guarded on the evidence: both Everlast invoices are Paid at $1,500. Effective cash went from $3,000 to $0, and runway from 1.1 months to 0.0. Owner equity moved from a $1,983.26 credit to a $1,016.74 debit: the owner has taken out $1,016.74 more than put in. The trial balance fell from $7,555.92 to $5,572.66, and ties. That fall is presentation, not an error.
- **Lens readings that moved:** Capital 17.9% → 0%, and Grow on collected cash 89.8% → 70%. The verdict, consensus (15 of 39), leverage (14%) and binding constraint (Expose the waste) did not move.
- **Receipt destination.** While no business bank account is on file, a payment still credits income, but it posts as an owner draw (a debit to 3000) rather than cash. This applies whether the payment is recorded in the payment dialog, by tap to pay or from the mailbox. The dialog states it: "Received into — the default while no business bank account is on file: Owner's personal account — owner draw". Entering a real bank account on the profile makes the next payment cash, and the field then reads "Deposit to".
- **The payment dialog's hard-coded fields are gone:** the "1000 · Business checking" destination, which named an account that was never opened, and the date "13 Nov 2026". It now shows the real date.

## Card reclass, 28 September 2026 — #190 closed

The owner ruled that there is no company card: AMEX ••2002 is a personal card used for business. The reclass and the mapping were one change.

- **Reclass posted.** Dr 2210 / Cr 3000, $2,572.66, as journal entry je-r190a. It is applied once after load, and only where the ••2002 expense rows sum to exactly what 2210 carries. It survived reloads, a saved book from the live build, and a saved book from before the owner draw, where both corrections applied exactly once each.
- **Mapping moved in the same change.** ••2002 now resolves to 3000. Captures, card batches and reversals of those rows land in owner equity and cannot recreate the liability.
- **Results:**
  - the trial balance fell from $5,572.66 to $4,555.92, and ties; the fall is presentation, not an error;
  - 2210 went from −$2,572.66 to $0;
  - 3000 went from a $1,016.74 debit to a $1,555.92 credit;
  - cash stayed at $0;
  - no lens reading moved, and the verdict, consensus (15 of 39), leverage (14%) and binding constraint (Expose the waste) are unchanged.

## Logged and unfixed, by decision

These stay logged by the owner's decision, not by oversight.

1. **Leverage cannot show an empty bank.** It reads cash through one factor, Grow on collected cash, diluted past visibility. Taking cash from $3,000 to $0 moved that factor from 89.8% to 70% but moved the 42-factor geometric mean by under a tenth of a point, so the index still read 14%. An index that barely moves when the bank goes to zero reports a number that cannot be acted on.
2. **Email filing adds expense rows without posting them.** The command-bar flow has the same shape by code.
3. **The reconciliation's owner-paid row** counts only the label "Owner personal", which no row carries.
4. **Reduced motion.** Opening the expenses screen runs brief colour and fade transitions for under half a second even under reduced motion.
5. **The Accrued batch rule:** whether accrued payables should reach a batch.
6. **The two-way status proxy:** after a partial payment, "Paid" readers understate collected revenue and "not Paid" readers overstate AR.
7. **Operating cash flow** on the KPI scorecard omits refunds and cash events.
8. **The mailbox stub** hard-codes invoice "1035", calendar item 2 and one client.
9. **The receipt label:** captures store "Attached", while the receipt check accepts only "On file".
10. **The remaining contrast causes** from earlier accessibility work.

## Standing rule this item evidences

A number reads the thing it describes, never a proxy that looks close enough. This is the fifth instance, and the first where the proxy error lived in the books rather than in a report.
