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

**Readers.** Every reader that treated the field as current cash now reads effective cash. That covers Coverage, the anomaly and fraud scans, the period snapshot, the Founders mindset view, the supply decision layer, the Alert center, the four Council-action views, the self-audit and the simulator.

**The account 1000 drill.** It lists refunds and cash events, so it foots to effective cash.

**The simulator.** It now projects from the whole state on the same cash basis as the books. Previously it cloned 13 state keys, so most lenses read empty inputs, and it credited a projected payment to every income account.

**Load guard.** If the stored field ever differs from the recorded opening balance, the anomaly scan shows "Ledger drift" with the difference. It is held for the owner's ruling and is never normalised.

## Result

The live figures did not move. Effective cash is $3,000.00 and the trial balance ties at $7,555.92, before and after. The same $1,000 payment now takes cash to $4,000 and the trial balance ties at $8,555.92. The three Coverage readings that asserted $0 as fact now read $3,000.

The drift check on the owner's saved state found no drift. Account 1000 showed $3,000.00, with the trial balance tying at $7,555.92.

## Still open, for the owner

1. **Unresolved payment methods.** "Card ••4417" is not on the chart of accounts. Five seeded expenses carry a payment method with no account: three marked "Cash", one on Card ••4417, and one gift card. Capturing a new card expense is refused until ••4417 is mapped, and removing any of those five is refused rather than guessed.
2. **Batch payments have no credit side.** Payables are not on the ledger, so paying them moves cash with nothing on the other side, and the trial balance would break. It is derived by construction and was not exercised. Where paid payables should post needs a ruling.
3. **Partial payments.** Confirm payment marks the whole invoice Paid even when the amount received is smaller, so cash counts the full invoice. This existed before #190 and is unchanged.
4. **Operating cash flow.** Operating cash flow on the KPI scorecard still omits refunds and cash events. There are none today, so no figure is affected yet.

## Standing rule this item evidences

A number reads the thing it describes, never a proxy that looks close enough. This is the fifth instance, and the first where the proxy error lived in the books rather than in a report.
