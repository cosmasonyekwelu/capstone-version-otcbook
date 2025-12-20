# OTCBook – OTC Crypto Desk Bookkeeping API (Django)


This project is provided **solely for educational and demonstration purposes**.

It is **not a production trading system**, **not financial software**, and **not a substitute for licensed financial tools**.
The following applies:

- **No real trading, financial calculations, or investment advice** should be executed with this system.
- **No warranties or guarantees** are provided regarding accuracy, compliance, or security.
- **DO NOT** use this software to collect real user data, real identity documents, or real financial information.
- **Not intended for production**, real clients, or regulated environments.

By using this repository, you acknowledge that the author(s) are **not responsible** for any misuse or consequences arising from real-world usage

This repository contains the backend system for **OTCBook**, a bookkeeping and financial advisory platform for Nigerian OTC crypto trading desks. The project provides tools for desk owners and traders to record trades, calculate P&L, manage teams, earn points, generate invoices, and receive advisory reports.
The backend is built with **Django** and **Django REST Framework**. No frontend is required for the core capstone submission.

---

## 1. Project Overview

OTCBook is designed for:

- Individual OTC traders
- Multi-user OTC desks
- Compliance-focused crypto operations

The system allows users to:

- Log NGN-based crypto trades
- Track profits and losses
- Generate invoices
- Earn OP points
- Unlock badges
- View leaderboards
- Receive automated financial advisory
- Export compliance reports

This API powers all these features.

Reference: Capstone specification.

---

## 2. Core Features

### 2.1 Authentication & User Management

- User registration (desk owner, trader, manager, analyst, viewer, auditor)
- Login using JWT
- Company (Desk) creation for desk owners
- Team member onboarding
- KYC upload for desks
- User profile endpoint

Endpoints (from spec):

- `POST /auth/register/`
- `POST /auth/login/`
- `POST /auth/kyc/`
- `GET /users/me/`
- `POST /desk/add-trader/`

---

### 2.2 Trade Logging

Traders can record all buy/sell trades:

- Asset
- Side (buy/sell)
- Rate
- Amount NGN
- Amount crypto
- Auto P&L calculation
- List and filter trades
- P&L summaries
- Export CSV

Endpoints:

- `POST /trades/create/`
- `GET /trades/list/`
- `GET /trades/pnl/`
- `GET /trades/<id>/`

---

### 2.3 Gamification System

OTCBook awards:

- OP points
- Badges
- Levels
- Weekly and monthly leaderboards

Points examples (from spec):

- +10 for logging a trade
- +30 for inviting teammate
- Bonus for fast trade logging

Endpoints:

- `/gamification/op/`
- `/gamification/badges/`
- `/gamification/leaderboard/`

---

### 2.4 Invoicing System

- Generate invoices from trades
- Auto-fill invoice fields
- Mark invoices as paid/unpaid
- Download invoices as PDF
- Email sending (optional)

Endpoints:

- `POST /invoice/create/<trade_id>/`
- `GET /invoice/<id>/download/`
- `GET /invoice/list/`

---

### 2.5 AI Financial Advisory

Generates:

- Quick insights
- Risk warnings
- Trend performance
- OP-based trust scores
- PDF risk reports

Endpoints:

- `/advisory/chat/`
- `/advisory/quick-insights/`
- `/advisory/risk-report/`

---

### 2.6 Admin & Compliance

Admin tools allow:

- View all users
- View all trades
- Ban/unban users
- Approve/reject KYC
- Monitor suspicious trades
- Generate compliance reports

Endpoints:

- `/admin/overview/`
- `/admin/users/`
- `/admin/trades/`

---

## 3. System Architecture

### Tech Stack

| Category          | Technology                |
| ----------------- | ------------------------- |
| Backend Framework | Django, DRF               |
| Database          | PostgreSQL                |
| Authentication    | JWT (SimpleJWT)           |
| File Storage      | Local or S3               |
| Background Jobs   | Celery + Redis (optional) |
| PDF Engine        | ReportLab or WeasyPrint   |
| AI                | OpenAI API or rule-based  |
| Documentation     | Swagger / Redoc           |
|                   |                           |

---

## 4. Installation & Setup

### 4.1 Clone Repository

```bash
git clone https://github.com/cosmasonyekwelu/capstone-version-otcbook.git
cd capstone-version-otcbook
```

### 4.2 Create Virtual Environment

```bash
py -m venv venv
venv\Scripts\activate
```

### 4.3 Install Dependencies

```bash
pip install -r requirements.txt
```

### 4.4 Run Migrations

```bash
py manage.py makemigrations
py manage.py migrate
```

### 4.5 Create Superuser

```bash
py manage.py createsuperuser
```

### 4.6 Start Server

```bash
py manage.py runserver
```

Your API will be available at:

```
http://localhost:4001/
```

---

## 5. Authentication Flow

### 5.1 Desk Owner Registration

Request:

```json
{
  "name": "John Doe",
  "email": "desk@example.com",
  "password": "test1234",
  "workspace": "Prime Desk"
}
```

### 5.2 Login

Request:

```json
{
  "email": "desk@example.com",
  "password": "test1234"
}
```

Response includes:

- access token
- refresh token
- user profile

---

## 6. API Summary

### Auth

| Method | Endpoint          | Description                 |
| ------ | ----------------- | --------------------------- |
| POST   | /auth/signup/     | Register desk owner         |
| POST   | /auth/login/      | Login with JWT              |
| POST   | /auth/kyc/        | Desk KYC upload             |
| GET    | /users/me/        | Get logged-in profile       |
| POST   | /desk/add-trader/ | Desk owner adds team member |

### Trades

| POST /trades/create/ | Create new trade |
| GET /trades/list/ | List trades |
| GET /trades/pnl/ | Profit/Loss summary |
| GET /trades/<id>/ | Single trade details |

### Gamification

| GET /gamification/op/ |
| GET /gamification/badges/ |
| GET /gamification/leaderboard/ |

### Invoices

| POST /invoice/create/<trade_id>/ |
| GET /invoice/<id>/download/ |
| GET /invoice/list/ |

### Advisory

| POST /advisory/chat/ |
| GET /advisory/quick-insights/ |
| POST /advisory/risk-report/ |

### Admin

| GET /admin/overview/ |
| GET /admin/users/ |
| GET /admin/trades/ |

---
