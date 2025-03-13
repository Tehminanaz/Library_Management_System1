-- MySQL setup script for library management system

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS library;

-- Use the database
USE library;

-- Create books table
CREATE TABLE IF NOT EXISTS books (
    bname VARCHAR(255) NOT NULL,
    bcode VARCHAR(50) PRIMARY KEY,
    total INT NOT NULL,
    subject VARCHAR(100) NOT NULL
);

-- Create issue table
CREATE TABLE IF NOT EXISTS issue (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    regno VARCHAR(50) NOT NULL,
    bcode VARCHAR(50) NOT NULL,
    idate DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE,
    returned TINYINT(1) DEFAULT 0,
    FOREIGN KEY (bcode) REFERENCES books(bcode)
);

-- Add sample books
INSERT IGNORE INTO books (bname, bcode, total, subject) VALUES
('The Great Gatsby', 'BOOK001', 5, 'Fiction'),
('To Kill a Mockingbird', 'BOOK002', 3, 'Fiction'),
('Introduction to Algorithms', 'BOOK003', 2, 'Computer Science'),
('Database Systems', 'BOOK004', 4, 'Computer Science'),
('Physics for Scientists and Engineers', 'BOOK005', 3, 'Science');

-- Create a user for the application (optional)
-- CREATE USER IF NOT EXISTS 'library_user'@'localhost' IDENTIFIED BY 'password';
-- GRANT ALL PRIVILEGES ON lmanage.* TO 'library_user'@'localhost';
-- FLUSH PRIVILEGES;

SELECT * FROM books;
SELECT * FROM issue;

