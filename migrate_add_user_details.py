from database import db
from sqlalchemy import text
from app import app

with app.app_context():
    db.session.execute(text('ALTER TABLE users ADD COLUMN IF NOT EXISTS gender VARCHAR(10);'))
    db.session.execute(text('ALTER TABLE users ADD COLUMN IF NOT EXISTS age INTEGER;'))
    db.session.execute(text('ALTER TABLE users ADD COLUMN IF NOT EXISTS address VARCHAR(255);'))
    db.session.execute(text('ALTER TABLE users ADD COLUMN IF NOT EXISTS contact_number VARCHAR(20);'))
    db.session.commit()
    print("Migration complete: gender, age, address, and contact_number columns added (if not already present).") 