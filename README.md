# NeuroShield: AI-Powered Fraud Detection Banking App

NeuroShield is a production-grade fintech application designed to detect and prevent fraudulent transactions in real-time using machine learning.

## 🚀 Features

- **Real-Time Fraud Detection**: Uses Isolation Forest (Scikit-learn) to score every transaction against user behavior profiles.
- **Fintech Dark Mode UI**: Premium mobile interface built with React Native and Expo.
- **Dynamic Model Management**: Admin APIs for model versioning and one-click rollbacks.
- **Background Automation**: Automated bank synchronization and model retraining via APScheduler.
- **Secure Auth**: JWT-based authentication with token blacklisting.
- **Real-Time Alerts**: WebSocket-based notifications for suspicious activities.
- **Integrated Payments**: Razorpay integration with secure webhook verification.

## 🛠️ Tech Stack

- **Frontend**: React Native (Expo), React Navigation, Axios.
- **Backend**: FastAPI (Python), SQLAlchemy, PostgreSQL, Redis.
- **AI/ML**: Scikit-learn, NumPy, Pandas.
- **DevOps**: Docker, Docker Compose.

## 📦 Project Structure

```text
├── backend/
│   ├── api/             # API Endpoints (Auth, Transactions, Payments, Analytics)
│   ├── core/            # Database config, Security, Settings
│   ├── ml/              # Fraud detection model and retraining logic
│   ├── models/          # SQLAlchemy Database Models
│   ├── tests/           # Pytest suite and performance benchmarks
│   └── main.py          # Application entry point
├── frontend/
│   ├── src/
│   │   ├── api/         # Axios client
│   │   ├── context/     # Auth State Management
│   │   ├── hooks/       # Custom hooks (WebSockets)
│   │   ├── navigation/  # Navigation stacks
│   │   └── screens/     # App screens (Dashboard, Analytics, Alerts)
└── docker-compose.yml   # Full stack orchestration
```

## 🏁 Getting Started

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npx expo start
```

### 3. Docker Deployment
```bash
docker-compose up --build
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
