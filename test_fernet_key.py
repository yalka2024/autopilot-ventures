#!/usr/bin/env python3
"""
Test script to verify Fernet key functionality.
"""

import os
import base64
from cryptography.fernet import Fernet
from dotenv import load_dotenv

def test_fernet_key():
    """Test the Fernet key from .env file."""
    print("🔍 Testing Fernet key...")
    
    # Load environment variables
    load_dotenv()
    
    # Get the key from environment
    key = os.getenv('FERNET_KEY', '')
    print(f"Key from env: '{key}'")
    print(f"Key length: {len(key)}")
    print(f"Key bytes: {key.encode()}")
    
    try:
        # Test if it's valid base64
        decoded = base64.urlsafe_b64decode(key)
        print(f"Decoded length: {len(decoded)}")
        
        # Test if it works with Fernet
        fernet = Fernet(key.encode())
        test_data = b"Hello, World!"
        encrypted = fernet.encrypt(test_data)
        decrypted = fernet.decrypt(encrypted)
        
        print(f"✅ Fernet key works! Test data: {test_data}")
        print(f"✅ Encrypted: {encrypted}")
        print(f"✅ Decrypted: {decrypted}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fernet key test failed: {e}")
        return False

if __name__ == "__main__":
    test_fernet_key() 