import sqlite3

def setup_sqlite_database():
    """
    Set up a SQLite database for the library management system.
    This script creates the necessary tables and adds some sample data.
    """
    # Connect to SQLite database (will create it if it doesn't exist)
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    # Create books table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        bname TEXT NOT NULL,
        bcode TEXT PRIMARY KEY,
        total INTEGER NOT NULL,
        subject TEXT NOT NULL
    )
    ''')
    
    # Create issue table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS issue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        regno TEXT NOT NULL,
        bcode TEXT NOT NULL,
        idate DATE NOT NULL,
        due_date DATE NOT NULL,
        return_date DATE,
        returned INTEGER DEFAULT 0,
        FOREIGN KEY (bcode) REFERENCES books(bcode)
    )
    ''')
    
    # Add sample books
    sample_books = [
        ('The Great Gatsby', 'BOOK001', 5, 'Fiction'),
        ('To Kill a Mockingbird', 'BOOK002', 3, 'Fiction'),
        ('Introduction to Algorithms', 'BOOK003', 2, 'Computer Science'),
        ('Database Systems', 'BOOK004', 4, 'Computer Science'),
        ('Physics for Scientists and Engineers', 'BOOK005', 3, 'Science')
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO books (bname, bcode, total, subject) VALUES (?, ?, ?, ?)
    ''', sample_books)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("SQLite database setup complete!")

if __name__ == "__main__":
    setup_sqlite_database()

