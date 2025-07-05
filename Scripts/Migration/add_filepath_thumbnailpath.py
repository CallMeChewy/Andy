import sqlite3
import os
import logging
import csv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def add_filepath_thumbnailpath():
    db_path = 'Assets/my_library.db'
    csv_path = 'Data/Spreadsheets/AndersonLibrary_PDFMetadata.csv'
    thumbnails_dir = 'Data/Thumbs/'
    books_dir = 'Data/Books/'

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

        # Add FilePath column if it doesn't exist
        cursor.execute("PRAGMA table_info(books)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'FilePath' not in columns:
            logging.info("Adding 'FilePath' column to 'books' table.")
            cursor.execute("ALTER TABLE books ADD COLUMN FilePath TEXT")
        else:
            logging.info("'FilePath' column already exists.")

        # Add ThumbnailPath column if it doesn't exist
        cursor.execute("PRAGMA table_info(books)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'ThumbnailPath' not in columns:
            logging.info("Adding 'ThumbnailPath' column to 'books' table.")
            cursor.execute("ALTER TABLE books ADD COLUMN ThumbnailPath TEXT")
        else:
            logging.info("'ThumbnailPath' column already exists.")

        # Read CSV and update database
        logging.info(f"Reading data from {csv_path}")
        updated_count = 0
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                filename = row.get('filename')
                
                if filename:
                    title = os.path.splitext(filename)[0]
                    file_path = os.path.join(books_dir, filename)
                    thumbnail_path = os.path.join(thumbnails_dir, f"{title}.png") # Assuming PNG thumbnails

                    cursor.execute("UPDATE books SET FilePath = ?, ThumbnailPath = ? WHERE lower(title) = ?", 
                                   (file_path, thumbnail_path, title.lower()))
                    if cursor.rowcount > 0:
                        updated_count += 1

        conn.commit()
        logging.info(f"Successfully updated {updated_count} FilePath and ThumbnailPath entries in the database.")

    except (sqlite3.Error, IOError) as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    add_filepath_thumbnailpath()