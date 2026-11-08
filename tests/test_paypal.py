from datetime import datetime, timezone
from decimal import Decimal
from api.paypal import PayPalError
from tests.conftest import post

def test_order_creation_and_capture_idempotency(app, client, signed_in, monkeypatch):
    pp=app.extensions["paypal"]
    monkeypatch.setattr(pp,"create_order",lambda amount,currency,description,key:{"id":"ORDER-TEST-1","status":"CREATED","approve_url":"https://www.sandbox.paypal.com/checkoutnow?token=ORDER-TEST-1"})
    monkeypatch.setattr(pp,"capture_order",lambda order_id,key:{"status":"COMPLETED","capture_id":"CAPTURE-1","amount":Decimal("18.50"),"currency":"USD","captured_at":datetime.now(timezone.utc),"merchant":"Test merchant"})
    r=post(client,signed_in,"/api/paypal/orders",json={"amount":"18.50","currency":"USD","description":"Sandbox order"})
    assert r.status_code==201 and r.json["mode"]=="sandbox"
    cap=post(client,signed_in,"/api/paypal/orders/ORDER-TEST-1/capture",json={})
    assert cap.status_code==200 and cap.json["status"]=="COMPLETED"
    assert cap.json["transaction"]["source"]=="paypal_sandbox"
    replay=post(client,signed_in,"/api/paypal/orders/ORDER-TEST-1/capture",json={})
    assert replay.status_code==200 and replay.json["idempotent_replay"] is True
    assert client.get("/api/transactions").json["total"]==1

def test_order_validation(client, signed_in):
    assert post(client,signed_in,"/api/paypal/orders",json={"amount":"0","currency":"USD"}).status_code==400
    assert post(client,signed_in,"/api/paypal/orders",json={"amount":"5","currency":"EUR"}).status_code==400

def test_order_creation_idempotency(app,client,signed_in,monkeypatch):
    pp=app.extensions["paypal"];calls=[]
    monkeypatch.setattr(pp,"create_order",lambda *a:(calls.append(1) or {"id":"ORDER-REPLAY","status":"CREATED","approve_url":"https://www.sandbox.paypal.com/approve"}))
    headers={"X-CSRF-Token":signed_in,"Idempotency-Key":"checkout-intent-001"}
    first=client.post("/api/paypal/orders",json={"amount":"5.00","currency":"USD"},headers=headers)
    replay=client.post("/api/paypal/orders",json={"amount":"5.00","currency":"USD"},headers=headers)
    assert first.status_code==201 and replay.status_code==200
    assert first.json["order_id"]==replay.json["order_id"] and replay.json["idempotent_replay"] is True
    assert len(calls)==1

def test_capture_failure_never_creates_transaction(app,client,signed_in,monkeypatch):
    pp=app.extensions["paypal"]
    monkeypatch.setattr(pp,"create_order",lambda *a:{"id":"ORDER-FAIL","status":"CREATED","approve_url":"https://www.sandbox.paypal.com/approve"})
    monkeypatch.setattr(pp,"capture_order",lambda *a:(_ for _ in ()).throw(PayPalError("capture failed")))
    post(client,signed_in,"/api/paypal/orders",json={"amount":"22.00","currency":"USD"})
    r=post(client,signed_in,"/api/paypal/orders/ORDER-FAIL/capture",json={})
    assert r.status_code==502
    assert client.get("/api/transactions").json["total"]==0

def test_pending_capture_is_persisted_and_webhook_promotes_it(app,client,signed_in,monkeypatch):
    pp=app.extensions["paypal"]
    monkeypatch.setattr(pp,"create_order",lambda *a:{"id":"ORDER-PENDING","status":"CREATED","approve_url":"https://www.sandbox.paypal.com/approve"})
    monkeypatch.setattr(pp,"capture_order",lambda *a:{"status":"PENDING","capture_id":"CAPTURE-PENDING","amount":Decimal("8.00"),"currency":"USD","captured_at":datetime.now(timezone.utc),"merchant":"Test merchant"})
    post(client,signed_in,"/api/paypal/orders",json={"amount":"8.00","currency":"USD"})
    captured=post(client,signed_in,"/api/paypal/orders/ORDER-PENDING/capture",json={})
    assert captured.status_code==202 and captured.json["status"]=="PENDING"
    assert captured.json["transaction"]["payment_status"]=="PENDING"
    import api.app as app_module
    monkeypatch.setattr(app_module,"verify_webhook",lambda *a:True)
    event={"id":"EVENT-PENDING-COMPLETE","event_type":"PAYMENT.CAPTURE.COMPLETED","resource":{"id":"CAPTURE-PENDING","status":"COMPLETED","amount":{"value":"8.00","currency_code":"USD"},"supplementary_data":{"related_ids":{"order_id":"ORDER-PENDING"}}}}
    assert client.post("/api/paypal/webhooks",json=event).status_code==200
    tx=client.get("/api/transactions").json["items"][0]
    assert tx["payment_status"]=="COMPLETED" and tx["paypal_capture_id"]=="CAPTURE-PENDING"

def test_webhook_signature_preserves_original_event_bytes(app,monkeypatch):
    from api.paypal import verify_webhook
    class Response:
        status_code=200
        def json(self):return {"verification_status":"SUCCESS"}
    class HTTP:
        def post(self,url,headers,data,timeout):
            assert b'"id": "event-raw"' in data
            assert b'"webhook_event":{' in data
            return Response()
    pp=app.extensions["paypal"]
    monkeypatch.setattr(pp,"_access_token",lambda:"sandbox-token")
    pp.http=HTTP()
    raw=b'{"id": "event-raw", "event_type":"PAYMENT.CAPTURE.COMPLETED"}'
    headers={"Paypal-Transmission-Id":"t","Paypal-Transmission-Time":"now","Paypal-Cert-Url":"https://api.sandbox.paypal.com/cert","Paypal-Auth-Algo":"SHA256withRSA","Paypal-Transmission-Sig":"sig"}
    assert verify_webhook(raw,{"id":"event-raw"},headers,"webhook-test-id",pp)

def test_amount_mismatch_rejected(app,client,signed_in,monkeypatch):
    pp=app.extensions["paypal"]
    monkeypatch.setattr(pp,"create_order",lambda *a:{"id":"ORDER-MISMATCH","status":"CREATED","approve_url":"https://www.sandbox.paypal.com/approve"})
    monkeypatch.setattr(pp,"capture_order",lambda *a:{"status":"COMPLETED","capture_id":"CAPTURE-MISMATCH","amount":Decimal("9.00"),"currency":"USD","captured_at":datetime.now(timezone.utc),"merchant":"Test"})
    post(client,signed_in,"/api/paypal/orders",json={"amount":"10.00","currency":"USD"})
    r=post(client,signed_in,"/api/paypal/orders/ORDER-MISMATCH/capture",json={})
    assert r.status_code==409 and client.get("/api/transactions").json["total"]==0

def test_webhook_signature_and_event_idempotency(app,client,monkeypatch):
    import api.app as app_module
    monkeypatch.setattr(app_module,"verify_webhook",lambda *a:True)
    event={"id":"EVT-1","event_type":"PAYMENT.CAPTURE.PENDING","resource":{"id":"capture"}}
    headers={"Paypal-Transmission-Id":"transmission"}
    first=client.post("/api/paypal/webhooks",json=event,headers=headers)
    second=client.post("/api/paypal/webhooks",json=event,headers=headers)
    assert first.status_code==200 and second.status_code==200
    assert second.json["status"] in {"already_processed","already_received"}

def test_invalid_webhook_rejected(app,client,monkeypatch):
    import api.app as app_module
    monkeypatch.setattr(app_module,"verify_webhook",lambda *a:False)
    r=client.post("/api/paypal/webhooks",json={"id":"bad","event_type":"PAYMENT.CAPTURE.COMPLETED"})
    assert r.status_code==401

def test_webhook_cert_host_validation(app,monkeypatch):
    from api.paypal import verify_webhook
    pp=app.extensions["paypal"]
    def should_not_call(*a,**k):raise AssertionError("must reject non-PayPal certificate hosts before network")
    monkeypatch.setattr(pp,"_request",should_not_call)
    headers={"Paypal-Transmission-Id":"t","Paypal-Transmission-Time":"now","Paypal-Cert-Url":"https://paypal.com.attacker.invalid/cert","Paypal-Auth-Algo":"SHA256withRSA","Paypal-Transmission-Sig":"sig"}
    assert verify_webhook(b"{}",{"id":"e"},headers,"webhook-test-id",pp) is False
