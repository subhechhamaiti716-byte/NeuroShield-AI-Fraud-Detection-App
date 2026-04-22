import requests

BASE_URL = "http://127.0.0.1:8000"

def test_flow():
    # 1. Health check
    print("Health:", requests.get(f"{BASE_URL}/health").json())

    # 2. DB check
    print("DB Check:", requests.get(f"{BASE_URL}/test-db").json())

    # 3. Register
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "1234567890",
        "password": "password123"
    }
    print("Registering...")
    res = requests.post(f"{BASE_URL}/auth/signup", json=user_data)
    print(res.status_code, res.text)
    
    # 4. Login
    print("Logging in...")
    login_data = {
        "username": "test@example.com",
        "password": "password123"
    }
    res = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    print(res.status_code, res.text)
    if res.status_code == 200:
        token = res.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # 5. Access protected route
        res = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print("Me:", res.status_code, res.text)
        
        # 6. Add transaction
        tx_data = {
            "amount": 100.0,
            "currency": "USD",
            "merchant": "Test Merchant",
            "transaction_type": "purchase",
            "location": "Test City",
            "device_id": "test_device"
        }
        print("Adding Transaction...")
        res = requests.post(f"{BASE_URL}/transactions/", json=tx_data, headers=headers)
        print("Transaction:", res.status_code, res.text)

if __name__ == "__main__":
    test_flow()
