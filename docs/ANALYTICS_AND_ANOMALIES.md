# Analytics and Anomaly Signals

## Analytics

All financial aggregation is deterministic and uses `Decimal` amounts. Only `COMPLETED` PayPal/Sandbox records and `IMPORTED` CSV rows enter spend totals; pending and denied payments are retained but excluded. Totals, average, count, categories, merchant totals, daily/weekly/monthly series, largest payments, recurring merchant candidates, and monthly budget utilization are returned per currency. Date-only end filters are inclusive. Current-month budget use is compared only with current-month recorded items.

Filters supported by `/api/analytics/summary` include date range, category, merchant, currency, source and status. `/api/transactions` provides the same filters with pagination. CSV imports require amount, currency, description and merchant; date is optional, rows are limited to 100 and 1 MB per request. Imported rows use `IMPORTED` status and are never labeled PayPal-verified.

## Anomaly detector

The anomaly module checks per-user, per-currency history for category amounts at least 2.5 times the prior category median (with a minimum absolute difference) after at least three prior examples, and repeated same-merchant payments less than an hour apart after repeated history. It stores a score, severity, historical baseline and review state. Users can mark a signal reviewed or dismiss it.

The output says unusual activity is not a fraud determination. No alert is created when there is insufficient category history. These are explainable statistical heuristics, not a validated fraud model. Rates, category-spend spikes, and sophisticated seasonality are not implemented.
