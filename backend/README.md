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
│   ├── fonts/          # Vijaya.ttf for Tamil PDF support (download separately)
│   └── js/
├── manage.py
└── requirements.txt
```

## Tamil PDF Font Setup (Important for Tamil Reports)

To properly render Tamil text in PDF reports, you need the **Vijaya font**:

### Option 1: Windows Built-in Font
Vijaya usually comes pre-installed with Windows at:
- `C:\Windows\Fonts\Vijaya.ttf`

### Option 2: Manual Installation
1. Download Vijaya font from a trusted source
2. Place it in: `backend/static/fonts/Vijaya.ttf`
3. The PDF generator will automatically detect and use it

See `backend/static/fonts/README.md` for detailed instructions.

Without this font, Tamil PDF reports may not display correctly.

## Future AI Integration

- Gemini is already integrated in `advisor/views.py`:
  - When the Profile form submits (POST) with `GEMINI_API_KEY` configured, Django calls Gemini server-side.
  - If Gemini is unavailable, the UI displays fallback placeholder results.
- Models: Add when user authentication & profile persistence are needed
- Models: Add when user auth & profile persistence are needed
