import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI

st.markdown("""
<style>
     body {
            background-color: #87CEEB !important;
            color: #ffffff; 
        }
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .success-msg {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #D1FAE5;
        border: 1px solid #10B981;
    }
    .warning-msg {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #FEF3C7;
        border: 1px solid #F59E0B;
    }
    .error-msg {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #FEE2E2;
        border: 1px solid #EF4444;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        color: #1E3A8A;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        border-top: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Database connection function
def get_sqlite_connection():
    try:
        conn = sqlite3.connect('library.db', check_same_thread=False)
        return conn, None
    except Exception as e:
        return None, e

# Function to execute SQL queries with error handling
def execute_query(query, data=None, fetch=False):
    # Convert MySQL queries to SQLite format if needed
    query = query.replace("AUTO_INCREMENT", "AUTOINCREMENT")
    query = query.replace("TINYINT(1)", "INTEGER")
    query = query.replace("CURDATE()", "date('now')")
    
    conn, error = get_sqlite_connection()
    
    if error:
        st.error(f"Database connection error: {error}")
        return None
    
    try:
        cursor = conn.cursor()
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
            
        if fetch:
            result = cursor.fetchall()
            cursor.close()
            return result
        else:
            conn.commit()
            cursor.close()
            return True
    except Exception as e:
        st.error(f"SQLite query execution error: {e}")
        return None
    finally:
        if conn:
            conn.close()

# Function to initialize database tables
def initialize_database():
    # Create books table for SQLite
    books_table = """
    CREATE TABLE IF NOT EXISTS books (
        bname TEXT NOT NULL,
        bcode TEXT PRIMARY KEY,
        total INTEGER NOT NULL,
        subject TEXT NOT NULL
    )
    """
    execute_query(books_table)
    
    # Create issue table for SQLite
    issue_table = """
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
    """
    execute_query(issue_table)
    
    # Add sample data if the tables are empty
    check_books = "SELECT COUNT(*) FROM books"
    result = execute_query(check_books, fetch=True)
    if result and result[0][0] == 0:
        # Add sample books
        sample_books = [
            ('The Great Gatsby', 'BOOK001', 5, 'Fiction'),
            ('To Kill a Mockingbird', 'BOOK002', 3, 'Fiction'),
            ('Introduction to Algorithms', 'BOOK003', 2, 'Computer Science'),
            ('Database Systems', 'BOOK004', 4, 'Computer Science'),
            ('Physics for Scientists and Engineers', 'BOOK005', 3, 'Science')
        ]
        
        for book in sample_books:
            insert_query = "INSERT INTO books (bname, bcode, total, subject) VALUES (?, ?, ?, ?)"
            execute_query(insert_query, book)

# Function to add a new book
def add_book():
    st.markdown("<h2 class='sub-header'>📚 Add a New Book</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        bname = st.text_input("Book Name", placeholder="Enter book title")
        bcode = st.text_input("Book Code", placeholder="Enter unique book code")
    
    with col2:
        total = st.number_input("Quantity", min_value=1, step=1)
        sub = st.text_input("Subject/Category", placeholder="Enter book subject")
    
    if st.button("Add Book", key="add_book_btn"):
        if bname and bcode and total and sub:
            # Check if book code already exists
            check_query = "SELECT bcode FROM books WHERE bcode = ?"
            result = execute_query(check_query, (bcode,), fetch=True)
            
            if result:
                st.markdown("<div class='warning-msg'>⚠️ Book with this code already exists!</div>", unsafe_allow_html=True)
            else:
                sql = "INSERT INTO books (bname, bcode, total, subject) VALUES (?, ?, ?, ?)"
                data = (bname, bcode, total, sub)
                if execute_query(sql, data):
                    st.markdown(f"<div class='success-msg'>✅ Book '{bname}' added successfully!</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='warning-msg'>⚠️ Please fill all fields before adding the book.</div>", unsafe_allow_html=True)

# Function to issue a book
def issue_book():
    st.markdown("<h2 class='sub-header'>📖 Issue a Book</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Student Name", placeholder="Enter student name")
        rno = st.text_input("Registration Number", placeholder="Enter registration number")
    
    with col2:
        # Fetch available books for selection
        books_query = "SELECT bname, bcode FROM books WHERE total > 0"
        books = execute_query(books_query, fetch=True)
        
        if books:
            book_options = {f"{book[0]} ({book[1]})": book[1] for book in books}
            selected_book = st.selectbox("Select Book", options=list(book_options.keys()))
            code = book_options[selected_book] if selected_book else ""
        else:
            st.warning("No books available for issue")
            code = st.text_input("Book Code", placeholder="Enter book code")
        
        date = st.date_input("Issue Date", value=datetime.now())
        due_date = st.date_input("Due Date", value=datetime.now() + timedelta(days=14))
    
    if st.button("Issue Book", key="issue_book_btn"):
        if name and rno and code:
            # Check if book exists and has stock
            check_query = "SELECT total FROM books WHERE bcode = ?"
            result = execute_query(check_query, (code,), fetch=True)
            
            if not result:
                st.markdown("<div class='error-msg'>❌ Book not found in the system.</div>", unsafe_allow_html=True)
            elif result[0][0] <= 0:
                st.markdown("<div class='warning-msg'>⚠️ Book is out of stock.</div>", unsafe_allow_html=True)
            else:
                # Check if student already has this book
                check_issue = "SELECT id FROM issue WHERE regno = ? AND bcode = ? AND returned = 0"
                issue_result = execute_query(check_issue, (rno, code), fetch=True)
                
                if issue_result:
                    st.markdown("<div class='warning-msg'>⚠️ This student already has this book issued.</div>", unsafe_allow_html=True)
                else:
                    sql = "INSERT INTO issue (name, regno, bcode, idate, due_date, returned) VALUES (?, ?, ?, ?, ?, ?)"
                    data = (name, rno, code, date, due_date, 0)
                    if execute_query(sql, data):
                        # Update book stock
                        update_query = "UPDATE books SET total = total - 1 WHERE bcode = ?"
                        if execute_query(update_query, (code,)):
                            st.markdown(f"<div class='success-msg'>📘 Book '{code}' issued to {name} successfully!</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='warning-msg'>⚠️ Please fill all fields before issuing the book.</div>", unsafe_allow_html=True)

# Function to return a book
def submit_book():
    st.markdown("<h2 class='sub-header'>📤 Return a Book</h2>", unsafe_allow_html=True)
    
    # Get list of issued books
    issued_query = """
    SELECT i.id, i.name, i.regno, b.bname, i.bcode, i.idate, i.due_date 
    FROM issue i 
    JOIN books b ON i.bcode = b.bcode 
    WHERE i.returned = 0
    """
    issued_books = execute_query(issued_query, fetch=True)
    
    if not issued_books:
        st.info("No books are currently issued")
        return
    
    # Create a DataFrame for better display
    df = pd.DataFrame(
        issued_books, 
        columns=["ID", "Student Name", "Reg No", "Book Name", "Book Code", "Issue Date", "Due Date"]
    )
    
    # Calculate overdue status
    today = datetime.now().date()
    df["Status"] = df["Due Date"].apply(lambda x: "Overdue" if x < today else "Active")
    df["Days Overdue"] = df["Due Date"].apply(lambda x: (today - x).days if x < today else 0)
    
    # Display the table with styling
    st.dataframe(df)
    
    # Return book form
    col1, col2 = st.columns(2)
    
    with col1:
        selected_id = st.selectbox("Select Issue ID to Return", options=df["ID"].tolist())
    
    with col2:
        return_date = st.date_input("Return Date", value=datetime.now())
    
    if st.button("Return Book", key="return_book_btn"):
        if selected_id:
            # Get the book code for the selected issue
            book_code_query = "SELECT bcode FROM issue WHERE id = ?"
            book_code_result = execute_query(book_code_query, (selected_id,), fetch=True)
            
            if book_code_result:
                book_code = book_code_result[0][0]
                
                # Mark as returned in issue table
                update_issue = "UPDATE issue SET returned = 1, return_date = ? WHERE id = ?"
                if execute_query(update_issue, (return_date, selected_id)):
                    # Update book stock
                    update_book = "UPDATE books SET total = total + 1 WHERE bcode = ?"
                    if execute_query(update_book, (book_code,)):
                        st.markdown(f"<div class='success-msg'>📘 Book returned successfully!</div>", unsafe_allow_html=True)
                        st.rerun()
        else:
            st.markdown("<div class='warning-msg'>⚠️ Please select an issue to return.</div>", unsafe_allow_html=True)

# Function to delete a book
def delete_book():
    st.markdown("<h2 class='sub-header'>🗑️ Delete a Book</h2>", unsafe_allow_html=True)
    
    # Get list of books
    books_query = "SELECT bname, bcode, total, subject FROM books"
    books = execute_query(books_query, fetch=True)
    
    if not books:
        st.info("No books available in the library")
        return
    
    # Create a DataFrame for better display
    df = pd.DataFrame(books, columns=["Book Name", "Book Code", "Available", "Subject"])
    st.dataframe(df)
    
    # Book deletion form
    book_codes = [book[1] for book in books]
    selected_code = st.selectbox("Select Book Code to Delete", options=book_codes)
    
    if st.button("Delete Book", key="delete_book_btn"):
        if selected_code:
            # Check if book is currently issued
            check_issued = "SELECT id FROM issue WHERE bcode = ? AND returned = 0"
            issued_result = execute_query(check_issued, (selected_code,), fetch=True)
            
            if issued_result:
                st.markdown("<div class='warning-msg'>⚠️ Cannot delete book as it is currently issued to students.</div>", unsafe_allow_html=True)
            else:
                delete_query = "DELETE FROM books WHERE bcode = ?"
                if execute_query(delete_query, (selected_code,)):
                    st.markdown("<div class='success-msg'>🗑️ Book deleted successfully!</div>", unsafe_allow_html=True)
                    st.rerun()
        else:
            st.markdown("<div class='warning-msg'>⚠️ Please select a book to delete.</div>", unsafe_allow_html=True)

# Function to display all books
def display_books():
    st.markdown("<h2 class='sub-header'>📚 Library Books</h2>", unsafe_allow_html=True)
    
    # Search functionality
    search_term = st.text_input("Search by book name or subject", placeholder="Enter search term...")
    
    # Get books with optional search filter
    if search_term:
        books_query = """
        SELECT bname, bcode, total, subject FROM books 
        WHERE bname LIKE ? OR subject LIKE ?
        ORDER BY bname
        """
        search_param = f"%{search_term}%"
        books = execute_query(books_query, (search_param, search_param), fetch=True)
    else:
        books_query = "SELECT bname, bcode, total, subject FROM books ORDER BY bname"
        books = execute_query(books_query, fetch=True)
    
    if books:
        # Create a DataFrame for better display
        df = pd.DataFrame(books, columns=["Book Name", "Book Code", "Available", "Subject"])
        
        # Add filters
        col1, col2 = st.columns(2)
        with col1:
            subjects = ["All"] + sorted(list(set([book[3] for book in books])))
            selected_subject = st.selectbox("Filter by Subject", options=subjects)
        
        with col2:
            availability = st.checkbox("Show only available books")
        
        # Apply filters
        filtered_df = df
        if selected_subject != "All":
            filtered_df = filtered_df[filtered_df["Subject"] == selected_subject]
        
        if availability:
            filtered_df = filtered_df[filtered_df["Available"] > 0]
        
        # Display the table
        st.dataframe(filtered_df, use_container_width=True)
        
        # Display statistics
        st.markdown("### 📊 Library Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Books", len(df))
        with col2:
            st.metric("Available Books", df["Available"].sum())
        with col3:
            st.metric("Unique Subjects", len(df["Subject"].unique()))
    else:
        st.info("📌 No books available in the library.")

# Function to view issued books and overdue reports
def view_reports():
    st.markdown("<h2 class='sub-header'>📊 Library Reports</h2>", unsafe_allow_html=True)
    
    report_type = st.radio(
        "Select Report Type",
        ["Currently Issued Books", "Overdue Books", "Return History"]
    )
    
    if report_type == "Currently Issued Books":
        issued_query = """
        SELECT i.name, i.regno, b.bname, i.bcode, i.idate, i.due_date 
        FROM issue i 
        JOIN books b ON i.bcode = b.bcode 
        WHERE i.returned = 0
        ORDER BY i.due_date
        """
        issued_books = execute_query(issued_query, fetch=True)
        
        if issued_books:
            df = pd.DataFrame(
                issued_books, 
                columns=["Student Name", "Reg No", "Book Name", "Book Code", "Issue Date", "Due Date"]
            )
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No books are currently issued")
    
    elif report_type == "Overdue Books":
        today = datetime.now().date()
        
        # Use SQLite syntax
        overdue_query = """
        SELECT i.name, i.regno, b.bname, i.bcode, i.idate, i.due_date 
        FROM issue i 
        JOIN books b ON i.bcode = b.bcode 
        WHERE i.returned = 0 AND i.due_date < date('now')
        ORDER BY i.due_date
        """
        overdue_books = execute_query(overdue_query, fetch=True)
        
        if overdue_books:
            df = pd.DataFrame(
                overdue_books, 
                columns=["Student Name", "Reg No", "Book Name", "Book Code", "Issue Date", "Due Date"]
            )
            # Calculate days overdue
            df["Days Overdue"] = df["Due Date"].apply(lambda x: (today - x).days)
            st.dataframe(df, use_container_width=True)
        else:
            st.success("No overdue books!")
    
    else:  # Return History
        history_query = """
        SELECT i.name, i.regno, b.bname, i.bcode, i.idate, i.return_date 
        FROM issue i 
        JOIN books b ON i.bcode = b.bcode 
        WHERE i.returned = 1
        ORDER BY i.return_date DESC
        LIMIT 100
        """
        history = execute_query(history_query, fetch=True)
        
        if history:
            df = pd.DataFrame(
                history, 
                columns=["Student Name", "Reg No", "Book Name", "Book Code", "Issue Date", "Return Date"]
            )
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No return history available")

# Function for login with proper authentication
def login():
 
    st.markdown("<h1 class='main-header'>🔐 Library Management System</h1>", unsafe_allow_html=True)
    
    # In a real application, you would store usernames and hashed passwords in the database
    # For this example, we'll use a simple dictionary
    valid_users = {
        "admin": "12345",
        "librarian": "library2025"
    }
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image("picture.jpg", caption="Library Management System")
    
    with col2:
        st.markdown("### Login to Access Library System")
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        if st.button("Login", key="login_btn"):
            if username in valid_users and password == valid_users[username]:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.rerun()
            else:
                st.markdown("<div class='error-msg'>❌ Invalid username or password!</div>", unsafe_allow_html=True)

# Main function to navigate between options
def main():
    # Check SQLite database connection
    conn, error = get_sqlite_connection()
    if error:
        st.error(f"Database connection error: {error}")
        return

    # Close connection if it was successful
    if conn:
        conn.close()
    
    # Initialize database tables
    initialize_database()
    
    # Authentication check
    if not st.session_state.authenticated:
        login()
        return
    
    # Sidebar for navigation
    st.sidebar.markdown(f"### Welcome, {st.session_state.get('username', 'User')}!")
    
    st.sidebar.markdown("## 📚 Library Management Menu")
    choice = st.sidebar.radio("Select an option:", [
        "📊 Dashboard",
        "📚 View Books",
        "➕ Add Book",
        "📖 Issue Book",
        "📤 Return Book",
        "🗑️ Delete Book",
        "📋 Reports"
    ])
    
    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()
    
    # Main content based on selection
    if choice == "📊 Dashboard":
        st.markdown("<h1 class='main-header'>📊 Library Management Dashboard</h1>", unsafe_allow_html=True)
        
        # Get statistics
        total_books_query = "SELECT COUNT(*), SUM(total) FROM books"
        total_books_result = execute_query(total_books_query, fetch=True)
        
        issued_books_query = "SELECT COUNT(*) FROM issue WHERE returned = 0"
        issued_books_result = execute_query(issued_books_query, fetch=True)
        
        # Use SQLite syntax for overdue query
        overdue_query = "SELECT COUNT(*) FROM issue WHERE returned = 0 AND due_date < date('now')"
        overdue_result = execute_query(overdue_query, fetch=True)
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Book Titles", total_books_result[0][0] if total_books_result else 0)
            st.metric("Total Book Copies", total_books_result[0][1] if total_books_result else 0)
        with col2:
            st.metric("Currently Issued", issued_books_result[0][0] if issued_books_result else 0)
        with col3:
            st.metric("Overdue Books", overdue_result[0][0] if overdue_result else 0)
        
        # Recent activities
        st.markdown("### Recent Activities")

        # For SQLite, handle recent activities
        recent_issues = """
        SELECT 'Issue' as action, name, bcode, idate as date 
        FROM issue 
        WHERE returned = 0 
        ORDER BY idate DESC LIMIT 5
        """
        recent_returns = """
        SELECT 'Return' as action, name, bcode, return_date as date 
        FROM issue 
        WHERE returned = 1 
        ORDER BY return_date DESC LIMIT 5
        """

        # Execute both queries separately and combine results
        issues = execute_query(recent_issues, fetch=True) or []
        returns = execute_query(recent_returns, fetch=True) or []

        # Combine and sort manually
        recent_activities = sorted(issues + returns, key=lambda x: x[3], reverse=True)[:10]

        if recent_activities:
            df = pd.DataFrame(
                recent_activities, 
                columns=["Action", "Student Name", "Book Code", "Date"]
            )
            st.dataframe(df, use_container_width=True)
    
    elif choice == "📚 View Books":
        display_books()
    elif choice == "➕ Add Book":
        add_book()
    elif choice == "📖 Issue Book":
        issue_book()
    elif choice == "📤 Return Book":
        submit_book()
    elif choice == "🗑️ Delete Book":
        delete_book()
    elif choice == "📋 Reports":
        view_reports()
# Add footer with student information
    st.markdown(
        """
        <div class="footer">
            Developed by: Tehmina naz
        </div>
        """,
        unsafe_allow_html=True
    )
if __name__ == "__main__":
    main()

