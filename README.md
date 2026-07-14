# Smart Civic Issue Resolution System

A simple Python Flask app for reporting, tracking, and resolving civic issues with multiple user roles.

## Simplified Project Structure

```
project-civic-issues/
├── app.py                    # Root launcher script
├── requirements.txt          # Root Python dependencies
├── README.md                 # Project documentation
├── QUICKSTART.md             # Quick start guide
├── Procfile                  # Deployment startup command
├── backend/
│   ├── app.py                # Actual Flask application code
│   ├── config.py             # App configuration
│   ├── init_db.py            # Database init and demo data
│   ├── migrate_db.py         # Database migration helper
│   ├── requirements.txt      # Backend dependencies
│   ├── utils.py              # Utility functions
│   ├── backend/              # Flask instance folder
│   └── instance/             # Flask instance files
├── database/
│   └── civic_system.db       # SQLite database file (generated locally)
├── frontend/
│   ├── issue.html            # Issue reporting page
│   ├── static/               # Static assets and uploads
│   └── templates/            # Flask templates
└── .gitignore                # Ignored files and folders
```

## What Changed
- The actual application code is in `backend/app.py`.
- Root `app.py` now launches the backend Flask app.
- Root `requirements.txt` now matches `backend/requirements.txt`.
- `Procfile` is available for Heroku/Render-style deployment.

## Local Setup

### 1. Clone the repository
```bash
cd "d:\project civic issues"
```

### 2. Create and activate a Python virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize the database
```bash
python backend/init_db.py init
python backend/init_db.py seed
```

### 5. Run the application
```bash
python app.py
```

Open `http://localhost:5000` in your browser.

## GitHub Deployment Guide

### GitHub Pages? No.
GitHub Pages cannot host Python/Flask apps. Use GitHub for source control and deploy to a platform that supports Python.

### Recommended deployment targets
- Render
- Railway
- Heroku
- Azure App Service

### GitHub deployment flow
1. Push your repository to GitHub.
2. Connect your repo to a deployment service.
3. Use these commands:
   - Install/build: `pip install -r requirements.txt`
   - Start: `python app.py`

### Important deployment settings
- Set `FLASK_ENV=production`
- Set a secure `SECRET_KEY`
- Avoid committing `venv/`, `.env`, or local database files
- Use environment variables for secrets and database URLs

## Quick Start Credentials
- Citizen: phone `9876543210` or `9876543211`
- Municipal Officer: `MUN001` / `password123`
- Department Official: `DEPT001` / `password123`
- Police Officer: `POLICE001` / `password123`

## Notes
- The backend uses `frontend/templates` and `frontend/static` for the UI.
- Keep `database/civic_system.db` local only.
- For production, replace default `SECRET_KEY` in `backend/app.py`.
