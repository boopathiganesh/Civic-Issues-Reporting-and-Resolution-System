# Quick Start Guide

This guide will help you get the Smart Civic Issue Resolution System running in 5 minutes.

## Prerequisites
- Python 3.7 or higher installed
- Windows, macOS, or Linux

## Step 1: Setup (2 minutes)

### Navigate to Project Directory
```bash
cd "d:\project civic issues"
```

### Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 2: Initialize Database (1 minute)

```bash
python init_db.py
```

This will:
- Create the SQLite database
- Set up all tables
- Populate demo data with test users

## Step 3: Start the Application (1 minute)

```bash
python app.py
```

You should see output like:
```
 * Running on http://127.0.0.1:5000
```

## Step 4: Access the Application (1 minute)

Open your browser and go to: **http://localhost:5000**

## Testing the System

### Login as Citizen
1. Click the "Citizen" card
2. Enter phone: `9876543210`
3. Click "Get OTP"
4. Copy the demo OTP from the success message
5. Paste and verify
6. You're in! Try submitting a complaint

### Login as Municipal Officer
1. Click the "Municipal Officer" card
2. User ID: `MUN001`
3. Password: `password123`
4. Pincode: `600001`
5. View and verify complaints

### Login as Department Officer
1. Click the "Dept. Official" card
2. User ID: `DEPT001`
3. Password: `password123`
4. Department: Select from dropdown
5. View and resolve assigned complaints

### Login as Police Officer
1. Click the "Police Officer" card
2. User ID: `POLICE001`
3. Password: `password123`
5. Investigate fake complaints

## Key Features to Try

### As Citizen:
- ✅ Report new civic issues
- ✅ Track complaint status
- ✅ View location details
- ✅ See updates from authorities

### As Municipal Officer:
- ✅ Review submitted complaints
- ✅ Verify authenticity
- ✅ Forward to departments
- ✅ Set priority levels

### As Department Official:
- ✅ View assigned complaints
- ✅ Take action
- ✅ Upload proof/evidence
- ✅ Mark as resolved

### As Police Officer:
- ✅ Investigate fake complaints
- ✅ Document findings
- ✅ Archive investigations

## Troubleshooting

### "Port 5000 already in use"
```bash
# Change port
python app.py --port 5001
```

### "ModuleNotFoundError"
```bash
# Ensure virtual environment is activated and packages installed
pip install -r requirements.txt
```

### Database issues
```bash
# Reset database and recreate
python init_db.py reset
```

### Virtual Environment not activating
```bash
# Windows Powershell (if you get permission error):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try again
venv\Scripts\activate
```

## Common Pages

- **Home**: http://localhost:5000/
- **Dashboard**: http://localhost:5000/dashboard (after login)
- **Logout**: http://localhost:5000/logout

## Next Steps

1. **Customize**: Edit demo credentials in `init_db.py`
2. **Integrate**: Connect to real SMS service for OTP
3. **Deploy**: Follow deployment guide in README.md
4. **Extend**: Add more features (email, file upload, etc.)

## Getting Help

- Check `README.md` for detailed documentation
- Review `config.py` for configuration options
- Check Flask documentation: https://flask.palletsprojects.com/
- Review SQLAlchemy docs: https://www.sqlalchemy.org/

## Deactivating Virtual Environment

When you're done, deactivate the virtual environment:
```bash
deactivate
```

---

Enjoy using the Smart Civic Issue Resolution System! 🎉
