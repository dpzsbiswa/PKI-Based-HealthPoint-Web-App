import hmac
import hashlib
import base64
import json
import uuid
from datetime import datetime
from urllib.parse import urlencode
import requests

class ESewaPayment:
    def __init__(self):
        # eSewa configuration
        self.secret_key = "8gBm/:&EnhH.1/q"  # UAT secret key (without trailing parenthesis)
        self.product_code = "EPAYTEST"
        self.test_url = "https://rc-epay.esewa.com.np/api/epay/main/v2/form"
        self.production_url = "https://epay.esewa.com.np/api/epay/main/v2/form"
        self.status_check_test_url = "https://rc.esewa.com.np/api/epay/transaction/status/"
        self.status_check_production_url = "https://epay.esewa.com.np/api/epay/transaction/status/"
        
    def generate_signature(self, total_amount, transaction_uuid, product_code):
        """
        Generate HMAC SHA-256 signature for eSewa payment
        """
        # Create the message string in the required order
        # Note: The order should be exactly as specified in signed_field_names
        message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
        
        # Create HMAC SHA-256 signature
        hmac_obj = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        )
        
        # Get the digest and encode to base64
        digest = hmac_obj.digest()
        signature = base64.b64encode(digest).decode('utf-8')
        
        return signature
    
    def verify_signature(self, data, signature):
        """
        Verify the signature from eSewa response
        """
        # Extract signed fields from the response
        signed_field_names = data.get('signed_field_names', '')
        signed_fields = signed_field_names.split(',')
        
        # Build the message string in the same order as signed_field_names
        message_parts = []
        for field in signed_fields:
            if field in data:
                message_parts.append(f"{field}={data[field]}")
        
        message = ','.join(message_parts)
        
        # Generate signature for verification
        hmac_obj = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        )
        
        digest = hmac_obj.digest()
        expected_signature = base64.b64encode(digest).decode('utf-8')
        
        return signature == expected_signature
    
    def generate_transaction_uuid(self):
        """
        Generate a unique transaction UUID for eSewa
        """
        timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}-{unique_id}"
    
    def create_payment_form_data(self, appointment, amount, tax_amount=0, service_charge=0, delivery_charge=0):
        """
        Create payment form data for eSewa
        """
        # Validate input parameters
        if amount < 0:
            raise ValueError("Amount cannot be negative")
        if tax_amount < 0:
            raise ValueError("Tax amount cannot be negative")
        if service_charge < 0:
            raise ValueError("Service charge cannot be negative")
        if delivery_charge < 0:
            raise ValueError("Delivery charge cannot be negative")
        
        transaction_uuid = self.generate_transaction_uuid()
        total_amount = amount + tax_amount + service_charge + delivery_charge
        
        # Ensure all values are properly formatted as strings
        # eSewa expects integer values when possible (no decimal places)
        amount_str = str(int(amount)) if amount == int(amount) else str(amount)
        tax_amount_str = str(int(tax_amount)) if tax_amount == int(tax_amount) else str(tax_amount)
        total_amount_str = str(int(total_amount)) if total_amount == int(total_amount) else str(total_amount)
        
        # Generate signature with properly formatted values
        signature = self.generate_signature(
            total_amount_str,
            transaction_uuid,
            self.product_code
        )
        
        form_data = {
            'amount': amount_str,
            'tax_amount': tax_amount_str,
            'total_amount': total_amount_str,
            'transaction_uuid': transaction_uuid,
            'product_code': self.product_code,
            'product_service_charge': str(service_charge),
            'product_delivery_charge': str(delivery_charge),
            'success_url': f"http://localhost:5000/payment/success",
            'failure_url': f"http://localhost:5000/payment/failure",
            'signed_field_names': 'total_amount,transaction_uuid,product_code',
            'signature': signature
        }
        
        return form_data, transaction_uuid
    
    def check_transaction_status(self, transaction_uuid, total_amount, product_code=None):
        """
        Check transaction status from eSewa
        """
        if product_code is None:
            product_code = self.product_code
            
        url = f"{self.status_check_test_url}?product_code={product_code}&total_amount={total_amount}&transaction_uuid={transaction_uuid}"
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'HTTP {response.status_code}: {response.text}'}
        except requests.exceptions.RequestException as e:
            return {'error': f'Request failed: {str(e)}'}
    
    def decode_esewa_response(self, encoded_response):
        """
        Decode base64 encoded response from eSewa
        """
        try:
            decoded_bytes = base64.b64decode(encoded_response)
            decoded_string = decoded_bytes.decode('utf-8')
            return json.loads(decoded_string)
        except Exception as e:
            return {'error': f'Failed to decode response: {str(e)}'} 