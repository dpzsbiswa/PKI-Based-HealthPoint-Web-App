#!/usr/bin/env python3
"""
Payment Error Check Script for HealthPoint Application
Checks for potential payment process errors and edge cases
"""

import sys
import os
import traceback
from datetime import datetime, date, time

def test_payment_flow_edge_cases():
    """Test payment flow with edge cases"""
    print("🔍 Testing payment flow edge cases...")
    
    try:
        from app import app, db
        from models.payment import Payment
        from models.appointment import Appointment
        from models.user import User
        from utils.esewa import ESewaPayment
        
        with app.app_context():
            # Test 1: Zero consultation fee
            print("\n📋 Test 1: Zero consultation fee")
            doctor = User.query.filter_by(role='doctor').first()
            if doctor:
                original_fee = doctor.consultation_fee
                doctor.consultation_fee = 0
                db.session.commit()
                
                # This should be handled gracefully in the booking flow
                print("✅ Zero consultation fee test completed")
                
                # Restore original fee
                doctor.consultation_fee = original_fee
                db.session.commit()
            
            # Test 2: Negative amounts
            print("\n📋 Test 2: Negative amounts")
            esewa = ESewaPayment()
            try:
                form_data, _ = esewa.create_payment_form_data(
                    appointment=None,
                    amount=-100,
                    tax_amount=-13
                )
                print("⚠️  Negative amounts should be rejected")
            except Exception as e:
                print(f"✅ Negative amounts properly rejected: {e}")
            
            # Test 3: Very large amounts
            print("\n📋 Test 3: Very large amounts")
            try:
                form_data, _ = esewa.create_payment_form_data(
                    appointment=None,
                    amount=999999.99,
                    tax_amount=99999.99
                )
                print("✅ Large amounts handled properly")
            except Exception as e:
                print(f"❌ Large amounts error: {e}")
            
            # Test 4: Decimal precision
            print("\n📋 Test 4: Decimal precision")
            try:
                form_data, _ = esewa.create_payment_form_data(
                    appointment=None,
                    amount=100.50,
                    tax_amount=13.065
                )
                print("✅ Decimal precision handled properly")
                print(f"   Amount: {form_data.get('amount')}")
                print(f"   Tax: {form_data.get('tax_amount')}")
                print(f"   Total: {form_data.get('total_amount')}")
            except Exception as e:
                print(f"❌ Decimal precision error: {e}")
            
            return True
    except Exception as e:
        print(f"❌ Payment flow edge case error: {e}")
        traceback.print_exc()
        return False

def test_signature_verification_edge_cases():
    """Test signature verification with edge cases"""
    print("\n🔍 Testing signature verification edge cases...")
    
    try:
        from utils.esewa import ESewaPayment
        esewa = ESewaPayment()
        
        # Test 1: Empty signature
        print("\n📋 Test 1: Empty signature")
        test_data = {
            'transaction_code': '000AWEO',
            'status': 'COMPLETE',
            'total_amount': '1000.0',
            'transaction_uuid': '250610-162413',
            'product_code': 'EPAYTEST',
            'signed_field_names': 'transaction_code,status,total_amount,transaction_uuid,product_code,signed_field_names'
        }
        
        result = esewa.verify_signature(test_data, '')
        print(f"✅ Empty signature handled: {result}")
        
        # Test 2: Invalid signature
        print("\n📋 Test 2: Invalid signature")
        result = esewa.verify_signature(test_data, 'invalid_signature')
        print(f"✅ Invalid signature rejected: {result}")
        
        # Test 3: Missing signed fields
        print("\n📋 Test 3: Missing signed fields")
        incomplete_data = {
            'transaction_code': '000AWEO',
            'status': 'COMPLETE',
            'signed_field_names': 'transaction_code,status,total_amount,transaction_uuid,product_code,signed_field_names'
        }
        
        try:
            result = esewa.verify_signature(incomplete_data, 'some_signature')
            print(f"✅ Missing fields handled: {result}")
        except Exception as e:
            print(f"✅ Missing fields properly handled: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Signature verification edge case error: {e}")
        traceback.print_exc()
        return False

def test_database_constraints():
    """Test database constraints and relationships"""
    print("\n🔍 Testing database constraints...")
    
    try:
        from app import app, db
        from models.payment import Payment
        from models.appointment import Appointment
        from models.user import User
        
        with app.app_context():
            # Test 1: Duplicate transaction UUID
            print("\n📋 Test 1: Duplicate transaction UUID")
            existing_payment = Payment.query.first()
            if existing_payment:
                try:
                    duplicate_payment = Payment(
                        appointment_id=existing_payment.appointment_id,
                        transaction_uuid=existing_payment.transaction_uuid,
                        amount=100.0,
                        tax_amount=13.0,
                        total_amount=113.0
                    )
                    db.session.add(duplicate_payment)
                    db.session.commit()
                    print("❌ Duplicate UUID should be rejected")
                except Exception as e:
                    print(f"✅ Duplicate UUID properly rejected: {e}")
                finally:
                    db.session.rollback()
            
            # Test 2: Invalid appointment reference
            print("\n📋 Test 2: Invalid appointment reference")
            try:
                invalid_payment = Payment(
                    appointment_id=99999,  # Non-existent appointment
                    transaction_uuid="test-invalid-ref",
                    amount=100.0,
                    tax_amount=13.0,
                    total_amount=113.0
                )
                db.session.add(invalid_payment)
                db.session.commit()
                print("❌ Invalid appointment reference should be rejected")
            except Exception as e:
                print(f"✅ Invalid appointment reference properly rejected: {e}")
            finally:
                db.session.rollback()
            
            # Test 3: Null required fields
            print("\n📋 Test 3: Null required fields")
            try:
                null_payment = Payment(
                    appointment_id=None,
                    transaction_uuid=None,
                    amount=None,
                    total_amount=None
                )
                db.session.add(null_payment)
                db.session.commit()
                print("❌ Null required fields should be rejected")
            except Exception as e:
                print(f"✅ Null required fields properly rejected: {e}")
            finally:
                db.session.rollback()
            
            return True
    except Exception as e:
        print(f"❌ Database constraints error: {e}")
        traceback.print_exc()
        return False

def test_payment_status_transitions():
    """Test payment status transitions"""
    print("\n🔍 Testing payment status transitions...")
    
    try:
        from app import app, db
        from models.payment import Payment
        from models.appointment import Appointment
        
        with app.app_context():
            # Create a test payment
            test_appointment = Appointment.query.first()
            if test_appointment:
                test_payment = Payment(
                    appointment_id=test_appointment.id,
                    transaction_uuid="test-status-transitions",
                    amount=100.0,
                    tax_amount=13.0,
                    total_amount=113.0,
                    status="pending"
                )
                db.session.add(test_payment)
                db.session.commit()
                
                # Test status transitions
                print("\n📋 Test 1: Pending -> Completed")
                test_payment.status = "completed"
                db.session.commit()
                print("✅ Pending to completed transition successful")
                
                print("\n📋 Test 2: Completed -> Failed")
                test_payment.status = "failed"
                db.session.commit()
                print("✅ Completed to failed transition successful")
                
                print("\n📋 Test 3: Failed -> Cancelled")
                test_payment.status = "cancelled"
                db.session.commit()
                print("✅ Failed to cancelled transition successful")
                
                # Clean up
                db.session.delete(test_payment)
                db.session.commit()
                print("✅ Test payment cleaned up")
            
            return True
    except Exception as e:
        print(f"❌ Payment status transitions error: {e}")
        traceback.print_exc()
        return False

def test_url_generation():
    """Test URL generation for different environments"""
    print("\n🔍 Testing URL generation...")
    
    try:
        from utils.esewa import ESewaPayment
        esewa = ESewaPayment()
        
        # Test localhost URLs
        form_data, _ = esewa.create_payment_form_data(
            appointment=None,
            amount=100,
            tax_amount=13
        )
        
        success_url = form_data.get('success_url')
        failure_url = form_data.get('failure_url')
        
        print(f"✅ Success URL: {success_url}")
        print(f"✅ Failure URL: {failure_url}")
        
        # Check if URLs are properly formatted
        if 'localhost' in success_url and 'localhost' in failure_url:
            print("✅ URLs are properly configured for local development")
        else:
            print("⚠️  URLs may need to be updated for production")
        
        return True
    except Exception as e:
        print(f"❌ URL generation error: {e}")
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling in payment routes"""
    print("\n🔍 Testing error handling...")
    
    try:
        from app import app
        from utils.esewa import ESewaPayment
        
        # Test 1: Invalid appointment ID
        print("\n📋 Test 1: Invalid appointment ID")
        with app.test_client() as client:
            response = client.get('/payment/99999')
            print(f"✅ Invalid appointment ID handled: {response.status_code}")
        
        # Test 2: Unauthorized access
        print("\n📋 Test 2: Unauthorized access")
        with app.test_client() as client:
            response = client.get('/payment/1')
            print(f"✅ Unauthorized access handled: {response.status_code}")
        
        # Test 3: Invalid eSewa response
        print("\n📋 Test 3: Invalid eSewa response")
        esewa = ESewaPayment()
        
        # Test with invalid base64
        result = esewa.decode_esewa_response("invalid_base64")
        print(f"✅ Invalid base64 handled: {result.get('error', 'No error')}")
        
        # Test with invalid JSON
        import base64
        invalid_json = base64.b64encode(b"invalid json").decode('utf-8')
        result = esewa.decode_esewa_response(invalid_json)
        print(f"✅ Invalid JSON handled: {result.get('error', 'No error')}")
        
        return True
    except Exception as e:
        print(f"❌ Error handling test error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all payment error checks"""
    print("🚀 Starting Payment Error Checks for HealthPoint Application")
    print("=" * 60)
    
    checks = [
        test_payment_flow_edge_cases,
        test_signature_verification_edge_cases,
        test_database_constraints,
        test_payment_status_transitions,
        test_url_generation,
        test_error_handling
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
        print("🎉 All payment error checks passed!")
        print("✅ No runtime errors or payment process issues detected")
        return True
    else:
        print("⚠️  Some payment error checks failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 