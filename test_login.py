import requests

BASE = "https://neuroshield-ai-fraud-detection-app.onrender.com"

# Signup with YOUR real credentials
print("Signing up with your real account...")
res = requests.post(f"{BASE}/auth/signup", json={
    "name": "Subhechha",
    "email": "subhechhamaiti716@gmail.com",
    "phone": "8167002580",
    "password": "P$aLm23_My-L0RD"
})
print(f"  Signup: {res.status_code}: {res.text[:300]}")

if res.status_code == 400 and "already registered" in res.text:
    print("\n  Email already exists with old broken hash.")
    print("  You need to sign up with a slightly different email,")
    print("  OR I can clear the DB. Trying login anyway...")

# Try login
print("\nLogging in...")
res = requests.post(f"{BASE}/auth/login", data={
    "username": "subhechhamaiti716@gmail.com",
    "password": "P$aLm23_My-L0RD"
})
print(f"  Login: {res.status_code}: {res.text[:300]}")

if res.status_code == 200:
    print("\n  SUCCESS!")
