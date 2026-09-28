# #190 — Account 1000's stored balance field carries two meanings

**Logged:** 28 September 2026, in the #186 close-out.
**Class:** Bookkeeping defect, not a display issue.
**Status:** Open. It is logged in this pass and deliberately not fixed; reconciliation gets its own pass with its own evidence.
**Decision required:** Maintain the field or remove it. A field that exists and lies is worse than no field.

## What the field is, and what it is used as

`computeTB` treats the stored `balance` on account 1000 as the **opening balance**:

> effective cash = stored 1000 balance + cash collected (paid invoices) − cash paid (business-checking expenses)

The account 1000 ledger view labels the same value "Opening balance, 10 Aug 2026". Read that way, $0 is plausibly correct for a firm that opened with nothing.

The rest of the code does not hold to that meaning:

- **Readers treat it as current cash.** These include the Capital × every-unlock cross-check, the Capital enrichment, the target-list enrichment, the anomaly and fraud scans, the Founders simulator, and several view-models that fall back to it when effective cash is missing.
- **Writers treat it as a running balance.** Batch payment, refunds, filing an expense and marking an invoice paid all add to or subtract from it. Marking an invoice paid also sets its status to Paid, which `computeTB` already counts as cash in, so a real payment would be counted twice. This holds by construction from the code; it was not exercised in this pass.

On the current ledger the stored field reads **$0.00** and effective cash reads **$3,000.00**. The trial balance ties at $7,555.92 only because it uses the effective figure.

## Evidence: wrong readings it has caused

Four were caught and corrected in #186:

1. Branson's survivability wording, which read "a stated downside inside $0 of cash."
2. Branson's Capital cross-check, which read "Cash in account 1000 is $0."
3. The top-five text on the live council page and in the Word document, which read "nothing in the operating account."
4. The operator's own ruling, "account 1000 reads $0," which carried into the #186 stage description as "$0 cash."

Three are live in `index.html` now, on Founders · Coverage. They were found while logging this item and are left unfixed by ruling:

5. The cross-check "Capital × every unlock" reads "Cash $0 against $4,556 spend."
6. The Capital enrichment reads "$0 cash · $4,556 spend · $3,000 revenue" and calls it "a true zero on real data" that outranks every other enrichment.
7. The Coverage lead line repeats it: "a true zero on real data outranks every enrichment below it."

## What stays in place until the decision

The live council page keeps its current next step: reconcile account 1000, whose stored balance field reads $0.00 against $3,000.00 of effective cash.

## Standing rule this item evidences

A number reads the thing it describes, never a proxy that looks close enough. This is the fourth instance, and the first to catch the operator's own ruling as well as the code.
