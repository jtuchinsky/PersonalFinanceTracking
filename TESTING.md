# Testing Guide - Personal Finance Tracker

This document provides comprehensive instructions for running tests in the Personal Finance Tracker application from both the terminal and PyCharm IDE.

## Table of Contents
- [Test Overview](#test-overview)
- [Prerequisites](#prerequisites)
- [Backend Testing](#backend-testing)
  - [Terminal Instructions](#backend-terminal-instructions)
  - [PyCharm Instructions](#backend-pycharm-instructions)
- [Frontend Testing](#frontend-testing)
  - [Terminal Instructions](#frontend-terminal-instructions)
  - [PyCharm Instructions](#frontend-pycharm-instructions)
- [Test Results Reference](#test-results-reference)

---

## Test Overview

The project contains the following test suites:

### Backend Tests
1. **MongoDB Connection Test** (`test_connection.py`)
   - Tests database connectivity
   - Validates CRUD operations
   - Verifies collection access

2. **API Integration Tests** (`backend_test.py`)
   - Comprehensive API endpoint testing
   - User authentication flow
   - Account management operations
   - Transaction operations
   - Security validation

### Frontend Tests
- User Frontend (`frontend/`)
- Admin Frontend (`frontend-admin/`)
- Uses Jest and React Testing Library (Create React App default)

---

## Prerequisites

### Backend Prerequisites
1. **Python Environment**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   - Ensure `backend/.env` file exists with:
     - `MONGO_URL` - MongoDB connection string
     - `DB_NAME` - Database name
     - `JWT_SECRET` - JWT secret key
     - `ENCRYPTION_KEY` - Encryption key for credentials

3. **MongoDB Access**
   - MongoDB Atlas connection must be active
   - Database must be accessible from your network

### Frontend Prerequisites
1. **Node.js and Yarn**
   ```bash
   # User Frontend
   cd frontend
   yarn install

   # Admin Frontend
   cd frontend-admin
   yarn install
   ```

---

## Backend Testing

### Backend Terminal Instructions

#### 1. MongoDB Connection Test

**Purpose**: Verify database connectivity and basic operations

```bash
# From project root
python test_connection.py
```

**Expected Output**:
```
🔗 Testing MongoDB Atlas Connection
==================================================
✅ MongoDB connection successful!
📋 Found X collections:
   • accounts: X documents
   • users: X documents
   ...
🧪 Testing basic operations...
✅ Insert test successful
✅ Read test successful
✅ Delete test successful
🎉 All tests passed!
```

#### 2. API Integration Tests

**Important**: These tests require a running backend server.

**Step 1: Start the Backend Server**
```bash
# Terminal 1 - Start User Server
cd backend
python user_server.py
# Server runs on http://localhost:8000
```

**Step 2: Update Test Configuration**
```bash
# Edit backend_test.py line 8 to use local server:
# Change:
# base_url="https://finance-dashboard-84.preview.emergentagent.com/api"
# To:
# base_url="http://localhost:8000/api"
```

**Step 3: Run Tests**
```bash
# Terminal 2 - From project root
python backend_test.py
```

**Expected Output**:
```
🚀 Starting Finance Tracker API Tests
📍 Testing against: http://localhost:8000/api

✅ Existing User Login: PASSED
✅ Get Accounts: PASSED - Found 3 accounts
✅ Get Categories: PASSED - Found 8 categories
✅ Dashboard Data: PASSED
✅ Create Account: PASSED
...

📊 Test Summary: X/X tests passed
🎉 All tests passed!
```

#### 3. Running with Pytest

While the main test files are standalone scripts, you can use pytest for any future test modules:

```bash
# Install pytest if not already installed
pip install pytest pytest-asyncio

# Run all pytest-compatible tests
python -m pytest -v

# Run specific test file
python -m pytest backend_test.py -v

# Run with detailed output
python -m pytest -v --tb=long
```

### Backend PyCharm Instructions

#### Method 1: Run Individual Test Files

1. **Open the test file** (`test_connection.py` or `backend_test.py`)

2. **Right-click anywhere in the editor**

3. **Select "Run 'test_connection'" or "Run 'backend_test'"**

4. **View results in the Run tool window** (bottom panel)

#### Method 2: Using Run Configurations

**For MongoDB Connection Test:**

1. Click **Run > Edit Configurations**
2. Click **+** (Add New Configuration) > **Python**
3. Configure:
   - **Name**: `MongoDB Connection Test`
   - **Script path**: `/path/to/test_connection.py`
   - **Working directory**: `/path/to/PersonalFinanceTracking`
   - **Python interpreter**: Select your project interpreter
4. Click **OK**
5. Click the **Run** button (green play icon)

**For API Integration Tests:**

1. Click **Run > Edit Configurations**
2. Click **+** (Add New Configuration) > **Python**
3. Configure:
   - **Name**: `API Integration Tests`
   - **Script path**: `/path/to/backend_test.py`
   - **Working directory**: `/path/to/PersonalFinanceTracking`
   - **Python interpreter**: Select your project interpreter
4. Click **OK**
5. **Important**: Start the backend server first in a separate terminal
6. Click the **Run** button

#### Method 3: Using PyCharm's Test Runner

1. **Right-click on the test file** in the Project view
2. **Select "Run 'pytest in test_connection.py'"**
3. PyCharm will automatically detect and run the tests
4. View results in the Test Runner panel with color-coded pass/fail indicators

#### Debugging Tests in PyCharm

1. **Set breakpoints** by clicking in the left gutter of the code editor
2. **Right-click the test file** or configuration
3. **Select "Debug 'test_connection'" or "Debug 'backend_test'"**
4. Use the **Debug panel** to:
   - Step through code (F8)
   - Inspect variables
   - Evaluate expressions
   - View call stack

---

## Frontend Testing

### Frontend Terminal Instructions

#### User Frontend Tests

```bash
# Navigate to user frontend
cd frontend

# Run all tests
yarn test

# Run tests in CI mode (non-interactive)
CI=true yarn test

# Run tests with coverage
yarn test --coverage

# Run specific test file
yarn test Dashboard.test.js

# Run tests matching a pattern
yarn test --testNamePattern="renders correctly"
```

#### Admin Frontend Tests

```bash
# Navigate to admin frontend
cd frontend-admin

# Run all tests
yarn test

# Run tests in CI mode
CI=true yarn test

# Run with coverage
yarn test --coverage
```

#### Common Test Commands

```bash
# Watch mode (re-runs tests on file changes)
yarn test --watch

# Update snapshots
yarn test -u

# Verbose output
yarn test --verbose

# Run tests and exit (useful for CI)
yarn test --watchAll=false
```

### Frontend PyCharm Instructions

#### Method 1: Using NPM/Yarn Scripts

1. **Open `package.json`** in the frontend or frontend-admin directory

2. **Locate the "scripts" section**

3. **Click the green play icon** next to `"test": "react-scripts test"`

4. **Select "Run 'test'"**

5. **View results** in the Run tool window

#### Method 2: Using Run Configurations

1. Click **Run > Edit Configurations**
2. Click **+** > **npm**
3. Configure:
   - **Name**: `Frontend Tests` (or `Admin Frontend Tests`)
   - **package.json**: Select the appropriate package.json
   - **Command**: `run`
   - **Scripts**: `test`
   - **Environment variables** (optional): `CI=true` for non-interactive mode
4. Click **OK**
5. Click **Run**

#### Method 3: Using Jest Plugin (Recommended)

1. **Install the Jest plugin** (if not already installed):
   - Go to **Settings > Plugins**
   - Search for "Jest"
   - Install and restart PyCharm

2. **Configure Jest**:
   - Go to **Settings > Languages & Frameworks > JavaScript > Jest**
   - Check "Enable Jest"
   - Set **Jest package**: `frontend/node_modules/jest` or `frontend-admin/node_modules/jest`
   - Set **Configuration file**: Auto-detect or specify `frontend/package.json`

3. **Run tests**:
   - **Right-click any test file** in Project view
   - Select **"Run 'YourTest.test.js'"**
   - Or use **Ctrl+Shift+F10** (Windows/Linux) or **Cmd+Shift+R** (Mac)

4. **View results**:
   - Color-coded test results in Test Runner panel
   - Click individual tests to see details
   - Re-run failed tests only

#### Debugging Frontend Tests

1. **Set breakpoints** in your test files or component files
2. **Right-click the test file**
3. **Select "Debug 'YourTest.test.js'"**
4. Tests will pause at breakpoints
5. Use **Debug panel** to inspect state and variables

---

## Test Results Reference

### Successful Test Indicators

#### Terminal
- ✅ Green checkmarks
- "PASSED" status
- "All tests passed!" message
- Exit code 0

#### PyCharm
- Green progress bar
- Green checkmarks next to test names
- "All tests passed" message in status bar
- No red indicators

### Failed Test Indicators

#### Terminal
- ❌ Red X marks
- "FAILED" status
- Error messages and stack traces
- Exit code 1

#### PyCharm
- Red progress bar
- Red X marks next to failed tests
- Error messages in test output
- Clickable links to error locations

---

## Quick Reference Commands

### Backend Tests (Terminal)
```bash
# MongoDB connection test
python test_connection.py

# API integration tests (requires running server)
python backend_test.py

# Pytest
python -m pytest -v
```

### Frontend Tests (Terminal)
```bash
# User frontend
cd frontend && yarn test

# Admin frontend
cd frontend-admin && yarn test

# CI mode (non-interactive)
CI=true yarn test

# With coverage
yarn test --coverage
```

### PyCharm Shortcuts
- **Run tests**: `Ctrl+Shift+F10` (Windows/Linux) or `Cmd+Shift+R` (Mac)
- **Debug tests**: `Ctrl+Shift+F9` (Windows/Linux) or `Cmd+Shift+D` (Mac)
- **Re-run last test**: `Shift+F10` (Windows/Linux) or `Ctrl+R` (Mac)
- **Re-run failed tests**: Click "Rerun Failed Tests" icon in Test Runner

---

## Continuous Integration

For automated testing in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Backend Tests
  run: |
    python test_connection.py
    # API tests require running server - handle separately

- name: Frontend Tests
  run: |
    cd frontend
    CI=true yarn test --coverage

    cd ../frontend-admin
    CI=true yarn test --coverage
```

---

## Troubleshooting

### Common Issues

1. **MongoDB Connection Fails**
   - Verify `MONGO_URL` in `backend/.env`
   - Check network connectivity
   - Verify MongoDB Atlas whitelist settings

2. **API Tests Fail**
   - Ensure backend server is running on correct port
   - Verify `base_url` in `backend_test.py`
   - Check server logs for errors

3. **Frontend Tests Fail**
   - Clear node_modules and reinstall: `rm -rf node_modules && yarn install`
   - Clear Jest cache: `yarn test --clearCache`
   - Check for Node.js version compatibility

4. **PyCharm Doesn't Detect Tests**
   - Verify Python interpreter is configured correctly
   - Check test framework settings in Preferences
   - Invalidate caches: **File > Invalidate Caches / Restart**

---

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [PyCharm Testing Guide](https://www.jetbrains.com/help/pycharm/testing-your-first-python-application.html)

---

**Last Updated**: 2025-12-20
**Version**: 1.0