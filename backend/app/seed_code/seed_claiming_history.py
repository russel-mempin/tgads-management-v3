import csv, os
from sqlmodel import Session, select
from app.database import engine
from app.models import JobOrder, JobItem, ClaimingHistory
from app.utils.utils import to_int
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "seed_data", "claiming_history.csv")

def seed_claiming_history_from_csv(file_path: str = CSV_PATH):
    with Session(engine) as session, open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            jo_number = session.exec(
                select(JobOrder).where(JobOrder.jo_number == row["jo_number"])
            ).first()
            item_id = session.exec(
                select(JobItem).where(JobItem.item_id == row["item_id"])
            ).first()
            if not jo_number:
                print(f"JO Number not found: {row['jo_number']}")
                continue
            if not item_id:
                print(f"Item ID not found: {row['item_id']}")
                continue
            if to_int(row["pcs_claimed"]) > item_id.quantity:
                print(f"Pieces claimed is greater than item quantity.")
            claiming_history = ClaimingHistory(
                date_claimed=datetime.fromisoformat(row["date_claimed"]),
                name=row["name"],
                pcs_claimed=to_int(row["pcs_claimed"]),
                job_order_id=jo_number.id,
                job_item_id=item_id.id
            )
            session.add(claiming_history)
        session.commit()
