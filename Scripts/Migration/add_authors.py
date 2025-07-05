'''
# File: add_authors.py
# Path: Scripts/Migration/add_authors.py
# Description: Adds author information to the database from a CSV file.

import csv
import sqlite3
import os

def add_authors_to_database():
    """Reads author data from a CSV and updates the database."""
    db_path = 'Assets/my_library.db'
    csv_path = 'Data/Spreadsheets/AndersonLibrary_PDFMetadata.csv'

    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return

    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Add author column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE books ADD COLUMN author TEXT")
            print("Added 'author' column to 'books' table.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("'author' column already exists.")
            else:
                raise

        # Read CSV and update database
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                filename = row.get('filename')
                author = row.get('pdf_author')

                if filename and author:
                    # We need to get the title from the filename
                    title = os.path.splitext(filename)[0]
                    cursor.execute("UPDATE books SET author = ? WHERE title = ?", (author, title))

        conn.commit()
        print("Successfully updated authors in the database.")

    except (sqlite3.Error, IOError) as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    add_authors_to_database()
'''