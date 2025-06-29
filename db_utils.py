#!/usr/bin/env python3
"""
Database utility script for the Expense Tracker
"""

import os
from app import create_app
from models import db, Expense, Category
from datetime import datetime, date

def init_db():
    """Initialize the database with tables"""
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

def reset_db():
    """Reset the database (drop and recreate all tables)"""
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database reset successfully!")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python db_utils.py [init|reset]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'init':
        init_db()
    elif command == 'reset':
        reset_db()
    else:
        print("Unknown command. Use: init, or reset")
