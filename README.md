# OTCBook – OTC Crypto Desk Bookkeeping API (Django)


This project is provided **solely for educational and demonstration purposes**.

It is **not a production trading system**, **not financial software**, and **not a substitute for licensed financial tools**.
The following applies:

- **No real trading, financial calculations, or investment advice** should be executed with this system.
- **No warranties or guarantees** are provided regarding accuracy, compliance, or security.
- **DO NOT** use this software to collect real user data, real identity documents, or real financial information.


By using this repository, you acknowledge that the author(s) are **not responsible** for any misuse or consequences arising from real-world usage

This repository contains the backend system for **OTCBook**, a bookkeeping and financial advisory platform for Nigerian OTC crypto trading desks. The project provides tools for desk owners and traders to record trades, calculate P&L, manage teams, earn points, generate invoices, and receive advisory reports.
The backend is built with **Django** and **Django REST Framework**. 

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
| Database          | PostgreSQL/sqlite3 for dev|
| Authentication    | JWT (SimpleJWT)           |
| File Storage      | Cloudinary                |
| Background Jobs   | Celery + Redis (optional) |
| PDF Engine        | ReportLab                 |
| AI                | GROQ API                  |
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
py manage.py runserver 4001
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

Using Django Admin

---

```
capstone-version-otcbook
├─ advisory
│  ├─ admin.py
│  ├─ apps.py
│  ├─ migrations
│  │  ├─ 0001_initial.py
│  │  ├─ 0002_alter_tradeinsight_options_riskreport.py
│  │  ├─ 0003_alter_riskreport_ai_summary_and_more.py
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ services.py
│  ├─ tests.py
│  ├─ urls.py
│  ├─ views.py
│  └─ __init__.py
├─ common
│  ├─ admin.py
│  ├─ apps.py
│  ├─ migrations
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ storage
│  │  ├─ cloudinary.py
│  │  └─ __init__.py
│  ├─ tests.py
│  ├─ views.py
│  └─ __init__.py
├─ full_api.json
├─ gamification
│  ├─ admin.py
│  ├─ apps.py
│  ├─ migrations
│  │  ├─ 0001_initial.py
│  │  ├─ 0002_badge_description_badge_is_active_badge_min_points_and_more.py
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ serializers.py
│  ├─ services.py
│  ├─ signals.py
│  ├─ tests.py
│  ├─ urls.py
│  ├─ views.py
│  └─ __init__.py
├─ invoices
│  ├─ admin.py
│  ├─ apps.py
│  ├─ migrations
│  │  ├─ 0001_initial.py
│  │  ├─ 0002_alter_invoice_issued_at_alter_invoice_pdf_url_and_more.py
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ serializers.py
│  ├─ services.py
│  ├─ tests.py
│  ├─ urls.py
│  ├─ views.py
│  └─ __init__.py
├─ manage.py
├─ otcbook-trades.postman_collection.json
├─ otcbook_server
│  ├─ asgi.py
│  ├─ common
│  ├─ settings.py
│  ├─ urls.py
│  ├─ wsgi.py
│  └─ __init__.py
├─ Procfile
├─ README.md
├─ requirements.txt
├─ trades
│  ├─ admin.py
│  ├─ apps.py
│  ├─ filters.py
│  ├─ migrations
│  │  ├─ 0001_initial.py
│  │  ├─ 0002_trade_trade_type_alter_asset_is_active_and_more.py
│  │  ├─ 0003_alter_asset_is_active_alter_asset_is_custom_and_more.py
│  │  ├─ 0004_alter_trade_desk_alter_asset_options_and_more.py
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ serializers.py
│  ├─ tests.py
│  ├─ urls.py
│  ├─ views.py
│  └─ __init__.py
├─ updatedreq.txt
└─ users
   ├─ admin.py
   ├─ apps.py
   ├─ managers.py
   ├─ migrations
   │  ├─ 0001_initial.py
   │  ├─ 0002_remove_desk_id_card_desk_id_card_url.py
   │  ├─ 0003_desk_address.py
   │  └─ __init__.py
   ├─ models.py
   ├─ serializers.py
   ├─ tests.py
   ├─ urls.py
   ├─ views.py
   └─ __init__.py

```