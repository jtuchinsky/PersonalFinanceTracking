import requests
import sys
import json
from datetime import datetime, timezone
from typing import Dict, Any

class FinanceTrackerAPITester:
    def __init__(self, base_url="https://finance-dashboard-84.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.accounts = []
        self.categories = []

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}: PASSED {details}")
        else:
            print(f"❌ {name}: FAILED {details}")
        return success

    def make_request(self, method: str, endpoint: str, data: Dict[Any, Any] = None, expected_status: int = 200) -> tuple[bool, Dict[Any, Any]]:
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            
            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text}
            
            if not success:
                print(f"   Status: {response.status_code}, Expected: {expected_status}")
                print(f"   Response: {response_data}")
            
            return success, response_data
            
        except Exception as e:
            print(f"   Request failed: {str(e)}")
            return False, {"error": str(e)}

    def test_user_registration(self):
        """Test user registration with mock data creation"""
        print("\n🔍 Testing User Registration...")
        
        # Use unique timestamp-based email
        import time
        timestamp = str(int(time.time()))
        test_user = {
            "name": "Test User",
            "email": f"test{timestamp}@example.com",
            "password": "test123"
        }
        
        success, response = self.make_request('POST', 'auth/register', test_user, 200)
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_data = response['user']
            return self.log_test("User Registration", True, f"- Token received, User ID: {self.user_data['id']}")
        else:
            return self.log_test("User Registration", False, f"- Response: {response}")

    def test_existing_user_login(self):
        """Test login with existing user credentials"""
        print("\n🔍 Testing Existing User Login...")
        
        login_data = {
            "email": "testuser2607@example.com",
            "password": "test123456"
        }
        
        success, response = self.make_request('POST', 'auth/login', login_data, 200)
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_data = response['user']
            return self.log_test("Existing User Login", True, f"- Token received, User: {self.user_data['name']}")
        else:
            return self.log_test("Existing User Login", False, f"- Response: {response}")

    def test_user_login(self):
        """Test user login"""
        print("\n🔍 Testing User Login...")
        
        # Use unique timestamp-based email
        import time
        timestamp = str(int(time.time()))
        login_data = {
            "email": f"test{timestamp}@example.com",
            "password": "test123"
        }
        
        success, response = self.make_request('POST', 'auth/login', login_data, 200)
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_data = response['user']
            return self.log_test("User Login", True, f"- Token received, User: {self.user_data['name']}")
        else:
            return self.log_test("User Login", False, f"- Response: {response}")

    def test_get_accounts(self):
        """Test getting user accounts"""
        print("\n🔍 Testing Get Accounts...")
        
        success, response = self.make_request('GET', 'accounts', expected_status=200)
        
        if success and isinstance(response, list) and len(response) >= 3:
            self.accounts = response
            account_names = [acc['name'] for acc in response]
            expected_accounts = ['TD Bank Checking', 'TD Bank Savings', 'Chase Freedom Credit Card']
            
            has_expected = all(name in account_names for name in expected_accounts)
            
            if has_expected:
                return self.log_test("Get Accounts", True, f"- Found {len(response)} accounts: {account_names}")
            else:
                return self.log_test("Get Accounts", False, f"- Missing expected accounts. Found: {account_names}")
        else:
            return self.log_test("Get Accounts", False, f"- Expected list of accounts, got: {response}")

    def test_get_categories(self):
        """Test getting categories"""
        print("\n🔍 Testing Get Categories...")
        
        success, response = self.make_request('GET', 'categories', expected_status=200)
        
        if success and isinstance(response, list) and len(response) >= 8:
            self.categories = response
            category_names = [cat['name'] for cat in response]
            expected_categories = ['Food & Dining', 'Transportation', 'Bills & Utilities', 'Income']
            
            has_expected = all(name in category_names for name in expected_categories)
            
            if has_expected:
                return self.log_test("Get Categories", True, f"- Found {len(response)} categories")
            else:
                return self.log_test("Get Categories", False, f"- Missing expected categories. Found: {category_names}")
        else:
            return self.log_test("Get Categories", False, f"- Expected list of categories, got: {response}")

    def test_dashboard_data(self):
        """Test dashboard data endpoint"""
        print("\n🔍 Testing Dashboard Data...")
        
        success, response = self.make_request('GET', 'dashboard', expected_status=200)
        
        if success:
            required_fields = ['total_balance', 'monthly_spending', 'accounts', 'recent_transactions', 'category_spending']
            has_all_fields = all(field in response for field in required_fields)
            
            if has_all_fields:
                details = f"- Total Balance: ${response['total_balance']:.2f}, Monthly Spending: ${response['monthly_spending']:.2f}"
                details += f", Accounts: {len(response['accounts'])}, Recent Transactions: {len(response['recent_transactions'])}"
                return self.log_test("Dashboard Data", True, details)
            else:
                missing = [field for field in required_fields if field not in response]
                return self.log_test("Dashboard Data", False, f"- Missing fields: {missing}")
        else:
            return self.log_test("Dashboard Data", False, f"- Response: {response}")

    def test_create_transaction(self):
        """Test creating a new transaction"""
        print("\n🔍 Testing Create Transaction...")
        
        if not self.accounts:
            return self.log_test("Create Transaction", False, "- No accounts available")
        
        transaction_data = {
            "account_id": self.accounts[0]['id'],
            "amount": -50.00,
            "description": "Test Grocery Purchase",
            "category": "Food & Dining",
            "transaction_type": "debit",
            "date": datetime.now(timezone.utc).isoformat()
        }
        
        success, response = self.make_request('POST', 'transactions', transaction_data, 200)
        
        if success and 'id' in response:
            return self.log_test("Create Transaction", True, f"- Transaction ID: {response['id']}")
        else:
            return self.log_test("Create Transaction", False, f"- Response: {response}")

    def test_get_transactions(self):
        """Test getting transactions"""
        print("\n🔍 Testing Get Transactions...")
        
        success, response = self.make_request('GET', 'transactions', expected_status=200)
        
        if success and isinstance(response, list):
            return self.log_test("Get Transactions", True, f"- Found {len(response)} transactions")
        else:
            return self.log_test("Get Transactions", False, f"- Expected list of transactions, got: {response}")

    def test_get_transactions_with_filters(self):
        """Test getting transactions with filters"""
        print("\n🔍 Testing Get Transactions with Filters...")
        
        if not self.accounts:
            return self.log_test("Get Transactions with Filters", False, "- No accounts available")
        
        # Test account filter
        account_id = self.accounts[0]['id']
        success, response = self.make_request('GET', f'transactions?account_id={account_id}', expected_status=200)
        
        if success and isinstance(response, list):
            return self.log_test("Get Transactions with Filters", True, f"- Found {len(response)} transactions for account")
        else:
            return self.log_test("Get Transactions with Filters", False, f"- Response: {response}")

    def test_invalid_endpoints(self):
        """Test error handling for invalid requests"""
        print("\n🔍 Testing Error Handling...")
        
        # Test invalid login
        invalid_login = {"email": "invalid@test.com", "password": "wrong"}
        success, _ = self.make_request('POST', 'auth/login', invalid_login, 401)
        
        if success:
            self.log_test("Invalid Login Error", True, "- Correctly returned 401")
        else:
            self.log_test("Invalid Login Error", False, "- Should return 401 for invalid credentials")
        
        # Test unauthorized access (without token)
        old_token = self.token
        self.token = None
        success, _ = self.make_request('GET', 'dashboard', expected_status=403)
        self.token = old_token
        
        if success:
            return self.log_test("Unauthorized Access Error", True, "- Correctly returned 403")
        else:
            return self.log_test("Unauthorized Access Error", False, "- Should return 403 for unauthorized access")

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Finance Tracker API Tests")
        print(f"📍 Testing against: {self.base_url}")
        
        # Test registration and authentication
        if not self.test_user_registration():
            print("❌ Registration failed, stopping tests")
            return False
        
        # Test login (using same credentials)
        if not self.test_user_login():
            print("❌ Login failed, stopping tests")
            return False
        
        # Test core endpoints
        self.test_get_accounts()
        self.test_get_categories()
        self.test_dashboard_data()
        self.test_create_transaction()
        self.test_get_transactions()
        self.test_get_transactions_with_filters()
        
        # Test error handling
        self.test_invalid_endpoints()
        
        # Print summary
        print(f"\n📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    tester = FinanceTrackerAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())