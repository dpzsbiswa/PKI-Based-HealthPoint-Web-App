from database import db
from sqlalchemy import text
from app import app

with app.app_context():
    db.session.execute(text('ALTER TABLE appointments ADD COLUMN IF NOT EXISTS cancellation_remarks TEXT;'))
    db.session.commit()
    print("Migration complete: cancellation_remarks column added (if it did not exist).") 