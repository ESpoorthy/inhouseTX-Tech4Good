# Demo setup

## Local dashboard only

1. Install requirements in a Python virtual environment.
2. Copy `.env.example` to `.env` and set a strong `SECRET_KEY`; leave `PAYPAL_MODE=sandbox`.
3. Run `python scripts/migrate.py` then `python -m api.app`.
4. In a second terminal run `python scripts/seed_demo.py` and retain the printed one-time password.
5. Open the local app and sign in. All seeded rows say `synthetic_demo`; this path requires no PayPal and makes no payment.

## PayPal Sandbox checkout

1. Create a Sandbox REST app in PayPal Developer Dashboard and configure local `.env` with its client ID and secret plus webhook ID. Keep these out of screenshots and source control.
2. Use a public HTTPS tunnel or deployed HTTPS URL for `/api/paypal/webhooks`, configure the relevant capture event subscriptions, and store that webhook ID in the environment.
3. Create/use a PayPal Sandbox buyer account. Set an amount and description in checkout, approve using the buyer account, and return to the app. The server performs the capture/status check; a browser return alone does not establish payment success.
4. Confirm payment status and transaction source in UI, then inspect server-side webhook/audit state without exposing secrets.

Credentials, buyer account, public webhook route, and network reachability are external prerequisites. Do not use real payment accounts or cards.
