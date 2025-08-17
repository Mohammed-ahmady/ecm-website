# Script to generate a secure SECRET_KEY
import secrets
import os
import sys
from pathlib import Path

def generate_secret_key(length=64):
    """Generate a secure SECRET_KEY with specified length"""
    return secrets.token_urlsafe(length)

def update_env_file():
    """Update .env file with a secure SECRET_KEY"""
    # Get the base directory of the project
    base_dir = Path(__file__).resolve().parent.parent
    env_path = base_dir / '.env'
    
    if not env_path.exists():
        print(f"❌ No .env file found at {env_path}")
        return
    
    # Read current content
    with open(env_path, 'r') as f:
        env_content = f.readlines()
    
    # Generate new secret key
    new_secret_key = generate_secret_key()
    
    # Update SECRET_KEY line or add if not found
    secret_key_found = False
    for i, line in enumerate(env_content):
        if line.strip().startswith('SECRET_KEY='):
            env_content[i] = f'SECRET_KEY={new_secret_key}\n'
            secret_key_found = True
            break
    
    if not secret_key_found:
        env_content.append(f'SECRET_KEY={new_secret_key}\n')
    
    # Write updated content
    with open(env_path, 'w') as f:
        f.writelines(env_content)
    
    print(f"✅ SECRET_KEY has been updated in .env file")
    print(f"New SECRET_KEY: {new_secret_key}")
    print(f"Length: {len(new_secret_key)} characters")
    
if __name__ == "__main__":
    update_env_file()
    print("Run 'python manage.py check --deploy' to confirm the warning is resolved.")
