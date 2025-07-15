#!/usr/bin/env python
"""
Memory-optimized Django development server runner
This script helps prevent VS Code memory issues when running Django with ngrok
"""
import os
import sys
import subprocess
import signal
from pathlib import Path

def cleanup_django_processes():
    """Clean up any existing Django processes using taskkill"""
    try:
        # Kill any existing Django processes
        subprocess.run(['taskkill', '/f', '/im', 'python.exe', '/fi', 'WINDOWTITLE eq *manage.py*'], 
                      capture_output=True, text=True)
    except subprocess.CalledProcessError:
        pass  # No processes to kill

def run_django_optimized():
    """Run Django with memory optimizations"""
    # Set environment variables for memory optimization
    os.environ['PYTHONOPTIMIZE'] = '1'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    os.environ['DJANGO_SETTINGS_MODULE'] = 'ecm_website.settings'
    
    # Clean up before starting
    cleanup_django_processes()
    
    print("🚀 Starting Django with memory optimizations...")
    
    try:
        # Run Django with optimizations
        subprocess.run([
            sys.executable, 
            'manage.py', 
            'runserver', 
            '127.0.0.1:8000',
            '--noreload',  # Disable auto-reload to save memory
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Django server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Django server failed: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("Django Memory-Optimized Runner")
    print("=" * 40)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Run Django
    success = run_django_optimized()
    
    if success:
        print("✅ Django server finished successfully")
    else:
        print("❌ Django server encountered issues")
        sys.exit(1)

if __name__ == "__main__":
    main()
