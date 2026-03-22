# 🚀 AI Interview Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![Firebase](https://img.shields.io/badge/firebase-ffca28?style=for-the-badge&logo=firebase&logoColor=black)](https://firebase.google.com)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)

## 📋 Overview
Complete AI-powered platform for technical interview preparation in AI/ML/DL/DS domains.

## 🏗️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: Firebase (Firestore, Auth, Storage)
- **AI/ML**: OpenAI, Gemini, Hugging Face, Custom Models
- **Task Queue**: Celery + Redis
- **Authentication**: JWT + Firebase Auth

### Frontend
- **Framework**: Next.js 14 (React 18)
- **Styling**: Tailwind CSS + CSS Modules
- **State Management**: Redux Toolkit
- **Charts**: Recharts, D3.js
- **HTTP Client**: Axios + React Query

### Infrastructure
- **Container**: Docker + Docker Compose
- **Reverse Proxy**: Nginx
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Firebase Account

### Installation

1. **Clone Repository**
```bash
git clone https://github.com/yourusername/ai-interview-platform.git
cd ai-interview-platform



cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements/dev.txt
cp .env.example .env
# Edit .env with your configuration
python scripts/seed_data.py
uvicorn main:app --reload


