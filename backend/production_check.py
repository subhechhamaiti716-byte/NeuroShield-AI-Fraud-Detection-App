import os
import sys

def check_env_vars():
    required_vars = [
        "SECRET_KEY",
        "DATABASE_URL",
        "RAZORPAY_KEY_ID",
        "RAZORPAY_KEY_SECRET",
        "PLAID_CLIENT_ID",
        "PLAID_SECRET"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var) or "your_" in os.getenv(var) or "replace-" in os.getenv(var):
            missing.append(var)
            
    print("-" * 50)
    print("NeuroShield Production Readiness Check")
    print("-" * 50)
    
    if not missing:
        print("✅ SUCCESS: All production environment variables are set!")
    else:
        print("⚠️  WARNING: The following variables are missing or use default placeholders:")
        for var in missing:
            print(f"   - {var}")
        print("\nTo fix this:")
        print("1. Go to your Render Dashboard (backend service).")
        print("2. Go to 'Environment' settings.")
        print("3. Add the keys listed above.")
        
    print("-" * 50)

if __name__ == "__main__":
    check_env_vars()
