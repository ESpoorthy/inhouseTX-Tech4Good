# PayPal Sandbox Integration

## Current implementation

The integration uses the PayPal REST API with the Sandbox base URL `https://api-m.sandbox.paypal.com` and Orders v2. The server exchanges a Sandbox client ID/secret for an OAuth 2.0 access token. The client secret never reaches the browser; the public client ID is returned only to load PayPal's JavaScript SDK.

The browser SDK creates an order through the backend, gives the buyer the PayPal approval experience, and then sends the approved order ID back to the backend for capture. A browser approval callback is not treated as payment success. The server checks capture-level status, amount, currency and capture ID before storing the transaction. `PENDING` and `DENIED` capture states are retained without counting as completed spending. A verified completion webhook can reconcile a pending capture to completed.

API routes:

- `POST /api/paypal/orders`
- `GET /api/paypal/orders/{order_id}`
- `POST /api/paypal/orders/{order_id}/capture`
- `POST /api/paypal/webhooks`

The app accepts Sandbox demo checkout amounts in USD only, from 0.01 through 10,000.00 USD. Orders and captures have separate stable PayPal request IDs and database uniqueness constraints. Repeated application idempotency keys return the original local order. Capture retries reuse the original capture request ID. Capture and webhook persistence are additionally guarded by unique PayPal order/capture/event IDs.

The webhook endpoint uses PayPal's `verify-webhook-signature` API, requires a configured webhook ID and required transmission headers, restricts `cert_url` to HTTPS PayPal hostnames, and preserves the incoming raw event JSON bytes in the verification body. Verified event IDs are unique, so delivery replays are acknowledged without duplicate transactions. The handler reconciles only events whose order, capture, amount and currency match a locally created order.

## Official API review

The implementation follows PayPal's current Orders v2 server-side create/approve/capture process and Sandbox REST base URL. PayPal documents OAuth client credentials for REST API access and recommends `PayPal-Request-Id` for idempotent POSTs. PayPal's webhook guide documents server verification and event delivery retries. The JavaScript SDK is loaded directly from PayPal as required by the SDK guide.

- [Orders API integration](https://developer.paypal.com/api/rest/integration/orders-api)
- [PayPal REST API authentication and requests](https://developer.paypal.com/api/make-api-requests)
- [Orders v2 reference](https://developer.paypal.com/api/orders/v2)
- [JavaScript SDK configuration](https://developer.paypal.com/sdk/js/configuration/)
- [Webhook overview](https://developer.paypal.com/api/rest/webhooks/)
- [Webhook signature integration](https://developer.paypal.com/api/rest/webhooks/rest/)
- [PayPal request idempotency](https://developer.paypal.com/api/rest/requests/)
- [PayPal AI Hackathon rules](https://paypalaihackathon.devpost.com/rules)

PayPal API details can change; recheck these official docs and Sandbox behavior before final recording/submission.

## Verification status

The PayPal HTTP boundary is unit-tested with mocked responses for order creation, successful capture, duplicate capture, amount mismatch, failed capture, pending capture, webhook replay, invalid signature and pending-to-completed webhook reconciliation. The HTTP API shape and state logic are exercised locally.

**No live Sandbox checkout or webhook has been verified in this environment.** PayPal Sandbox client credentials and a registered reachable HTTPS webhook URL were not available. Never call mocked outcomes live PayPal transactions. The checkout page shows the setup requirement and does not display success when PayPal is unconfigured or capture fails.

## Setup for live Sandbox verification

1. Create a free PayPal Developer account and a REST Sandbox app.
2. Add its Sandbox client ID and secret to the backend environment as `PAYPAL_CLIENT_ID` and `PAYPAL_CLIENT_SECRET`.
3. Create a Sandbox buyer account in the Developer Dashboard.
4. For webhook testing, register `https://<public-https-host>/api/paypal/webhooks` on the same REST app, subscribe to `PAYMENT.CAPTURE.PENDING`, `PAYMENT.CAPTURE.COMPLETED`, and `PAYMENT.CAPTURE.DENIED`, and set its ID as `PAYPAL_WEBHOOK_ID`.
5. Set `PAYPAL_MODE=sandbox`, restart, and check **Settings → PayPal Sandbox**.
6. Use the Sandbox buyer account to approve checkout and verify the capture and saved transaction. Never substitute a production credential or live account.

The Devpost rules require a functional demo that judges can run, a public open-source code repository, and a public YouTube demo under three minutes. A live hosted URL is optional if complete reproducible setup instructions are supplied, but the source code must be published by the project owner before submission.
