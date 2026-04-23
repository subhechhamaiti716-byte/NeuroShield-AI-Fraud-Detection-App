import requests

BASE = "https://neuroshield-ai-fraud-detection-app.onrender.com"

# Test login with form data (OAuth2PasswordRequestForm)
print("Testing login...")
res = requests.post(f"{BASE}/auth/login", data={
    "username": "subhechhamaiti716@gmail.com",
    "password": "P$aLm23_My-L0RD"
})
print(f"Status: {res.status_code}")
print(f"Response: {res.text}")

if res.status_code == 200:
    token = res.json().get("access_token")
    print(f"\nToken: {token[:30]}...")
    
    # Test /auth/me
    print("\nTesting /auth/me...")
    me = requests.get(f"{BASE}/auth/me", headers={"Authorization": f"Bearer {token}"})
    print(f"Status: {me.status_code}")
    print(f"Response: {me.text}")
