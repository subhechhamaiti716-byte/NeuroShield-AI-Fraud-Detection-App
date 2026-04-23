import requests

BASE = "https://neuroshield-ai-fraud-detection-app.onrender.com"

# The original account was created with the OLD passlib hash, so we need to 
# delete it and re-create. But we can't delete via API. 
# Instead, let's just test login with original email first to confirm the error,
# then signup with a completely new account.

# Test 1: Try login with original account (will fail - old hash format)
print("Test 1: Login with original account...")
res = requests.post(f"{BASE}/auth/login", data={
    "username": "subhechhamaiti716@gmail.com",
    "password": "P$aLm23_My-L0RD"
})
print(f"  Status: {res.status_code} - {res.text[:200]}")

# Test 2: Signup with completely new account
print("\nTest 2: Signup fresh account...")
res = requests.post(f"{BASE}/auth/signup", json={
    "name": "Subhechha2",
    "email": "subhechha.new@gmail.com",
    "phone": "9876543210",
    "password": "P$aLm23_My-L0RD"
})
print(f"  Status: {res.status_code} - {res.text[:200]}")

# Test 3: Login with fresh account
print("\nTest 3: Login with fresh account...")
res = requests.post(f"{BASE}/auth/login", data={
    "username": "subhechha.new@gmail.com",
    "password": "P$aLm23_My-L0RD"
})
print(f"  Status: {res.status_code} - {res.text[:200]}")

if res.status_code == 200:
    token = res.json().get("access_token")
    print(f"\nSUCCESS! Login works!")
    me = requests.get(f"{BASE}/auth/me", headers={"Authorization": f"Bearer {token}"})
    print(f"  /auth/me: {me.status_code} - {me.text[:200]}")
