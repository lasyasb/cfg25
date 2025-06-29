#!/usr/bin/env python
"""
Script to compile Django translation messages for Visions India project
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def compile_translations():
    """Compile all translation messages"""
    try:
        # Compile messages for all languages
        execute_from_command_line(['manage.py', 'compilemessages'])
        print("✅ Translation compilation completed successfully!")
        print("🌍 Languages available: English, Tamil (தமிழ்), Hindi (हिंदी)")
        print("🚀 You can now switch languages using the language selector on the homepage!")
    except Exception as e:
        print(f"❌ Error compiling translations: {e}")
        print("💡 Make sure you have gettext installed on your system")

if __name__ == "__main__":
    compile_translations() 