# 🏋️ MyCoach

**Client management, payments & hour tracking for coaches.**

A lightweight self-hosted web app to manage your coaching business — clients, sessions, invoices, and payments in one place.

---

## ✨ Features

- 👤 **Client management** — profiles, contact info, notes
- ⏱️ **Session tracking** — log coaching hours per client
- 💳 **Payment tracking** — record payments, outstanding balance per client
- 📊 **Dashboard** — overview of sessions, revenue, unpaid invoices
- 🔐 **Auth** — secure login (JWT)
- 🐳 **Docker ready** — one command to start

---

## 🚀 Quick Start

```bash
git clone https://github.com/gaelgael5/mycoach.git
cd mycoach
cp .env.example .env
# Edit .env and set a strong SECRET_KEY
docker compose up -d
```

Open http://localhost:8000 🎉

---

## 🏗️ Architecture

```
mycoach/
├── src/
│   ├── main.py              # FastAPI entry point
│   ├── core/
│   │   ├── auth.py          # JWT authentication
│   │   ├── clients.py       # Client management
│   │   ├── sessions.py      # Session / hour tracking
│   │   └── payments.py      # Payment tracking
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   └── ui/
│       ├── index.html       # Main dashboard
│       └── login.html       # Login page
├── data/                    # SQLite database (gitignored)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## 🛣️ Roadmap

### ✅ v0.1 — Foundation
- [ ] Client CRUD (create, read, update, delete)
- [ ] Session logging (date, duration, notes)
- [ ] Payment recording (amount, date, method)
- [ ] Dashboard with totals

### 🔜 v0.2
- [ ] Invoice generation (PDF)
- [ ] Email reminders for unpaid balances
- [ ] Client portal (self-service view)

### 🔜 v1.0
- [ ] Multi-coach support
- [ ] Calendar integration
- [ ] Stripe / payment gateway

---

## 📄 License

MIT
# Build trigger Mon Mar  2 02:14:48 PM CET 2026
