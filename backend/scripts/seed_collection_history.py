"""
Seed 600–900 CollectionExecutionEvents for the last 30 days.
Run from the backend/ directory:
    python scripts/seed_collection_history.py
"""
import os, sys, random
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
    DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)

with Session(engine) as db:
    bins = db.execute(text(
        "SELECT id, type, area_name FROM waste_bin WHERE is_active IS TRUE ORDER BY id"
    )).mappings().all()
    vehicles = db.execute(text(
        "SELECT id, plate_number FROM vehicle WHERE is_active IS TRUE ORDER BY id"
    )).mappings().all()

    if not bins or not vehicles:
        print("No bins or vehicles found. Run seed_vehicles first.")
        sys.exit(1)

    now = datetime.now(timezone.utc)
    events = []
    for bin_row in bins:
        # each bin collected 1–4 times in the last 30 days
        n = random.randint(1, 4)
        days_used = random.sample(range(1, 31), min(n, 30))
        for d in days_used:
            ts = now - timedelta(days=d, hours=random.randint(6, 20), minutes=random.randint(0, 59))
            vehicle = random.choice(vehicles)
            events.append({
                "collection_route_id": 1,          # placeholder route
                "event_type":          "collection",
                "timestamp":           ts,
                "waste_bin_id":        bin_row["id"],
                "vehicle_id":          vehicle["id"],
                "fill_level_before":   random.randint(40, 100),
            })

    # delete existing seed events to allow re-running
    db.execute(text("DELETE FROM collection_execution_event WHERE event_type = 'collection'"))

    # ensure at least one CollectionRoute with id=1 exists as FK placeholder
    existing = db.execute(text("SELECT id FROM collection_route LIMIT 1")).fetchone()
    if existing:
        placeholder_id = existing[0]
        for e in events:
            e["collection_route_id"] = placeholder_id
    else:
        print("No collection_route rows found — create one assignment first, then re-run this script.")
        sys.exit(1)

    db.execute(
        text("""
            INSERT INTO collection_execution_event
                (collection_route_id, event_type, timestamp, waste_bin_id, vehicle_id, fill_level_before)
            VALUES
                (:collection_route_id, :event_type, :timestamp, :waste_bin_id, :vehicle_id, :fill_level_before)
        """),
        events,
    )
    db.commit()
    print(f"Seeded {len(events)} collection events.")
