# Job Portal — Django + PostgreSQL Backend

Complete Python/Django rewrite of the Node.js/MongoDB backend.

## Stack
- **Framework**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL (via psycopg2)
- **Auth**: JWT (djangorestframework-simplejwt)
- **File Storage**: Local disk (dev) / Cloudinary (prod)
- **AI**: OpenAI GPT-3.5-turbo (optional)

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

Key variables:
```
DB_NAME=job_portal
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your-50-char-secret-key
```

### 3. Create PostgreSQL database
```sql
CREATE DATABASE job_portal;
```

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Create admin user
```bash
python scripts/create_admin.py
```

### 6. Seed coding problems
```bash
python scripts/seed_coding_problems.py
```

### 7. Start the server
```bash
python manage.py runserver 5000
```

API is now running at `http://localhost:5000`

---

## API Endpoints (matches original Node.js API)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register user/employer |
| POST | `/api/auth/login` | Login |
| GET | `/api/auth/me` | Get current user |
| GET | `/api/jobs/` | List jobs (search, filter, paginate) |
| POST | `/api/jobs/create` | Create job (employer) |
| POST | `/api/applications/apply` | Apply for job |
| GET | `/api/notifications/` | Get notifications |
| GET | `/api/copilot/readiness` | AI readiness score |
| POST | `/api/copilot/chat` | AI career chat |
| GET | `/api/coding/daily` | Daily coding problems |
| POST | `/api/coding/problems/:id/submit` | Submit solution |
| POST | `/api/mock-interview/start` | Start mock interview |
| GET | `/api/reputation` | Reputation score |
| GET | `/api/recruiter/jobs/:id/funnel` | Hiring funnel |
| GET | `/api/marketplace/micro-internships` | Micro-internships |
| ... | *(all 80+ endpoints from Node.js backend)* | |

---

## Apps Structure

```
django_backend/
├── accounts/          # Users, Employers, Auth, Admin
├── jobs/              # Jobs, Bookmarks
├── applications/      # Job Applications
├── posts/             # Social Feed, Comments
├── notifications/     # Notification System
├── features/          # 14 Features (Copilot, Coding, Interview, etc.)
├── recruiter/         # Hiring Funnel, Ranking, Talent Pools
├── marketplace/       # Micro-Internships
└── django_backend/    # Settings, URLs, Utils
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Django secret key (50+ chars) |
| `DB_NAME` | Yes | PostgreSQL database name |
| `DB_USER` | Yes | PostgreSQL username |
| `DB_PASSWORD` | Yes | PostgreSQL password |
| `DB_HOST` | Yes | PostgreSQL host |
| `OPENAI_API_KEY` | No | For AI features (Copilot, Mock Interview) |
| `CLOUDINARY_*` | No | For cloud file storage in production |
| `GITHUB_TOKEN` | No | For GitHub reputation integration |

---

## Frontend Integration

Update your frontend `.env` to point to the Django backend:
```
VITE_API_URL=http://localhost:5000
```

All API response shapes match the original Node.js backend exactly.
