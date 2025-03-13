# Database Connection Troubleshooting Guide

## MySQL Connection Error (Error 2003)

If you're seeing the error "Can't connect to MySQL server on 'localhost:3306' (10061)", here are steps to resolve it:

### 1. Verify MySQL is Running

#### Windows:
1. Open Task Manager (Ctrl+Shift+Esc)
2. Look for "mysqld.exe" or "MySQL" in the list of running processes
3. If not found, start MySQL:
   - Open Services (services.msc)
   - Find "MySQL" service
   - Right-click and select "Start"

#### Mac:
1. Open Terminal
2. Run: `sudo launchctl list | grep mysql`
3. If not running, start MySQL:
   - Run: `brew services start mysql` (if installed via Homebrew)
   - Or: `sudo /usr/local/mysql/support-files/mysql.server start`

#### Linux:
1. Open Terminal
2. Run: `sudo systemctl status mysql`
3. If not running, start MySQL:
   - Run: `sudo systemctl start mysql`

### 2. Check MySQL Connection Settings

Try connecting to MySQL using the command line:


