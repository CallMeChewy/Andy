# Add this to the end of your Source/Data/DatabaseModels.py file:

# Complete the COMMON_QUERIES section (it was cut off)
COMMON_QUERIES = {
    "SELECT_ALL": "SELECT * FROM Books",
    "SELECT_BY_ID": "SELECT * FROM Books WHERE Id = ?",
    "SELECT_BY_TITLE": "SELECT * FROM Books WHERE Title LIKE ?",
    "SELECT_BY_AUTHOR": "SELECT * FROM Books WHERE Author LIKE ?",
    "COUNT_TOTAL": "SELECT COUNT(*) FROM Books",
    "GET_CATEGORIES": "SELECT DISTINCT Category FROM Books WHERE Category IS NOT NULL ORDER BY Category",
    "GET_AUTHORS": "SELECT DISTINCT Author FROM Books WHERE Author IS NOT NULL ORDER BY Author",
    "GET_SUBJECTS": "SELECT DISTINCT Subject FROM Books WHERE Subject IS NOT NULL ORDER BY Subject"
}

# Legacy compatibility - add aliases for old class names AND function names
Book = BookRecord  # Compatibility alias
Category = CategoryInfo  # Compatibility alias  
Subject = CategoryInfo  # Compatibility alias for subjects
CreateBookFromRow = CreateBookRecordFromDict  # Compatibility alias for old function name