#!/usr/bin/env python3
"""
Migration script to add appointment_files table
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_appointment_files_table():
    """Create the appointment_files table"""
    
    # Database connection
    database_url = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost/doctorpatient')
    engine = create_engine(database_url)
    
    # SQL to create the appointment_files table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS appointment_files (
        id VARCHAR(36) PRIMARY KEY,
        filename VARCHAR(255) NOT NULL,
        file_path VARCHAR(500) NOT NULL,
        file_size INTEGER NOT NULL,
        appointment_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        patient_id INTEGER NOT NULL,
        file_type VARCHAR(50),
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE,
        FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """
    
    try:
        with engine.connect() as conn:
            # Create the table
            conn.execute(text(create_table_sql))
            conn.commit()
            print("✓ appointment_files table created successfully!")
            
            # Create index for better performance
            index_sql = """
            CREATE INDEX IF NOT EXISTS idx_appointment_files_appointment_id 
            ON appointment_files(appointment_id);
            """
            conn.execute(text(index_sql))
            conn.commit()
            print("✓ Index created successfully!")
            
    except ProgrammingError as e:
        if "already exists" in str(e):
            print("ℹ appointment_files table already exists")
        else:
            print(f"❌ Error creating table: {e}")
            raise
    except Exception as e:
        print(f"❌ Database error: {e}")
        raise

if __name__ == "__main__":
    print("Starting appointment_files table migration...")
    create_appointment_files_table()
    print("Migration completed!") 