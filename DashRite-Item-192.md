# #192 Parts 2 and 3 — the refund cap and the Paid/AR routing

**Base:** 080a6ddc, which the gate confirmed. **Builds:** 430d6457 (the routing), then 09d76801 (the refund picker). #192 is closed.

## Part 2 — the refund cap

A refund cannot exceed what the invoice has received, net of refunds already issued. The amount received is read from the payment records. Above that, the refund is refused with the received amount stated, for example: "Refused — 1004 has received $1,500.00; a refund cannot exceed what was collected".

**The refund picker is routed (build 09d76801).** It listed only invoices marked Paid, so a partially paid invoice could not be refunded at all. It now lists any non-void invoice whose refundable amount (received minus already refunded) is above zero, and its displayed maximum shows that figure instead of the invoice total. The cap is reachable. On a copy with $400 received on $1,000: $500 was refused ("has received $400.00"), $300 was issued (maximum now $100), $150 was refused ("of which $300.00 is already refunded"), and $100 was issued. The trial balance tied at every step.

**Found while routing it: a silent neighbouring-value substitution.** A requested invoice that was not in the picker fell back to the first listed invoice. On the base, four refunds meant for the partially paid invoice were each issued against 1004, Everlast Welders, and posted to the ledger. Now a requested invoice with nothing refundable selects nothing, and the refund is refused by name ("… has nothing left to refund — nothing was issued").

**Refund eligibility stays the one genuine judgment,** and it is ruled: an invoice is refundable up to the amount received.

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

**Named, left on the proxy, accepted:** six readers inside `function(){}` callbacks (lines 23433, 23605, 23628, 23651, 23885 and 23935). Inside those callbacks `this` is not the component, so the helpers cannot be called safely. **What routing them later needs:** in each enclosing method, bind the component once (`var self = this;`, the pattern `_autofixVM` already uses) and call `self._invDone(...)` / `self._receiptRows(...)`, or convert the callback to an arrow function. Then exercise each one on a copy with a partial payment, as the other 112 were.

**Found while exercising the classes:**
- The invoice list aged invoices on `status === 'Open'`, so a partially paid invoice read "In progress". It now ages like any open invoice.
- The receipts register printed its method as `p.method || 'Check'`. No payment was ever recorded as a check. **Logged as the worst version of this defect: a default presenting as fact reads as evidence.** It now shows the record's declared "Not recorded".
- Both findings are the same class as the rest of the item: a label or default standing in for the thing it describes, found outside the pattern being searched.

## Proof

- **The live book.** No lens, verdict, consensus, leverage, binding constraint or trial-balance figure moved. Across fifteen screens compared by text, the only change is the register's method column, "Check" → "Not recorded", which is intended. A one-cent difference on the time-based burn and pace rates came from capture timing: the KPI screen, captured in step, shows the same figure on both builds.
- **A copy with a partial payment** ($400 of $1,000, with a test bank account so the receipt is cash): cash reads $400, AR reads $600, the invoice reads unfinished (and ages as Current), the register lists a $400 receipt with the method "Not recorded", and the trial balance ties at $4,955.92.

The Paid/AR proxy is closed, except for the seven named readers.
