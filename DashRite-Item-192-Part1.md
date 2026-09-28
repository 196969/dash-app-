# #192 Phase 2, Part 1 — payment records

**Base:** 8d47edd9, which the gate confirmed. **Build:** 080a6ddc.

## What changed

- **Payment records.** Each payment is now recorded under `connectors.payments` as `{ id, invoice, date, amount, method }`. State stays at 264 keys and the seed is not edited, so no saved book is discarded.
- **Records are the source.** `_invReceived` sums an invoice's records. The cumulative `received` field is still written, as a derived total. It is read only for an invoice with no record at all, which means a simulator projection or a book before its first load.
- **Every payment path appends a record.** That covers the payment dialog, both tap-to-pay actions (method "Tap to pay") and the mailbox. Where no method is known, the record reads "Not recorded".
- **Existing books.** Records were created once after load, under the flag `rulings190.paymentsV1`, with an audit line: `pay-1004-1` (1 September 2026, $1,500) and `pay-1005-1` (5 September 2026, $1,500). Both have the method "Not recorded". The method was never captured, so it is declared rather than invented.

## Proof

- **A saved-book round trip, run first.** A book saved under 8d47edd9 was loaded under this build. It gained exactly the two records, kept its own data, and did not change on a second reload. The trial balance stayed at $4,555.92.
- **The live book.** Every invoice's received figure equals the sum of its records, with zero mismatches. No lens, verdict, consensus, leverage or binding constraint moved.
- **Two payments against one invoice, on a copy.** $400 by dialog (the invoice is Partially paid, balance $600), then $600 by tap to pay (Paid, balance $0): two records summing to $1,000, and the trial balance tied throughout.

## Remaining in #192 Phase 2

- **Part 2, the refund cap.**
- **Part 3, the routing:** read the four remaining uses, add `finished`, confirm each class on a copy, route the 118 readers, and leave the 3 judgments named on the proxy. The receipts register and receipt page can now read the payment records.
