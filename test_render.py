import requests

url = "https://neuroshield-ai-fraud-detection-app.onrender.com/auth/signup"
data = {"name":"Test User","email":"test1@example.com","phone":"1234567890","password":"password123"}
try:
    res = requests.post(url, json=data)
    print("Status:", res.status_code)
    print("Response:", res.text)
except Exception as e:
    print("Error:", e)
