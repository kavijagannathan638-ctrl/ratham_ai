# RATHAM AI — Predictive Blood Continuity Intelligence Network

> **Predictive AI platform transforming blood supply management from reactive firefighting into real-time operational continuity.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0-FF6F00?logo=xgboost)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🌟 Key Features

* 🔮 **Predictive Transfusion Need Forecasting**: Evaluates clinical trends (hemoglobin levels, drop velocity, transfusion intervals, fatigue scores) to predict patient transfusion need 7 days in advance.
* 📱 **Donor Reachability AI**: Calculates donor response probability based on historical latency, distance, and weekday availability to prevent calling unavailable donors.
* 🛡 **Donor Burnout Protection**: Detects contact fatigue and enforces automated cooldown periods to protect the donor base from over-solicitation.
* ⚡ **Emergency Swarm Orchestration**: Multi-candidate fallback engine that dispatches Wave 1 primary contacts and Wave 2 backup swarms automatically upon decline.
* 📊 **SHAP-Style AI Explainability**: Provides human-interpretable clinical and operational factor breakdowns for every decision signal.
* 🔑 **Role-Based Access Control (RBAC)**: Custom tailored workflows and dashboards for **City Coordinators**, **Super Admins**, and **Hospital Operators**.

---

## 🧠 Machine Learning Models

RATHAM AI serves three custom-trained **XGBoost Classifiers**:

1. **Transfusion Need Forecast Model** (`need_model`): Predicts patient 7-day transfusion probability & urgency (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
2. **Donor Reachability Model** (`reachability_model`): Predicts probability of donor availability and response latency.
3. **Donor Burnout Risk Model** (`burnout_model`): Predicts contact fatigue and computes optimal donor cooldown days (`HEALTHY`, `WATCH`, `HIGH_RISK`).

---

## 🏗 System Architecture

```
React (Vite 5) ──► REST API (FastAPI) ──► Decision & Swarm Engine
                          │                          │
                          ▼                          ▼
                   SQLite Persistence        3 XGBoost ML Models
```

---

## 🚀 Quick Start Guide

### Prerequisites
* **Python**: `3.10+`
* **Node.js**: `18+` & `npm`

---

### 1. Backend Setup & Model Initialization

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Generate datasets & train ML models
python ../ml/generate_datasets.py
python ../ml/train_models.py

# Initialize database
python ../scripts/seed_demo.py

# Run FastAPI development server
uvicorn app.main:app --reload --port 8000
```
Backend API will run at `http://localhost:8000` (Interactive API docs at `http://localhost:8000/docs`).

---

### 2. Frontend Setup

```bash
# In a new terminal window
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```
Frontend Web App will run at `http://localhost:5173`.

---

## 🔑 Access Credentials

| Role | Email Address | Password | Focus Area |
| :--- | :--- | :--- | :--- |
| **City Coordinator** | `coordinator@ratham.ai` | `coord123` | Operational Dashboard, Emergency Dispatch & Donor Matching |
| **Super Admin** | `admin@ratham.ai` | `admin123` | ML Model Governance, Audit Logs & System Diagnostics |

---

## 🧪 Running Automated Tests

```bash
# Run pytest test suite across API, ML inference, & Swarm Engine
pytest backend/tests
```

---

## 📁 Repository Structure

```
RATHAM_AI_complete/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI REST Routers (auth, patients, donors, emergencies, analytics, admin)
│   │   ├── core/         # Config, Database, Logging, Security, & Dependencies
│   │   ├── matching/     # Donor Ranking Decision Engine
│   │   ├── emergency/    # Swarm Fallback Orchestration Engine
│   │   ├── ml/           # Model Registry & Inference Service
│   │   └── models/       # SQLAlchemy ORM Database Schemas
│   └── tests/            # Automated Pytest Suite
├── frontend/
│   ├── src/              # React 18 Components & CSS Tokens
│   └── package.json
├── ml/
│   ├── training/         # XGBoost Model Training Scripts
│   └── evaluation/       # ROC-AUC & F1 Evaluation Tools
├── models/               # Serialized ML Model Artifacts (.pkl)
├── scripts/              # Database Seeding & Setup Scripts
└── README.md
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
