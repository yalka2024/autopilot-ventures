#!/usr/bin/env python3
"""
Script to fix the Fernet key in the .env file.
"""

import os
import re

def fix_fernet_key():
    """Fix the Fernet key in the .env file."""
    print("🔧 Fixing Fernet key in .env file...")
    
    # Read the current .env file
    with open('.env', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Generate a new valid Fernet key
    from generate_fernet_key import generate_fernet_key
    new_key = generate_fernet_key()
    
    # Replace the old key (with or without leading space)
    old_pattern = r'^\s*FERNET_KEY=.*$'
    new_line = f'FERNET_KEY={new_key}'
    
    # Replace the line
    new_content = re.sub(old_pattern, new_line, content, flags=re.MULTILINE)
    
    # Write back to .env file
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Fixed Fernet key: {new_key}")
    print("✅ .env file updated successfully!")

if __name__ == "__main__":
    fix_fernet_key() 