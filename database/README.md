# Database

دیتابیس production این معماری PostgreSQL 16 است و توسط سرویس `database` در `docker-compose.yml` اجرا می‌شود.

داده‌ها در volume با نام `postgres_data` نگه‌داری می‌شوند و با حذف container از بین نمی‌روند.

برای مشاهده:

```bash
docker compose exec database psql -U uemp -d uemp
```

برای backup:

```bash
docker compose exec database pg_dump -U uemp -d uemp > uemp-backup.sql
```

برای restore، ابتدا دیتابیس خالی را آماده و سپس فایل SQL را وارد کنید.
