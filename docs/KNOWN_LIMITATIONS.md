# Known limitations and external actions

## External actions needed before final Devpost submission

1. Provide/configure PayPal Developer Sandbox app client ID, client secret, webhook ID, buyer test account, and a public HTTPS webhook target. Then run and record a genuine create/approve/capture/webhook demo. Current API tests mock PayPal responses.
2. Review the implementation and submission package, then authorize/push the branch to the public GitHub repository. No remote write was performed.
3. Choose a public demo host and provide its deployment secrets/domain; deploy and validate TLS, persistence, health, and webhook delivery. No deployment was performed.
4. Record a concise public YouTube video under the current Devpost rules and add the URL. No video was recorded or uploaded.
5. Complete the Devpost project form, add public repository/demo links and submit before the deadline. No external account was accessed and no submission was made.

## Technical constraints

- Current user sessions are signed cookies and rate limiting is in process memory. Use a shared session/rate-limit store for horizontally scaled deployment.
- The schema initializer supports a small hackathon setup; migration evolution is manual and not production migration tooling.
- The fallback model is trained from synthetic descriptions. Metrics must not be generalized to real payment data.
- Analytics are based on records captured/imported by this app. The PayPal connection is checkout/order workflow, not broad account transaction-history access.
- Anomaly rules are small-sample heuristics and flag unusual behavior, never confirmed fraud.
- Optional LLM phrasing has no live-provider verification in this environment; deterministic answers remain available.
- Automated tests do not replace deployment security review, accessibility testing, privacy review, or actual Sandbox checks.
- Dependency installation was blocked by package registry DNS/network restrictions in the implementation environment; checks used installed packages.
