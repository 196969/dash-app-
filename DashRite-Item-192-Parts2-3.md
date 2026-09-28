# #192 Parts 2 and 3 — the refund cap and the Paid/AR routing

**Base:** 080a6ddc, which the gate confirmed. **Build:** 430d6457.

## Part 2 — the refund cap

A refund cannot exceed what the invoice has received, net of refunds already issued. The amount received is read from the payment records. Above that, the refund is refused with the received amount stated, for example: "Refused — 1004 has received $1,500.00; a refund cannot exceed what was collected".

**Consequence to rule on.** The refund picker, line 31367, lists only invoices marked Paid, and it stays on the proxy by ruling. So a partially paid invoice cannot be chosen for a refund through the screen. The cap is correct and enforced, but for partial payments it is unreachable until the picker is ruled.

## Part 3 — the routing

**The four remaining uses:**
- line 21448: received by customer;
- line 25193: "Projects delivered and collected", a finished count;
- line 26693: days to pay and average fee, from payment dates;
- line 30447: revenue by client or state.

**One helper per class:**

| Class | Helper | Readers routed |
|---|---|---|
| Cash received | `_receiptRows`: one row per payment record, with its amount, date and method | 63 |
| Money still owed | `_openRows`: the outstanding balance | 20 |
| Is this invoice finished | `_invDone`: the balance is zero on a non-void invoice | 29 |

The receipts register and the receipt page now read the payment records, so each receipt names its own payment. The receipt page says "a part payment; $X still due" when the invoice is unfinished.

**Named, left on the proxy:**
- refund eligibility (line 31367), by ruling;
- six readers inside `function(){}` callbacks (lines 23433, 23605, 23628, 23651, 23885 and 23935), where `this` is not the component and the helpers cannot be called safely.

**Found while exercising the classes:**
- The invoice list aged invoices on `status === 'Open'`, so a partially paid invoice read "In progress". It now ages like any open invoice.
- The receipts register printed its method as `p.method || 'Check'`, a default presenting as fact. No payment was ever recorded as a check. It now shows the record's declared "Not recorded".

## Proof

- **The live book.** No lens, verdict, consensus, leverage, binding constraint or trial-balance figure moved. Across fifteen screens compared by text, the only change is the register's method column, "Check" → "Not recorded", which is intended. A one-cent difference on the time-based burn and pace rates came from capture timing: the KPI screen, captured in step, shows the same figure on both builds.
- **A copy with a partial payment** ($400 of $1,000, with a test bank account so the receipt is cash): cash reads $400, AR reads $600, the invoice reads unfinished (and ages as Current), the register lists a $400 receipt with the method "Not recorded", and the trial balance ties at $4,955.92.

The Paid/AR proxy is closed, except for the seven named readers.
