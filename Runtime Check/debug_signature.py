#!/usr/bin/env python3
"""
Debug script for eSewa signature generation
"""

import hmac
import hashlib
import base64

def debug_signature():
    """Debug the signature generation process"""
    
    # Parameters from eSewa documentation
    total_amount = "100"
    transaction_uuid = "11-201-13"
    product_code = "EPAYTEST"
    secret_key = "8gBm/:&EnhH.1/q("
    
    # Create the message string
    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    
    print("Debug Information:")
    print(f"Secret Key: {secret_key}")
    print(f"Message: {message}")
    print(f"Message bytes: {message.encode('utf-8')}")
    
    # Create HMAC SHA-256 signature
    hmac_obj = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    )
    
    # Get the digest
    digest = hmac_obj.digest()
    print(f"Digest (hex): {digest.hex()}")
    
    # Encode to base64
    signature = base64.b64encode(digest).decode('utf-8')
    print(f"Signature: {signature}")
    
    # Expected signature
    expected = "4Ov7pCI1zIOdwtV2BRMUNjz1upIlT/COTxfLhWvVurE="
    print(f"Expected: {expected}")
    print(f"Match: {signature == expected}")
    
    # Let's also test the HTML form example
    print("\nHTML Form Example:")
    html_total = "110"
    html_uuid = "241028"
    html_product = "EPAYTEST"
    
    html_message = f"total_amount={html_total},transaction_uuid={html_uuid},product_code={html_product}"
    print(f"HTML Message: {html_message}")
    
    html_hmac = hmac.new(
        secret_key.encode('utf-8'),
        html_message.encode('utf-8'),
        hashlib.sha256
    )
    
    html_digest = html_hmac.digest()
    html_signature = base64.b64encode(html_digest).decode('utf-8')
    print(f"HTML Signature: {html_signature}")
    
    # Expected from HTML form
    html_expected = "i94zsd3oXF6ZsSr/kGqT4sSzYQzjj1W/waxjWyRwaME="
    print(f"HTML Expected: {html_expected}")
    print(f"HTML Match: {html_signature == html_expected}")

if __name__ == "__main__":
    debug_signature() 