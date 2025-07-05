# File: add_authors_v2.py
# Path: Scripts/Migration/add_authors_v2.py
# Description: Adds author information to the database from a CSV file.

import csv
import sqlite3
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def add_authors_to_database():
    """Reads author data from a CSV and updates the database."""
    db_path = 'Assets/my_library.db'
    csv_path = 'Data/Spreadsheets/AndersonLibrary_PDFMetadata.csv'

    if not os.path.exists(db_path):
        logging.error(f"Database file not found at {db_path}")
        return

    if not os.path.exists(csv_path):
        logging.error(f"CSV file not found at {csv_path}")
        return

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if the column already exists
        cursor.execute("PRAGMA table_info(books)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'author' not in columns:
            logging.info("Adding 'author' column to 'books' table.")
            cursor.execute("ALTER TABLE books ADD COLUMN author TEXT")
        else:
            logging.info("'author' column already exists.")

        # Read CSV and update database
        logging.info(f"Reading data from {csv_path}")
        updated_count = 0
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                filename = row.get('filename')
                author = row.get('pdf_author')

                if filename and author:
                    title = os.path.splitext(filename)[0]
                    # Use a case-insensitive match for the title
                    cursor.execute("UPDATE books SET author = ? WHERE lower(title) = ?", (author, title.lower()))
                    if cursor.rowcount > 0:
                        updated_count += 1

        conn.commit()
        logging.info(f"Successfully updated {updated_count} authors in the database.")

    except (sqlite3.Error, IOError) as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    add_authors_to_database()
