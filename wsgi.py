#!/usr/bin/env python3
"""
WSGI configuration for the Nova88 Telegram Bot
"""
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from main import app

if __name__ == "__main__":
    app.run()