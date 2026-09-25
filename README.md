# Study Hood

A lead-capture platform for a college admissions consultancy: students fill one application form specifying their preferred college(s), and the admin (you) reviews and processes submissions from a password-protected dashboard.

## What it does

- **Public application form** (`/apply`) — students submit name, contact details, city, course of interest, preferred college(s), 12th-grade percentage, and a free-text note. Server-side validation checks email format, phone number, and requires explicit consent before storing any data.
- **Admin dashboard** (`/admin`) — password-protected (HTTP Basic Auth). Lists every submission, newest first.
- **CSV export** (`/admin/export`) — download all submissions as a spreadsheet for offline processing or forwarding to college contacts.
- **Delete endpoint** (`DELETE /admin/applications/{id}`) — remove a record (e.g. duplicate or spam submission).

## Why it's built this way

This is a v1 lead-capture tool, not a full application-processing pipeline — no payments, no document uploads, no per-college routing logic. That was a deliberate scope decision: get real submissions flowing and prove the concept before building out anything more complex. Everything here is real, working code you can deploy today.

## Run it locally

```bash
pip install -r requirements.txt
cp .env.example .env
# edit .env and set a real ADMIN_PASSWORD before doing anything with real student data
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000` for the public form, `http://127.0.0.1:8000/admin` for the dashboard (login with whatever you set in `.env`).

## Before you use this with real students

- **Change `ADMIN_PASSWORD`** in `.env` — the default in `.env.example` is not secure.
- **This needs to run on HTTPS in production.** HTTP Basic Auth sends credentials in a way that's only safe over an encrypted connection — Render and Railway (see below) both provide free HTTPS automatically.
- **You are collecting personal data from real people.** Have a clear, honest privacy statement on the form about what you do with it and who sees it, matching what the form's consent checkbox actually says.

## Deploying so students can actually use it

This needs a real server — SQLite is fine to start, but GitHub Pages (static-only) cannot run this. Free options that work:

- **Render** (render.com) — connect your GitHub repo, set the start command to `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, add your `.env` variables in their dashboard.
- **Railway** (railway.app) — similar flow, auto-detects Python and FastAPI.

Either gives you a public URL like `study-hood.onrender.com` within a few minutes of connecting the repo.

## Switching to MySQL

By default this runs on local SQLite. To use MySQL instead, set in `.env`:
```
DATABASE_URL=mysql+pymysql://user:password@host:3306/study_hood
```
No code changes needed.

## Project structure

```
app/
  main.py       Routes: home, apply form, admin dashboard, CSV export, delete
  models.py     SQLAlchemy Application model
  database.py   DB engine/session setup
  auth.py       HTTP Basic Auth for admin routes
  templates/    Jinja2 HTML templates
  static/       CSS
.env.example    Copy to .env and fill in real values
```
