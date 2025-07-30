#!/usr/bin/env python3
"""
Debug script for eSewa signature issue
"""

import hmac
import hashlib
import base64

def debug_signature_issue():
    """Debug the signature generation issue"""
    
    print("🔍 Debugging eSewa Signature Issue")
    print("=" * 50)
    
    # Test with exact values from eSewa documentation
    secret_key = "8gBm/:&EnhH.1/q("
    
    # Test Case 1: From documentation example
    print("\n1. Testing with documentation example:")
    total_amount = "100"
    transaction_uuid = "11-201-13"
    product_code = "EPAYTEST"
    
    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    print(f"Message: {message}")
    
    hmac_obj = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    )
    digest = hmac_obj.digest()
    signature = base64.b64encode(digest).decode('utf-8')
    print(f"Generated Signature: {signature}")
    
    # Test Case 2: From HTML form example
    print("\n2. Testing with HTML form example:")
    html_total = "110"
    html_uuid = "241028"
    html_product = "EPAYTEST"
    
    html_message = f"total_amount={html_total},transaction_uuid={html_uuid},product_code={html_product}"
    print(f"Message: {html_message}")
    
    html_hmac = hmac.new(
        secret_key.encode('utf-8'),
        html_message.encode('utf-8'),
        hashlib.sha256
    )
    html_digest = html_hmac.digest()
    html_signature = base64.b64encode(html_digest).decode('utf-8')
    print(f"Generated Signature: {html_signature}")
    
    # Test Case 3: Check if there are any encoding issues
    print("\n3. Testing encoding variations:")
    
    # Test with different string encodings
    test_cases = [
        ("100", "11-201-13", "EPAYTEST"),
        ("110", "241028", "EPAYTEST"),
        ("1000", "demo-123", "EPAYTEST"),
    ]
    
    for amount, uuid, product in test_cases:
        message = f"total_amount={amount},transaction_uuid={uuid},product_code={product}"
        print(f"\nTest case: {amount}, {uuid}, {product}")
        print(f"Message: {message}")
        
        # Test different encoding approaches
        hmac1 = hmac.new(
            secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        )
        sig1 = base64.b64encode(hmac1.digest()).decode('utf-8')
        print(f"UTF-8 encoding: {sig1}")
        
        # Test with ASCII encoding
        hmac2 = hmac.new(
            secret_key.encode('ascii'),
            message.encode('ascii'),
            hashlib.sha256
        )
        sig2 = base64.b64encode(hmac2.digest()).decode('ascii')
        print(f"ASCII encoding: {sig2}")
    
    # Test Case 4: Check if secret key has special characters
    print("\n4. Testing secret key variations:")
    secret_key_variations = [
        "8gBm/:&EnhH.1/q(",
        "8gBm/:&EnhH.1/q()",
        "8gBm/:&EnhH.1/q",
    ]
    
    for key in secret_key_variations:
        print(f"\nSecret key: '{key}'")
        message = f"total_amount=100,transaction_uuid=11-201-13,product_code=EPAYTEST"
        
        hmac_obj = hmac.new(
            key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        )
        signature = base64.b64encode(hmac_obj.digest()).decode('utf-8')
        print(f"Signature: {signature}")

def test_actual_payload():
    """Test with actual payload that might be causing the issue"""
    print("\n5. Testing with actual application payload:")
    
    secret_key = "8gBm/:&EnhH.1/q("
    
    # Simulate what the application might be sending
    test_amount = "500.0"
    test_uuid = "250726-003438-cd53963e"
    test_product = "EPAYTEST"
    
    message = f"total_amount={test_amount},transaction_uuid={test_uuid},product_code={test_product}"
    print(f"Message: {message}")
    
    hmac_obj = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    )
    signature = base64.b64encode(hmac_obj.digest()).decode('utf-8')
    print(f"Generated Signature: {signature}")
    
    # Test with string conversion
    test_amount_str = str(test_amount)
    message_str = f"total_amount={test_amount_str},transaction_uuid={test_uuid},product_code={test_product}"
    print(f"Message (string): {message_str}")
    
    hmac_str = hmac.new(
        secret_key.encode('utf-8'),
        message_str.encode('utf-8'),
        hashlib.sha256
    )
    signature_str = base64.b64encode(hmac_str.digest()).decode('utf-8')
    print(f"Signature (string): {signature_str}")

if __name__ == "__main__":
    debug_signature_issue()
    test_actual_payload()
    
    print("\n" + "=" * 50)
    print("🔧 Troubleshooting Steps:")
    print("1. Check if the secret key is correct")
    print("2. Verify the message format matches exactly")
    print("3. Ensure all values are strings")
    print("4. Check for any hidden characters in the secret key")
    print("5. Verify the parameter order in signed_field_names") 