# Deployment guide

## Current state

The Flask app serves both JSON endpoints and the static browser UI, so the prototype can be deployed as one web service. This repository has not been deployed or connected to a live Sandbox app. The local SQLite default is suitable only for local evaluation; use PostgreSQL for a public persistent demo.

## Container

Build and run:

```sh
docker build -t inhouse-tx .
docker run --rm -p 3001:3001 \
  -e PORT=3001 -e SECRET_KEY='replace-with-random-secret' \
  -e DATABASE_URL='postgresql+psycopg://user:password@host:5432/inhouse_tx' \
  -e PAYPAL_MODE=sandbox \
  inhouse-tx
```

Set secrets using the host’s secret manager, never image build args. Add PayPal client credentials and webhook ID only in the deployment secret store. Configure an HTTPS webhook URL in PayPal Developer Dashboard and allow outbound HTTPS access to PayPal. Set `COOKIE_SECURE=true`, a narrow `FRONTEND_ORIGIN`, and a strong unique `SECRET_KEY`.

## Startup and persistence

The entrypoint initializes missing schema at startup. For new installations, use `python scripts/migrate.py` before serving traffic. The included initial migration establishes the same tables; later schema changes currently require a reviewed migration script. `/api/health` is a liveness response; `/api/ready` attempts a database query and should be used for readiness.

Use a managed PostgreSQL service with backups and TLS. Do not use ephemeral container storage for SQLite. Configure a single deployment instance unless session storage and rate limiting are moved to shared stores: current signed-cookie sessions and in-memory rate limiting are process-local.

## Frontend

The frontend is dependency-free static HTML/CSS/JS served by Flask. The PayPal JS SDK script is loaded from `www.paypal.com` at runtime using the server-provided public client ID; client secret remains server-only. No frontend build is required.

## Before public demo

- Run the complete documented checks.
- Set the environment variables listed in `.env.example` through the host.
- Verify TLS, secure cookies, CORS/origin, database persistence, readiness, and secret redaction.
- Configure Sandbox webhook URL and event subscriptions, then verify an actual Sandbox capture and event delivery.
- Confirm that the hosting platform permits outbound PayPal calls and inbound PayPal webhooks.

No live deployment or actual Sandbox transaction is claimed by this documentation.

## Render deployment

`render.yaml` defines the web service in Singapore on Render's free plan. The web service deploys the repository's `main` branch with Gunicorn and uses `/api/ready` as its readiness check. It references the existing `inhouse-tx-postgres` database through Render's database connection reference, so the database URL is not stored in this repository. Keep the Blueprint file on the deployment branch; do not merge it into `main` as part of deployment setup.

The Blueprint generates `SECRET_KEY` in Render. It intentionally leaves PayPal credentials empty and marks those values as manually managed so later Blueprint syncs do not overwrite credentials entered in the Render Dashboard. Set rotated Sandbox values for `PAYPAL_CLIENT_ID` and `PAYPAL_CLIENT_SECRET` in the service's Environment page. Keep `PAYPAL_MODE=sandbox`. `PAYPAL_WEBHOOK_ID` can remain empty until webhook verification is configured; checkout and capture do not require it. `FRONTEND_ORIGIN` is set to the deployed service's exact HTTPS origin. The application serves its frontend and API from the same origin.

The current service is [inhouse-tx-mkmu](https://inhouse-tx-mkmu.onrender.com), deployed from `main` at commit `b2c7f9651d5bbb929e7994b09511e975b8632e67`. `/`, `/api/health`, and `/api/ready` returned HTTP 200 after deployment; readiness reported `database=ok`. The expected origin was accepted and an unrelated origin received HTTP 403. Readiness reports `paypal_configured=false` until the rotated Sandbox client ID and secret are added in Render.

The free web service may spin down when idle, and the free Postgres instance expires after 30 days. These free-tier resources are suitable for evaluation, not durable production storage. Before a public judging demo, confirm the database is active and test readiness, account registration, Sandbox OAuth/order creation, and capture end to end. No actual PayPal capture is claimed here; a Blueprint alone does not prove a deployment is healthy.
