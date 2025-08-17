#!/usr/bin/env python
"""
Generate a secure SECRET_KEY for Django
"""
import secrets
import sys

def generate_django_secret_key(length=50):
    """
    Generate a secure random string suitable for Django's SECRET_KEY
    """
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(chars) for _ in range(length))

if __name__ == "__main__":
    # Generate key with default length of 50 characters
    key = generate_django_secret_key()
    
    print("\n=== SECURE DJANGO SECRET KEY ===\n")
    print(f"SECRET_KEY={key}")
    print("\n================================\n")
    print("Copy this key to your .env file")
    
    # If argument --update is provided, attempt to update .env file
    if len(sys.argv) > 1 and sys.argv[1] == "--update":
        try:
            import os
            from pathlib import Path
            
            # Get the base directory
            BASE_DIR = Path(__file__).resolve().parent.parent
            
            # Path to .env file
            env_path = BASE_DIR / '.env'
            
            if not env_path.exists():
                print(f"Error: .env file not found at {env_path}")
                sys.exit(1)
                
            # Read current .env file
            with open(env_path, 'r') as f:
                env_lines = f.readlines()
                
            # Replace or add SECRET_KEY
            secret_key_found = False
            with open(env_path, 'w') as f:
                for line in env_lines:
                    if line.startswith('SECRET_KEY='):
                        f.write(f"SECRET_KEY={key}\n")
                        secret_key_found = True
                    else:
                        f.write(line)
                        
                # Add SECRET_KEY if not found
                if not secret_key_found:
                    f.write(f"\nSECRET_KEY={key}\n")
                    
            print(f"✅ Updated SECRET_KEY in {env_path}")
            
        except Exception as e:
            print(f"Error updating .env file: {e}")
            sys.exit(1)
