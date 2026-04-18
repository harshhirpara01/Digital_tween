# Digital Tween

**Digital Tween** (Digi Teen) is a behavior-tracking web app with a FastAPI backend, a Jinja2 + HTML/CSS frontend, and a playful **Digi Buddy** companion that comments on your recent mood, sleep, and productivity patterns.

## Features

- **Auth:** Register with email → OTP verification (SMTP) → login → JWT (`Bearer` token).
- **SQLite + SQLAlchemy:** No separate database server required locally; data lives in `digital_tween.db` (created on first run).
- **Behavior logs:** Add, list, and delete daily entries (mood, sleep, study/work hours, screen time, productivity score, etc.).
- **ML (optional):** Train a small model on your logs after you have enough entries; use the predict API when models exist.
- **Account:** Update profile (name, profession) and **change password** from `/account`.
- **Web UI:** Login, register, home (Digi Buddy), logs, and account pages under `/static` and `templates/`.

## Requirements

- Python **3.10+** recommended  
- Dependencies: see `requirements.txt` (FastAPI, Uvicorn, SQLAlchemy, passlib/bcrypt, Jinja2, pandas, scikit-learn, …)

## Quick start

### 1. Clone and virtual environment

```bash
cd Digital_tween
python -m venv venv
```

**Windows**

```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
```

**macOS / Linux**

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment variables

Copy or create a `.env` file in the project root (do **not** commit real secrets). Example:

```env
JWT_SECRET=your-long-random-secret
ALGORITHM=HS256

# Optional: override SQLite path (default: ./digital_tween.db)
# DATABASE_URL=sqlite:////absolute/path/to/digital_tween.db

# Gmail SMTP for OTP (use an App Password, not your normal password)
MAIL_USER=you@gmail.com
EMAIL_PASS=your_app_password
```

- **`JWT_SECRET`** and **`ALGORITHM`** are used for access tokens.
- **`MAIL_USER`** / **`EMAIL_PASS`** are used to send registration OTPs over Gmail SMTP (`smtp.gmail.com:465`).

### 3. Run the server

```bash
uvicorn main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) — you will be redirected to `/login`.

### 4. Useful URLs

| URL | Description |
|-----|-------------|
| `/login`, `/register` | Auth |
| `/home` | Dashboard + Digi Buddy (needs login) |
| `/logs` | Add / view behavior logs |
| `/account` | Profile + change password |
| `/docs` | OpenAPI docs (when `DEBUG=true`) |

## API overview (JSON)

All JSON APIs return a shape like `{ "status": "success"|"error", "message": "...", "data": ... }` unless noted.

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/User_Register` | No | Start registration; sends OTP email |
| `POST` | `/verify_register_otp` | No | Verify OTP |
| `POST` | `/login` | No | Returns `{ "token": "..." }` in `data` |
| `GET` | `/account/me` | Bearer | Current user profile |
| `PATCH` | `/account/profile` | Bearer | Update `full_name`, `profession` |
| `POST` | `/account/change-password` | Bearer | `current_password`, `new_password`, `confirm_password` |
| `POST` | `/Behavior-log-add` | Bearer | Add log |
| `GET` | `/Behavior-log-get` | Bearer | List logs |
| `POST` | `/Behavior-log-delete` | Bearer | Delete by `log_id` |
| `POST` | `/ml/train/{user_id}` | Bearer | Train model (min logs + varied activities) |
| `POST` | `/ml/predict/activity` | Bearer | Predict (requires trained model) |

Send authenticated requests with header:

```http
Authorization: Bearer <your_jwt>
```

## Training rules

Training returns clear **400** messages if:

- You have **no logs** — add entries on the Logs page first.
- You have **fewer than 5** logs.
- You have **only one distinct `activity` value** — add at least two different activities so the classifier can learn.

## Frontend notes

- Static files: `/static/css/app.css`, `/static/js/*.js`.
- Token is stored in **`localStorage`** as `dt_token` for the web UI.

## Troubleshooting

### `pip install -r requirements.txt` fails with weird characters

The file must be **UTF-8**, not UTF-16. In VS Code / Cursor: status bar → encoding → **Save with Encoding → UTF-8**. Or rewrite the file as UTF-8 and reinstall.

### `ModuleNotFoundError` after install

Activate the **same** virtual environment you used for `pip install`, then run `uvicorn` from the project root.

### OTP email not sending

Check `MAIL_USER` / `EMAIL_PASS`, Gmail “App passwords”, and that `.env` is loaded (app calls `load_dotenv()` in `main.py`).

## Deployment hints

- **SQLite** is simple for demos; many free hosts use an **ephemeral filesystem**, so the DB file may reset on redeploy. For production, point **`DATABASE_URL`** at a managed database (same SQLAlchemy code, different URL).
- Set **`DEBUG=false`** in production if you want to hide `/docs` and OpenAPI.

## License

Use and modify for your course / project as needed.
