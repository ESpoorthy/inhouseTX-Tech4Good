# Security Notes

## Implemented

- Passwords are hashed with Werkzeug's password hashing helpers; sessions are signed, `HttpOnly`, `SameSite=Lax` cookies. Set a strong random `SECRET_KEY`; production refuses the development default and forces secure cookies.
- Private routes require a session. Transaction/order/feedback/budget/anomaly queries scope to the authenticated user. The user ID is never accepted from ordinary request payloads.
- Authenticated mutations require a session-bound CSRF token in `X-CSRF-Token`. CORS is not opened; the UI is same-origin. `FRONTEND_ORIGIN`, when set, rejects different origins.
- Payment secrets remain server-only. The app refuses non-Sandbox `PAYPAL_MODE`. Provider status, amount and currency are checked server-side; client approval does not mean capture success.
- PayPal order/capture/webhook IDs are idempotency constrained. Webhook signatures are checked through PayPal before event processing. Raw webhook bodies are not stored or logged.
- SQLAlchemy parameterization protects ordinary query construction. CSV uploads have size/row/column/type checks; transaction descriptions are treated as data.
- Simple per-process IP rate limiting, safe API errors, content-type/nosniff, frame/referrer policy, and restrictive CSP headers are enabled.
- The insights agent receives aggregates, not raw transaction descriptions, and has no payment tools.

## Limits and deployment controls

This is a hackathon demonstration, not a production-ready financial service. Password login has no email verification, MFA, account recovery or durable distributed rate limiter. SQLite is suitable for local demo only. Use HTTPS, `COOKIE_SECURE=true`, a unique secret, private database, restrictive ingress, and managed secret storage in a hosted environment. The in-memory rate limiter is process-local and can be bypassed by multiple workers. The app's declarative schema initialization is not a safe auto-migration system for evolving existing production databases. No formal penetration test, dependency vulnerability scan, privacy review or external security audit was performed.

Do not commit `.env`, Sandbox credentials, real transaction data, generated database files or user exports. Review repository status before any public push. No live payments are supported or authorized by this code.
