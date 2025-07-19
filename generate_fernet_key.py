"""Enhanced Fernet key generator for AutoPilot Ventures platform."""

import os
import base64
import argparse
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def generate_fernet_key() -> str:
    """Generate a new Fernet key."""
    return Fernet.generate_key().decode()


def validate_fernet_key(key: str) -> bool:
    """Validate if a Fernet key is properly formatted."""
    try:
        # Check if it's base64 encoded and 44 characters long
        if len(key) != 44:
            return False
        
        # Try to decode and create Fernet instance
        key_bytes = base64.urlsafe_b64decode(key)
        if len(key_bytes) != 32:
            return False
        
        Fernet(key.encode())
        return True
    except Exception:
        return False


def derive_key_from_password(password: str, salt: bytes = None) -> str:
    """Derive a Fernet key from a password using PBKDF2."""
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key.decode()


def format_key_for_env(key: str) -> str:
    """Format key for environment variable."""
    return f"FERNET_KEY={key}"


def save_key_to_env_file(key: str, env_file: str = ".env") -> None:
    """Save key to .env file."""
    env_content = ""
    
    # Read existing .env file if it exists
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            env_content = f.read()
    
    # Check if FERNET_KEY already exists
    if "FERNET_KEY=" in env_content:
        # Replace existing key
        lines = env_content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith("FERNET_KEY="):
                lines[i] = format_key_for_env(key)
                break
        env_content = '\n'.join(lines)
    else:
        # Add new key
        if env_content and not env_content.endswith('\n'):
            env_content += '\n'
        env_content += format_key_for_env(key) + '\n'
    
    # Write back to file
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Fernet key saved to {env_file}")


def test_key_functionality(key: str) -> bool:
    """Test if the key works for encryption/decryption."""
    try:
        fernet = Fernet(key.encode())
        test_data = "AutoPilot Ventures test data"
        encrypted = fernet.encrypt(test_data.encode())
        decrypted = fernet.decrypt(encrypted).decode()
        return decrypted == test_data
    except Exception as e:
        print(f"❌ Key test failed: {e}")
        return False


def main():
    """Main function for key generation."""
    parser = argparse.ArgumentParser(
        description="Generate and validate Fernet keys for AutoPilot Ventures"
    )
    parser.add_argument(
        '--validate', 
        type=str,
        help='Validate an existing Fernet key'
    )
    parser.add_argument(
        '--password',
        type=str,
        help='Derive key from password'
    )
    parser.add_argument(
        '--save-env',
        action='store_true',
        help='Save key to .env file'
    )
    parser.add_argument(
        '--env-file',
        type=str,
        default='.env',
        help='Environment file path (default: .env)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test key functionality'
    )
    
    args = parser.parse_args()
    
    if args.validate:
        print("🔍 Validating Fernet key...")
        if validate_fernet_key(args.validate):
            print("✅ Key is valid!")
            if args.test:
                if test_key_functionality(args.validate):
                    print("✅ Key functionality test passed!")
                else:
                    print("❌ Key functionality test failed!")
        else:
            print("❌ Key is invalid!")
            print("   Expected: 44-character base64-encoded string")
            print("   Example:  NUtkaTVVZnJsZS1DcDJqSGdBd01vVFlmeU0yaHpJM2ZJdDA2MlpJUTFDVT0=")
        return
    
    if args.password:
        print("🔑 Deriving key from password...")
        key = derive_key_from_password(args.password)
        print(f"✅ Derived key: {key}")
    else:
        print("🔑 Generating new Fernet key...")
        key = generate_fernet_key()
        print(f"✅ Generated key: {key}")
    
    # Validate the key
    if validate_fernet_key(key):
        print("✅ Key validation passed!")
    else:
        print("❌ Key validation failed!")
        return
    
    # Test functionality
    if args.test or not args.password:
        print("🧪 Testing key functionality...")
        if test_key_functionality(key):
            print("✅ Key functionality test passed!")
        else:
            print("❌ Key functionality test failed!")
            return
    
    # Save to .env file
    if args.save_env:
        save_key_to_env_file(key, args.env_file)
    
    # Display usage instructions
    print("\n📋 Usage Instructions:")
    print("1. Set environment variable:")
    print(f"   export FERNET_KEY='{key}'")
    print("2. Or add to .env file:")
    print(f"   FERNET_KEY={key}")
    print("3. Or use in Python:")
    print(f"   os.environ['FERNET_KEY'] = '{key}'")
    
    print("\n🔒 Security Notes:")
    print("- Keep this key secure and confidential")
    print("- Use different keys for different environments")
    print("- Rotate keys periodically for enhanced security")
    print("- Never commit keys to version control")


if __name__ == "__main__":
    main() 