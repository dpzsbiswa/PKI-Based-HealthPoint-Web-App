#!/usr/bin/env python3
"""
Database Check Script for HealthPoint Application
Checks database connectivity and table creation
"""

import sys
import os
from sqlalchemy import text

def check_database_connection():
    """Check if database connection works"""
    print("🔍 Checking database connection...")
    
    try:
        from app import app, db
        
        with app.app_context():
            # Test basic connection
            result = db.session.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            
            # Check if tables exist
            tables = ['users', 'appointments', 'files', 'payments']
            for table in tables:
                try:
                    result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"✅ Table '{table}' exists with {count} records")
                except Exception as e:
                    print(f"❌ Table '{table}' error: {e}")
            
            return True
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def check_payment_table():
    """Check payment table structure"""
    print("\n🔍 Checking payment table structure...")
    
    try:
        from app import app, db
        from models.payment import Payment
        
        with app.app_context():
            # Check if payment table has required columns
            columns = [
                'id', 'appointment_id', 'transaction_uuid', 'amount', 
                'tax_amount', 'total_amount', 'product_code', 'status',
                'esewa_transaction_code', 'esewa_ref_id', 'signature',
                'created_at', 'updated_at'
            ]
            
            for column in columns:
                try:
                    result = db.session.execute(text(f"SELECT {column} FROM payments LIMIT 1"))
                    print(f"✅ Column '{column}' exists in payments table")
                except Exception as e:
                    print(f"❌ Column '{column}' missing: {e}")
            
            return True
    except Exception as e:
        print(f"❌ Payment table check error: {e}")
        return False

def check_appointment_table():
    """Check appointment table structure"""
    print("\n🔍 Checking appointment table structure...")
    
    try:
        from app import app, db
        from models.appointment import Appointment
        
        with app.app_context():
            # Check if appointment table has required columns
            columns = [
                'id', 'patient_id', 'doctor_id', 'date', 'time', 
                'status', 'notes', 'created_at', 'cancellation_remarks'
            ]
            
            for column in columns:
                try:
                    result = db.session.execute(text(f"SELECT {column} FROM appointments LIMIT 1"))
                    print(f"✅ Column '{column}' exists in appointments table")
                except Exception as e:
                    print(f"❌ Column '{column}' missing: {e}")
            
            return True
    except Exception as e:
        print(f"❌ Appointment table check error: {e}")
        return False

def test_payment_creation():
    """Test payment record creation"""
    print("\n🔍 Testing payment record creation...")
    
    try:
        from app import app, db
        from models.payment import Payment
        from models.appointment import Appointment
        from models.user import User
        
        with app.app_context():
            # Check if we have any appointments and users
            appointment_count = Appointment.query.count()
            user_count = User.query.count()
            
            print(f"✅ Found {appointment_count} appointments and {user_count} users")
            
            if appointment_count > 0 and user_count > 0:
                # Try to create a test payment record
                test_appointment = Appointment.query.first()
                
                payment = Payment(
                    appointment_id=test_appointment.id,
                    transaction_uuid="test-123",
                    amount=100.0,
                    tax_amount=13.0,
                    total_amount=113.0,
                    status="pending"
                )
                
                db.session.add(payment)
                db.session.commit()
                print("✅ Test payment record created successfully")
                
                # Clean up test record
                db.session.delete(payment)
                db.session.commit()
                print("✅ Test payment record cleaned up")
            else:
                print("⚠️  No appointments or users found for testing")
            
            return True
    except Exception as e:
        print(f"❌ Payment creation test error: {e}")
        return False

def main():
    """Run all database checks"""
    print("🚀 Starting Database Checks for HealthPoint Application")
    print("=" * 60)
    
    checks = [
        check_database_connection,
        check_payment_table,
        check_appointment_table,
        test_payment_creation
    ]
    
    passed = 0
    failed = 0
    
    for check in checks:
        try:
            if check():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Check {check.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Check Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All database checks passed!")
        return True
    else:
        print("⚠️  Some database checks failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 