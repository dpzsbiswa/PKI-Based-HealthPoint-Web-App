#!/usr/bin/env python3
"""
Verify against exact eSewa developer guide example
"""

import hmac
import hashlib
import base64

def verify_exact_esewa_example():
    """Verify our implementation against the exact eSewa developer guide example"""
    
    print("🔍 Verifying Against Exact eSewa Developer Guide Example")
    print("=" * 60)
    
    # Exact values from the developer guide
    secret_key = "8gBm/:&EnhH.1/q"  # Our corrected secret key
    total_amount = "110"
    transaction_uuid = "241028"
    product_code = "EPAYTEST"
    expected_signature = "i94zsd3oXF6ZsSr/kGqT4sSzYQzjj1W/waxjWyRwaME="
    
    print("📋 Developer Guide Values:")
    print(f"  Secret Key: {secret_key}")
    print(f"  Total Amount: {total_amount}")
    print(f"  Transaction UUID: {transaction_uuid}")
    print(f"  Product Code: {product_code}")
    print(f"  Expected Signature: {expected_signature}")
    
    # Create the message exactly as specified
    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    print(f"\n📝 Generated Message: {message}")
    
    # Generate signature using the exact method from developer guide
    hmac_sha256 = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256)
    digest = hmac_sha256.digest()
    signature = base64.b64encode(digest).decode('utf-8')
    
    print(f"\n🔐 Signature Generation:")
    print(f"  Generated Signature: {signature}")
    print(f"  Expected Signature: {expected_signature}")
    print(f"  ✅ Match: {signature == expected_signature}")
    
    # Test with our ESewaPayment class
    print(f"\n🧪 Testing with our ESewaPayment class:")
    
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from utils.esewa import ESewaPayment
    
    esewa = ESewaPayment()
    our_signature = esewa.generate_signature(total_amount, transaction_uuid, product_code)
    
    print(f"  Our Class Signature: {our_signature}")
    print(f"  Expected Signature: {expected_signature}")
    print(f"  ✅ Match: {our_signature == expected_signature}")
    
    # Test the complete form data generation
    print(f"\n📋 Testing Complete Form Data Generation:")
    
    class MockAppointment:
        def __init__(self):
            self.id = 1
            self.doctor = MockDoctor()
    
    class MockDoctor:
        def __init__(self):
            self.name = "Dr. Test"
    
    mock_appointment = MockAppointment()
    
    # Use the exact values from developer guide
    form_data, transaction_uuid = esewa.create_payment_form_data(
        appointment=mock_appointment,
        amount=100,  # amount from developer guide
        tax_amount=10  # tax_amount from developer guide
    )
    
    print("Generated Form Data:")
    for key, value in form_data.items():
        print(f"  {key}: {value}")
    
    # Verify the signature matches
    form_signature = form_data['signature']
    form_total = form_data['total_amount']
    form_uuid = form_data['transaction_uuid']
    form_product = form_data['product_code']
    
    # Regenerate signature to verify
    verify_signature = esewa.generate_signature(form_total, form_uuid, form_product)
    print(f"\n🔍 Signature Verification:")
    print(f"  Form Signature: {form_signature}")
    print(f"  Verify Signature: {verify_signature}")
    print(f"  ✅ Verification: {form_signature == verify_signature}")
    
    # Test with different secret key variations
    print(f"\n🔑 Testing Secret Key Variations:")
    secret_variations = [
        "8gBm/:&EnhH.1/q",
        "8gBm/:&EnhH.1/q(",
        "8gBm/:&EnhH.1/q()",
    ]
    
    for key in secret_variations:
        hmac_obj = hmac.new(key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256)
        sig = base64.b64encode(hmac_obj.digest()).decode('utf-8')
        print(f"  Secret: '{key}' -> Signature: {sig}")
        print(f"  Match: {sig == expected_signature}")
    
    print(f"\n" + "=" * 60)
    print("🎉 Verification Complete!")
    
    if signature == expected_signature:
        print("✅ SUCCESS: Our implementation matches the eSewa developer guide exactly!")
        print("✅ The signature generation is working correctly.")
        print("✅ Ready for production use.")
    else:
        print("❌ ISSUE: Signature doesn't match the developer guide.")
        print("❌ Need to investigate further.")

if __name__ == "__main__":
    verify_exact_esewa_example() 