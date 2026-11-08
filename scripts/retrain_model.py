"""Train a candidate model with individually selected owner corrections."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api.app import create_app
from api.database import get_db
from api.models import Feedback, Transaction
from model.train import train_model
from sqlalchemy import select

parser=argparse.ArgumentParser(description="Default run creates a candidate only; --promote is an explicit operator action.")
parser.add_argument("--feedback-ids", nargs="*", type=int, default=[], help="Specific reviewed correction row IDs to include.")
parser.add_argument("--promote", action="store_true", help="Write the artifact active at next app startup after reviewing evaluation output.")
parser.add_argument("--allow-regression", action="store_true", help="Override the active-model macro F1 guard after manual review.")
args=parser.parse_args()
app=create_app()
examples=[]
with app.app_context():
    db=get_db()
    for fid in args.feedback_ids:
        feedback=db.get(Feedback,fid)
        tx=db.get(Transaction,feedback.transaction_id) if feedback else None
        if not feedback or not tx:
            parser.error(f"Feedback ID {fid} does not exist.")
        examples.append((tx.description,feedback.corrected_category))
_,_,report=train_model(feedback_rows=examples,promote=args.promote,allow_regression=args.allow_regression)
print(f"Candidate: {report['artifact']}")
print(f"Evaluated on held-out synthetic rows: accuracy={report['models'][report['selected_model']]['accuracy']:.4f}, macro_f1={report['models'][report['selected_model']]['macro_f1']:.4f}")
print(f"User corrections included: {len(examples)}")
if args.promote:
    print("Promoted artifact. Restart the backend to load it.")
else:
    print("Not promoted. Review reports/model_evaluation.json, then rerun with --promote if acceptable.")
