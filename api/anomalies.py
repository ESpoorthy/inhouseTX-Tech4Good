from datetime import datetime, timezone
from statistics import median
from sqlalchemy import select
from api.models import Transaction, Anomaly


def detect_anomalies(db, user_id):
    txs = db.scalars(select(Transaction).where(Transaction.user_id == user_id,
                                               Transaction.payment_status.in_(["COMPLETED", "IMPORTED"])).order_by(Transaction.created_at)).all()
    by_currency = {}
    for tx in txs:
        by_currency.setdefault(tx.currency, []).append(tx)
    found = []
    for currency, rows in by_currency.items():
        for i, tx in enumerate(rows):
            prior = [r for r in rows[:i] if r.category == tx.category]
            reasons = []
            score = 0.0
            baseline = {"category": tx.category, "currency": currency, "history_count": len(prior)}
            amount = float(tx.amount)
            if len(prior) >= 3:
                values = [float(x.amount) for x in prior]
                center = median(values)
                baseline["category_median"] = round(center, 2)
                if center > 0 and amount >= max(center * 2.5, center + 25):
                    score += min(0.85, 0.55 + (amount / center - 2.5) * 0.1)
                    reasons.append(f"{amount:.2f} {currency} is more than 2.5× the previous {tx.category} median ({center:.2f} {currency}).")
            same = [r for r in rows[:i] if r.merchant.lower() == tx.merchant.lower() and r.merchant]
            if len(same) >= 2 and tx.created_at and (tx.created_at - same[-1].created_at).total_seconds() < 3600:
                score = max(score, 0.75)
                reasons.append("Multiple payments to the same merchant appeared within an hour.")
            if len(prior) < 3:
                continue
            if score < 0.5:
                continue
            existing = db.scalar(select(Anomaly).where(Anomaly.transaction_id == tx.id))
            if not existing:
                anomaly = Anomaly(user_id=user_id, transaction_id=tx.id, score=round(min(score, 0.99), 2),
                                  severity="high" if score >= 0.75 else "medium",
                                  explanation=" ".join(reasons) + " This is an unusual-spending signal, not a fraud finding.",
                                  baseline=baseline)
                db.add(anomaly)
                db.flush()
                existing = anomaly
            if existing.review_status == "open":
                found.append({"id": existing.id, "transaction_id": tx.id, "amount": str(tx.amount),
                              "currency": currency, "merchant": tx.merchant, "category": tx.category,
                              "score": existing.score, "severity": existing.severity,
                              "explanation": existing.explanation, "suggested_action": "Review this payment and mark it reviewed or dismiss this alert.",
                              "review_status": existing.review_status})
    db.commit()
    return found
