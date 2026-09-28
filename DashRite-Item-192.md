# #192 — Frontier labels closed; the Paid/AR proxy classified

**Base:** 8d47edd9, which the gate confirmed. No code change was made in this session: the live build is unchanged.

## Item 1 — the Frontier labels: closed as not reproduced

In #191 both Frontier screens (cmdxfrontier and fndxfrontier) were measured by rendered pixel and by the sampler. No node on either screen failed by either measure (93 and 138 text nodes). The two labels logged at 4.38 do not reproduce on the current build. They are closed as not reproduced and taken off the log, with nothing fixed.

## Item 2 — the Paid/AR proxy, Phase 1: classification (read-only)

All 121 readers were classified by the question each asks, taken from what it does with the answer, not from where it sits.

| Class | Question | Readers | Answer it should read |
|---|---|---|---|
| Cash received | collected revenue, cash flow, weekly revenue, days to pay, deposits held, concentration by customer | 65 | the amount received |
| Money still owed | AR, aging buckets, open lists, collections | 27 | the amount outstanding |
| Is this invoice finished | status tags, pay-or-receipt actions, completion | 13 | finished only when the balance is zero |
| Counts | numbers of paid or open invoices, weekly counts | 9 | convention: a partially paid invoice counts as open, not paid, because it is unfinished |
| Genuine judgments | see below | 3 | left on the proxy and named |
| Not yet read | see below | 4 | classified once their use is read |

**The shape behind the original count of 106.** Most sites declare one list, `paid = invoices.filter(status === 'Paid')`, and reuse it for two or three questions in the same function: a collected sum, a by-customer map, and sometimes a count. Classified by site, that looked like 106 judgments. Classified by use, it is four questions.

**The three genuine judgments, left on the proxy:**
1. **Refund eligibility (line 31364).** Whether a partially paid invoice can be refunded, and up to what, is a policy question.
2. **The receipts register (line 36270) and the receipt page (line 36289).** These list invoices as receipts. With partial payments an invoice has several payments, but the book stores only a cumulative `received` per invoice. Listing payments needs payment-level records, which is a data decision rather than a helper.

**The four not yet read (lines 21448, 25193, 26693, 30447).** Each declares a paid list whose use sits more than eight lines below. They are unclassified, not exceptions.

**A caveat on method.** The first pass of the classification is shape-based: sums, accumulations, counts, lists and tests, placed by what follows each status test. Each class must be confirmed on a copy with a partial payment before anything is routed.

## Remaining: Phase 2

- Read the four unread uses.
- Build one helper per class: received (`_invReceived`, which already exists), outstanding (`_invBalance`, which already exists), finished (new: the balance is zero on a non-void, non-zero invoice), and the count convention.
- Route all 118 classified readers through their class helper, and leave the three judgments on the proxy, named.
- Prove that nothing moves on the live book, which has no partial payment. Then prove on a copy with a partial payment that cash reads received, AR reads outstanding, the invoice reads unfinished, and the trial balance ties.
- Full battery.
