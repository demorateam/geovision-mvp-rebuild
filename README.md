# UEMP — معماری تفکیک‌شده و Docker

این نسخه بر اساس پروژه MVP موجود بازطراحی شده است تا سه لایه اصلی مستقل باشند:

- `frontend/` منطقی: Next.js + React
- `backend/` اجرایی: FastAPI + SQLAlchemy
- `database/` اجرایی: PostgreSQL
- `gateway`: Nginx برای ارائه یک origin واحد و مسیریابی `/api` و `/uploads`

رابط کاربری اصلی حفظ شده و APIهای قبلی با همان مسیرها (`/api/...`) در FastAPI پیاده‌سازی شده‌اند.

## معماری

```text
Browser
   |
   v
Nginx :80
   |--------------------> frontend :3000
   |
   | /api/*, /uploads/*
   v
FastAPI :8000
   |
   v
PostgreSQL :5432

uploads --> Docker named volume
```

در production بهتر است TLS در reverse proxy یا load balancer بیرونی terminate شود. در این حالت `COOKIE_SECURE=true` باقی بماند.

## اجرای Docker

1. فایل env را بسازید:

```bash
cp .env.example .env
```

2. حداقل این مقادیر را تغییر دهید:

```env
POSTGRES_PASSWORD=یک-رمز-قوی
JWT_SECRET=یک-رشته-تصادفی-حداقل-۳۲-کاراکتری
```

3. سرویس‌ها را build و اجرا کنید:

```bash
docker compose up -d --build
```

4. وضعیت:

```bash
docker compose ps
docker compose logs -f backend
```

5. سلامت backend:

```bash
curl http://localhost/api/health
```

در production دامنه را به سرور وصل کنید و reverse proxy/TLS را جلوی gateway قرار دهید.

## کاربران نمونه

برای ساخت کاربران نمونه:

```bash
docker compose exec backend python -m app.init_db
```

برای ساخت دیتای نمایشی ۳۰ رخداد:

```bash
docker compose exec backend python -m app.seed_demo
```

کاربران:

| نقش | موبایل |
|---|---|
| مدیر | `09120000001` |
| شهروند | `09120000002` |
| شهروند | `09120000003` |
| اپراتور شهرداری | `09120000004` |
| اپراتور آتش‌نشانی | `09120000005` |

با `OTP_MODE=demo` کد OTP در پاسخ API برگردانده می‌شود.

## مهاجرت دیتابیس قبلی

نسخه قبلی از Prisma + SQLite استفاده می‌کرد. برای مهاجرت اطلاعات موجود، فایل `migration/legacy-dev.db` را به یک مسیر موقت داخل backend منتقل کنید و سپس:

```bash
docker cp ./dev.db $(docker compose ps -q backend):/app/legacy-dev.db
docker compose exec backend python -m app.migrate_sqlite /app/legacy-dev.db
```

اسکریپت migration مدل‌های `User`، `Incident`، `IncidentAgency` و `IncidentStatusHistory` را منتقل می‌کند.

نکته: قبل از migration از دیتابیس قبلی backup بگیرید.

## توسعه Frontend خارج از Docker

پیش‌نیاز: Node.js 20.

```bash
cd frontend
npm ci
cp ../.env.example .env.local
```

برای اتصال مستقیم به backend:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

و در backend برای محیط محلی:

```env
COOKIE_SECURE=false
CORS_ORIGINS=http://localhost:3000
```

سپس:

```bash
npm run dev
```

## توسعه Backend خارج از Docker

Python 3.12:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## نکات مهم معماری

- Frontend دیگر هیچ وابستگی به Prisma یا دیتابیس ندارد.
- FastAPI تنها لایه‌ای است که با PostgreSQL صحبت می‌کند.
- کلیدهای OpenAI و Neshan فقط در backend قرار می‌گیرند.
- JWT در cookie `urban_session` نگه‌داری می‌شود.
- Nginx یک origin واحد ایجاد می‌کند؛ بنابراین frontend می‌تواند همچنان از `/api/...` استفاده کند.
- فایل‌های آپلودشده در volume مستقل Docker نگه‌داری می‌شوند.
- PostgreSQL در volume مستقل Docker نگه‌داری می‌شود.
- `node_modules` و `.next` داخل ZIP قرار نگرفته‌اند.
- محتوای `public` نیز همانند فایل ارسالی شما عمداً کامل نیست.

## بررسی کد

```bash
cd frontend
npm run typecheck
npm run lint
npm run build
```

Backend:

```bash
python -m compileall -q backend
```
