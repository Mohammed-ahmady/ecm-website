#!/usr/bin/env python
"""
Script to prepare database for caching operations.
Run this before deployment to create the cache table.
"""
import os
import sys
import django
from django.core.management import call_command

if __name__ == "__main__":
    # Setup Django environment
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecm_website.settings")
    django.setup()
    
    # Create cache table
    try:
        print("Creating cache table...")
        call_command("createcachetable")
        print("✅ Cache table created successfully.")
    except Exception as e:
        print(f"❌ Error creating cache table: {e}")
        sys.exit(1)
    
    # Show migrations status
    try:
        print("\nChecking migrations status...")
        call_command("showmigrations")
    except Exception as e:
        print(f"❌ Error checking migrations: {e}")
    
    print("\n✅ Database preparation complete.")
