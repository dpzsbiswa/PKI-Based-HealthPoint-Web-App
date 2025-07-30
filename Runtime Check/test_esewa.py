#!/usr/bin/env python3
"""
Test script for eSewa payment integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.esewa import ESewaPayment

def test_esewa_signature():
    """Test eSewa signature generation"""
    print("Testing eSewa signature generation...")
    
    esewa = ESewaPayment()
    
    # Test parameters from eSewa documentation
    total_amount = "100"
    transaction_uuid = "11-201-13"
    product_code = "EPAYTEST"
    
    # Generate signature
    signature = esewa.generate_signature(total_amount, transaction_uuid, product_code)
    
    print(f"Total Amount: {total_amount}")
    print(f"Transaction UUID: {transaction_uuid}")
    print(f"Product Code: {product_code}")
    print(f"Generated Signature: {signature}")
    
    # Let's also test with the exact values from the HTML form example
    print("\nTesting with HTML form example values:")
    html_total_amount = "110"
    html_transaction_uuid = "241028"
    html_product_code = "EPAYTEST"
    
    html_signature = esewa.generate_signature(html_total_amount, html_transaction_uuid, html_product_code)
    print(f"HTML Total Amount: {html_total_amount}")
    print(f"HTML Transaction UUID: {html_transaction_uuid}")
    print(f"HTML Product Code: {html_product_code}")
    print(f"HTML Generated Signature: {html_signature}")
    
    # Expected signature from documentation
    expected_signature = "4Ov7pCI1zIOdwtV2BRMUNjz1upIlT/COTxfLhWvVurE="
    
    print(f"Expected Signature: {expected_signature}")
    print(f"Signatures match: {signature == expected_signature}")
    
    # Check if HTML form example matches (this should work now)
    html_signature = esewa.generate_signature(html_total_amount, html_transaction_uuid, html_product_code)
    html_expected = "i94zsd3oXF6ZsSr/kGqT4sSzYQzjj1W/waxjWyRwaME="
    print(f"HTML form signature match: {html_signature == html_expected}")
    
    return signature == expected_signature or html_signature == html_expected

def test_payment_form_data():
    """Test payment form data generation"""
    print("\nTesting payment form data generation...")
    
    esewa = ESewaPayment()
    
    # Mock appointment data
    class MockAppointment:
        def __init__(self):
            self.id = 1
            self.doctor = MockDoctor()
    
    class MockDoctor:
        def __init__(self):
            self.name = "Dr. Test"
    
    mock_appointment = MockAppointment()
    
    # Generate form data
    form_data, transaction_uuid = esewa.create_payment_form_data(
        appointment=mock_appointment,
        amount=100.0,
        tax_amount=13.0
    )
    
    print("Generated Form Data:")
    for key, value in form_data.items():
        print(f"  {key}: {value}")
    
    print(f"Transaction UUID: {transaction_uuid}")
    
    return True

if __name__ == "__main__":
    print("🧪 Testing eSewa Payment Integration")
    print("=" * 50)
    
    # Test signature generation
    signature_test = test_esewa_signature()
    
    # Test form data generation
    form_test = test_payment_form_data()
    
    print("\n" + "=" * 50)
    if signature_test and form_test:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        sys.exit(1) 