"""Minimal PayPal Orders v2 client, restricted to Sandbox."""
from __future__ import annotations

import os
import json
import time
from datetime import datetime, timezone
from decimal import Decimal
from urllib.parse import urlparse

import requests


class PayPalError(Exception):
    def __init__(self, public_message: str):
        super().__init__(public_message)
        self.public_message = public_message


class PayPalClient:
    base_url = "https://api-m.sandbox.paypal.com"

    def __init__(self, client_id: str, client_secret: str, http=requests):
        self.client_id = client_id
        self.client_secret = client_secret
        self.http = http
        self._token = None
        self._expires_at = 0

    @property
    def configured(self):
        return bool(self.client_id and self.client_secret)

    def _access_token(self):
        if not self.configured:
            raise PayPalError("PayPal Sandbox is not configured.")
        if self._token and time.time() < self._expires_at - 30:
            return self._token
        try:
            response = self.http.post(f"{self.base_url}/v1/oauth2/token", auth=(self.client_id, self.client_secret),
                                      data={"grant_type": "client_credentials"}, timeout=12)
        except requests.RequestException:
            raise PayPalError("PayPal Sandbox could not be reached.") from None
        if response.status_code >= 400:
            raise PayPalError("PayPal Sandbox authentication failed.")
        data = response.json()
        self._token = data["access_token"]
        self._expires_at = time.time() + int(data.get("expires_in", 300))
        return self._token

    def _request(self, method, path, request_id=None, body=None):
        headers = {"Authorization": f"Bearer {self._access_token()}", "Content-Type": "application/json"}
        if request_id:
            headers["PayPal-Request-Id"] = request_id
        try:
            response = self.http.request(method, f"{self.base_url}{path}", headers=headers, json=body, timeout=15)
        except requests.RequestException:
            raise PayPalError("PayPal Sandbox request failed; payment status was not assumed.") from None
        if response.status_code >= 400:
            # Do not expose provider details that may contain request/merchant information.
            raise PayPalError(f"PayPal Sandbox returned HTTP {response.status_code}.")
        return response.json() if response.content else {}

    def create_order(self, amount: Decimal, currency: str, description: str, request_id: str):
        data = self._request("POST", "/v2/checkout/orders", request_id, {
            "intent": "CAPTURE",
            "purchase_units": [{"description": description[:120],
                                "amount": {"currency_code": currency, "value": f"{amount:.2f}"}}],
            "application_context": {"brand_name": "InHouseTX Sandbox", "user_action": "PAY_NOW"},
        })
        approve = next((x.get("href") for x in data.get("links", []) if x.get("rel") in {"approve", "payer-action"}), None)
        if not data.get("id") or not approve:
            raise PayPalError("PayPal response did not contain an order ID and approval link.")
        return {"id": data["id"], "status": data.get("status", "CREATED"), "approve_url": approve}

    def get_order(self, order_id: str):
        return self._request("GET", f"/v2/checkout/orders/{order_id}")

    def capture_order(self, order_id: str, request_id: str):
        data = self._request("POST", f"/v2/checkout/orders/{order_id}/capture", request_id, {})
        unit = next(iter(data.get("purchase_units", [])), {})
        capture = next(iter(unit.get("payments", {}).get("captures", [])), {})
        amount = capture.get("amount", {})
        if not capture.get("id") or not amount.get("value") or not amount.get("currency_code"):
            return {"status": data.get("status", "PENDING"), "capture_id": None,
                    "amount": None, "currency": None, "captured_at": datetime.now(timezone.utc),
                    "merchant": "PayPal Sandbox"}
        stamp = capture.get("create_time")
        parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00")) if stamp else datetime.now(timezone.utc)
        return {"status": capture.get("status", data.get("status", "PENDING")), "order_status": data.get("status"), "capture_id": capture["id"],
                "amount": Decimal(amount["value"]).quantize(Decimal("0.01")),
                "currency": amount["currency_code"], "captured_at": parsed,
                "merchant": unit.get("payee", {}).get("merchant_id") or "PayPal Sandbox"}


def verify_webhook(raw: bytes, event: dict, headers, webhook_id: str, client: PayPalClient) -> bool:
    """Use PayPal's verify-webhook-signature API. Does not accept simulator mock IDs."""
    if not webhook_id or not client.configured:
        return False
    required = {
        "transmission_id": headers.get("Paypal-Transmission-Id"),
        "transmission_time": headers.get("Paypal-Transmission-Time"),
        "cert_url": headers.get("Paypal-Cert-Url"),
        "auth_algo": headers.get("Paypal-Auth-Algo"),
        "transmission_sig": headers.get("Paypal-Transmission-Sig"),
    }
    if not all(required.values()):
        return False
    cert = urlparse(required["cert_url"])
    if cert.scheme != "https" or not cert.hostname or not (cert.hostname == "paypal.com" or cert.hostname.endswith(".paypal.com")):
        return False
    try:
        token = client._access_token()
        fields = {**required, "webhook_id": webhook_id}
        body = "{" + ",".join(json.dumps(k) + ":" + json.dumps(v) for k, v in fields.items())
        body += ',"webhook_event":' + raw.decode("utf-8") + "}"
        response = client.http.post(f"{client.base_url}/v1/notifications/verify-webhook-signature",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            data=body.encode("utf-8"), timeout=15)
        if response.status_code >= 400:
            return False
        result = response.json()
    except (PayPalError, requests.RequestException, UnicodeDecodeError, ValueError):
        return False
    return result.get("verification_status") == "SUCCESS"
