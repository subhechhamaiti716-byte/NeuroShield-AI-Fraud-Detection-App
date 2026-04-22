# NeuroShield: AI-Powered Fraud Detection Banking App

NeuroShield is a production-grade fintech application designed to detect and prevent fraudulent transactions in real-time using machine learning.

## 🚀 Features

- **Real-Time Fraud Detection**: Uses Isolation Forest (Scikit-learn) to score every transaction against user behavior profiles.
- **Fintech Dark Mode UI**: Premium mobile interface built with React Native and Expo.
- **Dynamic Model Management**: Admin APIs for model versioning and one-click rollbacks.
- **Background Automation**: Automated bank synchronization and model retraining via APScheduler.
- **Secure Auth**: JWT-based authentication with token blacklisting and role-based access.
- **Real-Time Alerts**: WebSocket-based notifications for suspicious activities.
- **Integrated Payments**: Razorpay integration with secure webhook verification.

## 🛠️ Tech Stack

- **Frontend**: React Native (Expo), React Navigation, Axios.
- **Backend**: FastAPI (Python), SQLAlchemy, SQLite/PostgreSQL, WebSockets.
- **AI/ML**: Scikit-learn, NumPy, Pandas.

## 🏗️ Architecture Explanation

NeuroShield follows a modern, decoupled client-server architecture:
1. **Client Layer (React Native)**: A mobile-first UI with secure local storage for JWT tokens, connecting to the backend via REST APIs and WebSockets (for real-time alerts).
2. **API Gateway & Routing (FastAPI)**: Handles requests securely with rate limiting and global exception handling.
3. **Machine Learning Engine**: Before a transaction is saved to the DB, it passes through the `fraud_model` which evaluates risk using Scikit-Learn based on user behavior profiling (e.g., spending history, transaction frequency).
4. **Asynchronous Task Scheduler**: Runs scheduled jobs (APScheduler) in the background to sync mock bank data, retrain the ML model daily, and cleanup expired JWT tokens.
5. **Database Layer (SQLAlchemy)**: Manages users, transactions, and fraud logs with relational integrity.

## 🏁 Getting Started

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```
The backend will be available at `http://127.0.0.1:8000`. You can view the interactive API docs at `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npx expo start
```

## 📸 Screenshots
*(Add screenshots of the app here)*
- **Dashboard**: `![Dashboard](link-to-image)`
- **Fraud Alert**: `![Alert](link-to-image)`

## 🌐 Live Demo
*(Replace with your actual deployed link)*
- **Backend API**: [https://neuroshield-api.onrender.com](https://neuroshield-api.onrender.com)
- **Frontend App**: [https://neuroshield.vercel.app](https://neuroshield.vercel.app)

## 🚀 Deployment Guide

### Backend (Render / Railway)
1. Ensure your `.env` is configured correctly (refer to `backend/.env.example`).
2. Push your code to GitHub.
3. On Render/Railway, create a new Web Service.
4. Set the Build Command: `pip install -r requirements.txt`
5. Set the Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add all environment variables.

### Frontend (Vercel)
1. Push your frontend code to GitHub.
2. Go to Vercel, import your frontend repository.
3. Select `Create React App` or `Vite` preset (if migrated to web), or deploy via Expo EAS for mobile.
4. Add your `EXPO_PUBLIC_API_URL` environment variable.

## 📖 API Usage Examples

Here are some examples of interacting with the API via cURL:

**1. Health Check**
```bash
curl -X GET "http://127.0.0.1:8000/health"
# Response: {"status":"ok"}
```

**2. Register User**
```bash
curl -X POST "http://127.0.0.1:8000/auth/signup" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "securepassword", "name": "Test User", "phone": "1234567890"}'
```

**3. Login & Get Token**
```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=user@example.com&password=securepassword"
# Response includes: {"access_token": "...", "refresh_token": "...", "token_type": "bearer"}
```

**4. Add Transaction (Protected)**
```bash
curl -X POST "http://127.0.0.1:8000/transactions/add" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"amount": 500, "category": "retail", "merchant": "Apple Store", "location": "New York", "source": "MANUAL"}'
```

## 🧪 Testing
Run the test suite and performance benchmarks:
```bash
cd backend
pytest tests/
python tests/metrics.py
```

## 🛡️ License
MIT
