#!/usr/bin/env python3
"""
Test script to verify eSewa format requirements
"""

import hmac
import hashlib
import base64

def test_esewa_format():
    """Test different format variations that eSewa might expect"""
    
    print("🧪 Testing eSewa Format Requirements")
    print("=" * 50)
    
    secret_key = "8gBm/:&EnhH.1/q("
    
    # Test different number formats
    test_cases = [
        # (amount, tax, total, uuid, product)
        ("100", "10", "110", "241028", "EPAYTEST"),
        ("100.0", "10.0", "110.0", "241028", "EPAYTEST"),
        ("100", "10", "110", "241028", "EPAYTEST"),
        ("500", "65", "565", "demo-123", "EPAYTEST"),
        ("500.0", "65.0", "565.0", "demo-123", "EPAYTEST"),
    ]
    
    for i, (amount, tax, total, uuid, product) in enumerate(test_cases, 1):
        print(f"\n{i}. Testing format: amount={amount}, tax={tax}, total={total}")
        
        # Test different message formats
        formats = [
            f"total_amount={total},transaction_uuid={uuid},product_code={product}",
            f"total_amount={total},transaction_uuid={uuid},product_code={product}",
        ]
        
        for j, message in enumerate(formats, 1):
            print(f"   Format {j}: {message}")
            
            hmac_obj = hmac.new(
                secret_key.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            )
            signature = base64.b64encode(hmac_obj.digest()).decode('utf-8')
            print(f"   Signature: {signature}")
    
    # Test with exact values from eSewa documentation
    print(f"\n📋 Testing with eSewa documentation values:")
    
    # From the HTML form example
    doc_total = "110"
    doc_uuid = "241028"
    doc_product = "EPAYTEST"
    doc_signature = "i94zsd3oXF6ZsSr/kGqT4sSzYQzjj1W/waxjWyRwaME="
    
    doc_message = f"total_amount={doc_total},transaction_uuid={doc_uuid},product_code={doc_product}"
    print(f"Documentation message: {doc_message}")
    
    doc_hmac = hmac.new(
        secret_key.encode('utf-8'),
        doc_message.encode('utf-8'),
        hashlib.sha256
    )
    doc_generated = base64.b64encode(doc_hmac.digest()).decode('utf-8')
    print(f"Generated signature: {doc_generated}")
    print(f"Expected signature: {doc_signature}")
    print(f"Match: {doc_generated == doc_signature}")
    
    # Test with different secret key formats
    print(f"\n🔑 Testing secret key variations:")
    secret_keys = [
        "8gBm/:&EnhH.1/q(",
        "8gBm/:&EnhH.1/q()",
        "8gBm/:&EnhH.1/q",
        "8gBm/:&EnhH.1/q(",
    ]
    
    for key in secret_keys:
        print(f"Secret key: '{key}'")
        message = f"total_amount=110,transaction_uuid=241028,product_code=EPAYTEST"
        
        hmac_obj = hmac.new(
            key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        )
        signature = base64.b64encode(hmac_obj.digest()).decode('utf-8')
        print(f"Signature: {signature}")
        print(f"Expected: {doc_signature}")
        print(f"Match: {signature == doc_signature}")
        print()

def test_actual_application_values():
    """Test with values that the application actually generates"""
    print(f"\n💻 Testing with application-generated values:")
    
    secret_key = "8gBm/:&EnhH.1/q("
    
    # Simulate what the application generates
    app_amount = 500.0
    app_tax = 65.0
    app_total = 565.0
    app_uuid = "250726-003438-cd53963e"
    app_product = "EPAYTEST"
    
    # Test different string conversions
    conversions = [
        (str(app_total), "str()"),
        (f"{app_total}", "f-string"),
        (f"{app_total:.1f}", "f-string with format"),
        (f"{int(app_total)}", "f-string with int"),
    ]
    
    for total_str, method in conversions:
        message = f"total_amount={total_str},transaction_uuid={app_uuid},product_code={app_product}"
        print(f"Method: {method}")
        print(f"Message: {message}")
        
        hmac_obj = hmac.new(
            secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        )
        signature = base64.b64encode(hmac_obj.digest()).decode('utf-8')
        print(f"Signature: {signature}")
        print()

if __name__ == "__main__":
    test_esewa_format()
    test_actual_application_values()
    
    print("=" * 50)
    print("🔧 Recommendations:")
    print("1. Try using integer values instead of floats")
    print("2. Ensure no trailing zeros in decimal values")
    print("3. Verify the secret key format")
    print("4. Check if eSewa expects specific number formatting")
    print("5. Contact eSewa support for exact format requirements") 