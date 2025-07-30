#!/usr/bin/env python3
"""
Migration script to add payment table for eSewa integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models.payment import Payment

def migrate_add_payment_table():
    """Add payment table to database"""
    with app.app_context():
        try:
            # Create the payment table
            Payment.__table__.create(db.engine, checkfirst=True)
            print("✓ Payment table created successfully!")
            
            # Verify the table exists
            from sqlalchemy import text
            result = db.session.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'payments')"))
            if result.scalar():
                print("✓ Payment table verified in database")
            else:
                print("❌ Payment table not found in database")
                
        except Exception as e:
            print(f"❌ Error creating payment table: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("Starting payment table migration...")
    success = migrate_add_payment_table()
    if success:
        print("🎉 Payment table migration completed successfully!")
    else:
        print("💥 Payment table migration failed!")
        sys.exit(1) 