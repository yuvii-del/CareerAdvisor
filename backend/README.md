# Career & Educational Advisor - Django Backend

Django backend for the AI-powered Personalized Career & Educational Advisor Platform.

## Quick Start

```bash
# Create and activate virtual environment (recommended)
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Set Gemini API key (DO NOT hardcode it in code)
# Windows PowerShell:
$env:GEMINI_API_KEY="YOUR_NEW_GEMINI_KEY"

# Run migrations (when models are added)
python manage.py migrate

# Start development server
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/login/**

## URL Routes

| Route | Page |
|-------|------|
| `/` | Redirects to /login/ |
| `/login/` | Login / Landing (split screen) |
| `/profile-analysis/` | Student profile form |
| `/career-guidance/` | Career recommendations results |

## Project Structure

```
backend/
├── career_advisor/     # Project config
├── advisor/            # Main app
├── templates/          # Base + advisor templates
├── static/
│   ├── css/            # styles.css, login.css, profile.css, career.css
│   └── js/
├── manage.py
└── requirements.txt
```

## Future AI Integration

- Gemini is already integrated in `advisor/views.py`:
  - When the Profile form submits (POST) with `GEMINI_API_KEY` configured, Django calls Gemini server-side.
  - If Gemini is unavailable, the UI displays fallback placeholder results.
- Models: Add when user authentication & profile persistence are needed
- Models: Add when user auth & profile persistence are needed
