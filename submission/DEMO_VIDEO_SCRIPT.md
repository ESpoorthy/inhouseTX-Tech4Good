# Video voiceover draft (under 3 minutes)

**0:00–0:15** — “This is InHouseTX, PayPal AI Spending Intelligence. The original Team Tech4Good project categorised transaction text; this hackathon version connects that intelligence to a Sandbox payment flow.”

**0:15–0:35** — Show the dashboard. “Here are persisted transactions, categories, and trends. The source badge distinguishes synthetic demo data from PayPal Sandbox records, and all totals stay within their currency.”

**0:35–0:55** — If Sandbox credentials are configured, create an order, approve it with a Sandbox buyer, and return. “The server captures and verifies the order with PayPal. The browser alone cannot mark a payment successful.” If this has not been verified, omit the success claim and show a clear setup note instead.

**0:55–1:20** — Open a transaction. “The category prediction includes the model confidence and words that contributed to its decision. Low-confidence results are available for human review.”

**1:20–1:40** — Correct a category. “The correction is recorded with the original prediction and model version. Retraining is an explicit offline process, not automatic.”

**1:40–2:05** — Show analytics and budget. “We can filter by dates, merchant, category, source, and status. Amounts in separate currencies are not added together.”

**2:05–2:25** — Show anomaly. “This item is unusual relative to the available history. It is an alert for review, not a fraud verdict.”

**2:25–2:50** — Ask a spending question. “The totals come from deterministic analytics; language generation only explains those facts and cannot initiate a payment.”

**2:50–3:00** — Close. “InHouseTX combines PayPal Sandbox verification with explainable transaction intelligence. The repository includes setup, testing, security, and known-limitations documentation.”

Record actual behavior, add captions where possible, keep the published edit under the current Devpost video limit, and add the final URL to the Devpost form.
