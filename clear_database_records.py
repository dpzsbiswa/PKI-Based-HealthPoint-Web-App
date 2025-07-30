#!/usr/bin/env python3
"""
Script to clear all records from the database tables
"""

import os
import sys
import time
from sqlalchemy import text

def create_app():
    """Create Flask app for database operations"""
    from flask import Flask
    from database import db, init_app
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 
        'postgresql://user:password@localhost/doctorpatient'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db = init_app(app)
    return app, db

def wait_for_db(max_retries=30):
    """Wait for database to be ready"""
    app, database = create_app()
    
    for attempt in range(max_retries):
        try:
            with app.app_context():
                database.session.execute(text('SELECT 1'))
                print("✅ Database connection successful!")
                return app, database
        except Exception as e:
            print(f"⏳ Database connection attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                print("❌ Failed to connect to database after all retries")
                print("Please ensure the database is running:")
                print("1. Start Docker: sudo systemctl start docker")
                print("2. Start database: sudo docker-compose up -d db")
                sys.exit(1)

def clear_all_records():
    """Clear all records from all tables"""
    app, database = wait_for_db()
    
    try:
        with app.app_context():
            # Import models
            from models.user import User
            from models.file import File
            from models.appointment import Appointment
            from models.payment import Payment
            
            print("🗑️  Clearing all records from database...")
            
            # Delete records in order to respect foreign key constraints
            payment_count = database.session.query(Payment).count()
            database.session.query(Payment).delete()
            print(f"✅ Deleted {payment_count} payment records")
            
            file_count = database.session.query(File).count()
            database.session.query(File).delete()
            print(f"✅ Deleted {file_count} file records")
            
            appointment_count = database.session.query(Appointment).count()
            database.session.query(Appointment).delete()
            print(f"✅ Deleted {appointment_count} appointment records")
            
            user_count = database.session.query(User).count()
            database.session.query(User).delete()
            print(f"✅ Deleted {user_count} user records")
            
            # Commit all changes
            database.session.commit()
            print("✅ All records cleared successfully!")
            print(f"📊 Summary: {user_count} users, {appointment_count} appointments, {file_count} files, {payment_count} payments deleted")
            
    except Exception as e:
        print(f"❌ Error clearing records: {e}")
        database.session.rollback()
        sys.exit(1)

if __name__ == '__main__':
    print("🚀 Starting database record clearing process...")
    clear_all_records() 