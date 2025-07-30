#!/usr/bin/env python3
"""
Runtime Error Test Script for HealthPoint Application
Tests all major components for potential runtime errors
"""

import sys
import os
import traceback

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing imports...")
    
    try:
        from flask import Flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import error: {e}")
        return False
    
    try:
        from werkzeug.security import generate_password_hash, check_password_hash
        print("✅ Werkzeug security imported successfully")
    except ImportError as e:
        print(f"❌ Werkzeug security import error: {e}")
        return False
    
    try:
        from sqlalchemy import create_engine
        print("✅ SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"❌ SQLAlchemy import error: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError as e:
        print(f"❌ Requests import error: {e}")
        return False
    
    try:
        import hmac
        import hashlib
        import base64
        print("✅ Crypto modules imported successfully")
    except ImportError as e:
        print(f"❌ Crypto modules import error: {e}")
        return False
    
    return True

def test_app_creation():
    """Test Flask app creation"""
    print("\n🔍 Testing Flask app creation...")
    
    try:
        from app import app
        print("✅ Flask app created successfully")
        return True
    except Exception as e:
        print(f"❌ Flask app creation error: {e}")
        traceback.print_exc()
        return False

def test_esewa_utility():
    """Test eSewa payment utility"""
    print("\n🔍 Testing eSewa payment utility...")
    
    try:
        from utils.esewa import ESewaPayment
        esewa = ESewaPayment()
        print("✅ ESewaPayment class created successfully")
        
        # Test signature generation
        signature = esewa.generate_signature("110", "test-123", "EPAYTEST")
        print("✅ Signature generation works")
        
        # Test transaction UUID generation
        uuid = esewa.generate_transaction_uuid()
        print(f"✅ Transaction UUID generated: {uuid}")
        
        return True
    except Exception as e:
        print(f"❌ eSewa utility error: {e}")
        traceback.print_exc()
        return False

def test_database_models():
    """Test database models"""
    print("\n🔍 Testing database models...")
    
    try:
        from models.payment import Payment
        print("✅ Payment model imported successfully")
        
        from models.appointment import Appointment
        print("✅ Appointment model imported successfully")
        
        from models.user import User
        print("✅ User model imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Database models error: {e}")
        traceback.print_exc()
        return False

def test_payment_flow():
    """Test payment flow logic"""
    print("\n🔍 Testing payment flow logic...")
    
    try:
        from utils.esewa import ESewaPayment
        
        # Create a mock appointment object
        class MockAppointment:
            def __init__(self):
                self.id = 1
                self.doctor = MockDoctor()
        
        class MockDoctor:
            def __init__(self):
                self.consultation_fee = 100
        
        mock_appointment = MockAppointment()
        
        # Test payment form data creation
        esewa = ESewaPayment()
        form_data, transaction_uuid = esewa.create_payment_form_data(
            appointment=mock_appointment,
            amount=100,
            tax_amount=13
        )
        
        print("✅ Payment form data created successfully")
        print(f"   Transaction UUID: {transaction_uuid}")
        print(f"   Total Amount: {form_data.get('total_amount')}")
        print(f"   Signature: {form_data.get('signature')[:20]}...")
        
        return True
    except Exception as e:
        print(f"❌ Payment flow error: {e}")
        traceback.print_exc()
        return False

def test_url_generation():
    """Test URL generation for payment callbacks"""
    print("\n🔍 Testing URL generation...")
    
    try:
        from utils.esewa import ESewaPayment
        esewa = ESewaPayment()
        
        # Test that URLs are properly formatted
        form_data, _ = esewa.create_payment_form_data(
            appointment=None,
            amount=100,
            tax_amount=13
        )
        
        success_url = form_data.get('success_url')
        failure_url = form_data.get('failure_url')
        
        print(f"✅ Success URL: {success_url}")
        print(f"✅ Failure URL: {failure_url}")
        
        if 'localhost' in success_url and 'localhost' in failure_url:
            print("✅ URLs are properly configured for local development")
        else:
            print("⚠️  URLs may need to be updated for production")
        
        return True
    except Exception as e:
        print(f"❌ URL generation error: {e}")
        traceback.print_exc()
        return False

def test_signature_verification():
    """Test signature verification logic"""
    print("\n🔍 Testing signature verification...")
    
    try:
        from utils.esewa import ESewaPayment
        esewa = ESewaPayment()
        
        # Test with known good data
        test_data = {
            'transaction_code': '000AWEO',
            'status': 'COMPLETE',
            'total_amount': '1000.0',
            'transaction_uuid': '250610-162413',
            'product_code': 'EPAYTEST',
            'signed_field_names': 'transaction_code,status,total_amount,transaction_uuid,product_code,signed_field_names',
            'signature': '62GcfZTmVkzhtUeh+QJ1AqiJrjoWWGof3U+eTPTZ7fA='
        }
        
        # This should work with the correct signature
        result = esewa.verify_signature(test_data, test_data['signature'])
        print(f"✅ Signature verification test completed (result: {result})")
        
        return True
    except Exception as e:
        print(f"❌ Signature verification error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Runtime Error Tests for HealthPoint Application")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_app_creation,
        test_esewa_utility,
        test_database_models,
        test_payment_flow,
        test_url_generation,
        test_signature_verification
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! No runtime errors detected.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 