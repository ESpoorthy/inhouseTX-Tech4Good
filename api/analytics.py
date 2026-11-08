from datetime import datetime, timezone, timedelta
from decimal import Decimal
from sqlalchemy import select, func
from api.models import Transaction, Budget


def analytics_summary(db, user_id, filters):
    stmt = select(Transaction).where(Transaction.user_id == user_id, Transaction.payment_status.in_(["COMPLETED", "IMPORTED"]))
    for key, col in (("currency", Transaction.currency), ("category", Transaction.category),
                     ("source", Transaction.source)):
        value = filters.get(key)
        if value:
            stmt = stmt.where(col == value)
    if filters.get("merchant"):
        stmt = stmt.where(Transaction.merchant.ilike(f"%{filters['merchant'][:100]}%"))
    status = filters.get("status")
    if status:
        if status not in {"COMPLETED", "IMPORTED"}:
            stmt = stmt.where(Transaction.id == -1)
        else:
            stmt = stmt.where(Transaction.payment_status == status)
    try:
        def parse(value):
            d = datetime.fromisoformat(value)
            return d.replace(tzinfo=timezone.utc) if d.tzinfo is None else d
        start = parse(filters["start"]) if filters.get("start") else None
        end = parse(filters["end"]) if filters.get("end") else None
    except ValueError as exc:
        raise ValueError("Use ISO 8601 date filters.") from exc
    if start:
        stmt = stmt.where(func.coalesce(Transaction.payment_timestamp, Transaction.created_at) >= start)
    if end:
        if len(filters["end"]) == 10:
            end += timedelta(days=1)
        stmt = stmt.where(func.coalesce(Transaction.payment_timestamp, Transaction.created_at) < end)
    transactions = db.scalars(stmt.order_by(func.coalesce(Transaction.payment_timestamp, Transaction.created_at))).all()
    by_currency = {}
    for tx in transactions:
        curr = by_currency.setdefault(tx.currency, {"total": Decimal("0"), "count": 0, "categories": {}, "merchants": {}, "daily": {}, "weekly": {}, "monthly": {}, "largest": [], "recurring": {}})
        amount = Decimal(tx.amount)
        curr["total"] += amount
        curr["count"] += 1
        curr["categories"][tx.category] = curr["categories"].get(tx.category, Decimal("0")) + amount
        merchant = tx.merchant or "Unknown merchant"
        curr["merchants"][merchant] = curr["merchants"].get(merchant, Decimal("0")) + amount
        occurred = tx.payment_timestamp or tx.created_at
        day = occurred.date().isoformat()
        curr["daily"][day] = curr["daily"].get(day, Decimal("0")) + amount
        date_obj = occurred.date()
        monday = (date_obj - timedelta(days=date_obj.weekday())).isoformat()
        month = date_obj.strftime("%Y-%m")
        curr["weekly"][monday] = curr["weekly"].get(monday, Decimal("0")) + amount
        curr["monthly"][month] = curr["monthly"].get(month, Decimal("0")) + amount
        rec = curr["recurring"].setdefault(merchant, {"count": 0, "months": set(), "total": Decimal("0")})
        rec["count"] += 1
        rec["months"].add(month)
        rec["total"] += amount
        curr["largest"].append({"transaction_id": tx.id, "amount": amount, "description": tx.description, "merchant": merchant, "category": tx.category, "date": day})
    budgets = db.scalars(select(Budget).where(Budget.user_id == user_id)).all()
    budget_map = {(b.category, b.currency): b.amount for b in budgets}
    out = []
    for currency, c in sorted(by_currency.items()):
        categories = [{"category": k, "amount": str(v), "share": float(v / c["total"]) if c["total"] else 0,
                       "budget": str(budget_map[(k, currency)]) if (k, currency) in budget_map else None,
                       "budget_utilization": _budget_utilization(db, user_id, k, currency, budget_map[(k, currency)]) if (k, currency) in budget_map else None}
                      for k, v in sorted(c["categories"].items(), key=lambda x: x[1], reverse=True)]
        out.append({"currency": currency, "total": str(c["total"]), "transaction_count": c["count"],
                    "average": str((c["total"] / c["count"]).quantize(Decimal("0.01"))) if c["count"] else "0.00",
                    "categories": categories,
                    "merchants": [{"merchant": k, "amount": str(v)} for k, v in sorted(c["merchants"].items(), key=lambda x: x[1], reverse=True)],
                    "daily": [{"date": k, "amount": str(v)} for k, v in sorted(c["daily"].items())],
                    "weekly": [{"week_start": k, "amount": str(v)} for k, v in sorted(c["weekly"].items())],
                    "monthly": [{"month": k, "amount": str(v)} for k, v in sorted(c["monthly"].items())],
                    "recurring": [{"merchant": k, "transactions": v["count"], "active_months": len(v["months"]),
                                   "average": str((v["total"] / v["count"]).quantize(Decimal("0.01")))}
                                  for k, v in c["recurring"].items() if v["count"] >= 3 and len(v["months"]) >= 3],
                    "largest": [{**x, "amount": str(x["amount"])} for x in sorted(c["largest"], key=lambda x: x["amount"], reverse=True)[:5]]})
    return {"period": {"start": filters.get("start"), "end": filters.get("end")}, "currencies": out,
            "filters": {k: filters.get(k) for k in ("currency", "category", "merchant", "source", "status") if filters.get(k)}}


def _budget_utilization(db, user_id, category, currency, budget):
    now = datetime.now(timezone.utc)
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
    spent = db.scalar(select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        Transaction.user_id == user_id, Transaction.category == category, Transaction.currency == currency,
        Transaction.payment_status.in_(["COMPLETED", "IMPORTED"]),
        func.coalesce(Transaction.payment_timestamp, Transaction.created_at) >= start,
        func.coalesce(Transaction.payment_timestamp, Transaction.created_at) < end))
    return float(Decimal(str(spent)) / Decimal(budget) * 100) if budget else 0
