#!/usr/bin/env python3
"""
Demo script for eSewa payment integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.esewa import ESewaPayment

def demo_esewa_integration():
    """Demo the eSewa integration features"""
    
    print("🏥 HealthPoint eSewa Payment Integration Demo")
    print("=" * 60)
    
    # Initialize eSewa payment
    esewa = ESewaPayment()
    
    # Demo 1: Signature Generation
    print("\n1. 🔐 Signature Generation")
    print("-" * 30)
    
    total_amount = "1000"
    transaction_uuid = "demo-123-456"
    product_code = "EPAYTEST"
    
    signature = esewa.generate_signature(total_amount, transaction_uuid, product_code)
    print(f"Parameters:")
    print(f"  - Total Amount: {total_amount}")
    print(f"  - Transaction UUID: {transaction_uuid}")
    print(f"  - Product Code: {product_code}")
    print(f"Generated Signature: {signature}")
    
    # Demo 2: Payment Form Generation
    print("\n2. 💳 Payment Form Generation")
    print("-" * 30)
    
    class MockAppointment:
        def __init__(self):
            self.id = 1
            self.doctor = MockDoctor()
    
    class MockDoctor:
        def __init__(self):
            self.name = "Dr. John Smith"
    
    mock_appointment = MockAppointment()
    
    form_data, transaction_uuid = esewa.create_payment_form_data(
        appointment=mock_appointment,
        amount=500.0,
        tax_amount=65.0  # 13% VAT
    )
    
    print("Generated Payment Form Data:")
    for key, value in form_data.items():
        print(f"  {key}: {value}")
    
    # Demo 3: Transaction Status Check
    print("\n3. 📊 Transaction Status Check")
    print("-" * 30)
    
    print("Status check URL format:")
    status_url = f"{esewa.status_check_test_url}?product_code=EPAYTEST&total_amount=100&transaction_uuid=123"
    print(f"  {status_url}")
    
    # Demo 4: Response Decoding
    print("\n4. 🔍 Response Decoding")
    print("-" * 30)
    
    # Example encoded response from eSewa
    sample_encoded_response = "eyJ0cmFuc2FjdGlvbl9jb2RlIjoiMDAwQVdFTyIsInN0YXR1cyI6IkNPTVBMRVRFIiwidG90YWxfYW1vdW50IjoiMTAwMC4wIiwidHJhbnNhY3Rpb25fdXVpZCI6IjI1MDYxMC0xNjI0MTMiLCJwcm9kdWN0X2NvZGUiOiJFUEFZVEVTVCIsInNpZ25lZF9maWVsZF9uYW1lcyI6InRyYW5zYWN0aW9uX2NvZGUsc3RhdHVzLHRvdGFsX2Ftb3VudCx0cmFuc2FjdGlvbl91dWlkLHByb2R1Y3RfY29kZSxzaWduZWRfZmllbGRfbmFtZXMiLCJzaWduYXR1cmUiOiI2MkdjZlpUbVZremh0VWVoK1FKMUFxaUpyam9XV0dvZjNVK2VUUFRaN2ZBPSJ9"
    
    decoded_response = esewa.decode_esewa_response(sample_encoded_response)
    print("Decoded eSewa Response:")
    for key, value in decoded_response.items():
        print(f"  {key}: {value}")
    
    # Demo 5: Integration Features
    print("\n5. 🚀 Integration Features")
    print("-" * 30)
    
    features = [
        "✅ HMAC SHA-256 signature generation",
        "✅ Base64 signature encoding",
        "✅ Payment form data generation",
        "✅ Transaction UUID generation",
        "✅ Response signature verification",
        "✅ Base64 response decoding",
        "✅ Payment status checking",
        "✅ Tax calculation (13% VAT)",
        "✅ Success/failure handling",
        "✅ Database integration"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    # Demo 6: Usage Instructions
    print("\n6. 📖 Usage Instructions")
    print("-" * 30)
    
    instructions = [
        "1. Patient books appointment with doctor",
        "2. Patient clicks 'Pay Now' button",
        "3. System generates eSewa payment form",
        "4. Patient completes payment on eSewa",
        "5. eSewa redirects to success/failure URL",
        "6. System verifies payment and updates status",
        "7. Appointment is confirmed after payment"
    ]
    
    for instruction in instructions:
        print(f"  {instruction}")
    
    # Demo 7: Test Credentials
    print("\n7. 🧪 Test Credentials")
    print("-" * 30)
    
    credentials = [
        "eSewa ID: 9806800001/2/3/4/5",
        "Password: Nepal@123",
        "MPIN: 1122",
        "Token: 123456"
    ]
    
    for credential in credentials:
        print(f"  {credential}")
    
    print("\n" + "=" * 60)
    print("🎉 eSewa Integration Demo Complete!")
    print("\nTo test the integration:")
    print("1. Start the Flask application: python app.py")
    print("2. Register as a patient and doctor")
    print("3. Book an appointment with consultation fee")
    print("4. Use the 'Pay Now' button to test payment")
    print("5. Use the test credentials above for eSewa login")

if __name__ == "__main__":
    demo_esewa_integration() 