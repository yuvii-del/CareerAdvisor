"""
Views for Career & Educational Advisor Platform.
AI-ready: context variables prepared for future API integration.
"""

import json
import os
import random
import string

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from .i18n import normalize_lang, get_ui_strings, get_lang_from_request
from .models import EmailOTP, CareerGuidanceHistory


def _generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


def register_view(request):
    """
    Registration page: collect name, email, password, send OTP to email.
    After successful POST, user is created as inactive and an OTP is emailed.
    """
    if request.method == "POST":
        full_name = (request.POST.get("full_name") or "").strip()
        email = (request.POST.get("email") or "").strip().lower()
        password = request.POST.get("password") or ""
        confirm_password = request.POST.get("confirm_password") or ""

        if not full_name or not email or not password:
            messages.error(request, "All fields are required.")
            return render(request, "advisor/register.html")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "advisor/register.html")

        if User.objects.filter(email=email, is_active=True).exists():
            messages.error(request, "An active account with this email already exists. Please login.")
            return render(request, "advisor/register.html")

        # Either get an existing inactive user for this email or create a new one
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email,
                "first_name": full_name,
                "is_active": False,
            },
        )
        if not created:
            user.first_name = full_name
            user.is_active = False
        user.set_password(password)
        user.save()

        # Generate and store OTP
        code = _generate_otp()
        EmailOTP.objects.create(user=user, code=code)

        # Persist pending user in session
        request.session["pending_user_id"] = user.id

        # Send OTP email (uses configured EMAIL_BACKEND)
        send_mail(
            subject="Your Career Advisor verification code",
            message=f"Hello {full_name},\n\nYour verification code is: {code}\n\nIf you did not request this, you can ignore this email.",
            from_email=None,
            recipient_list=[email],
            fail_silently=True,
        )

        # In development, also show the code on screen to make testing easy.
        msg = "We sent a verification code to your email. Please enter it to verify your account."
        if getattr(settings, "DEBUG", False):
            msg += f" (For testing, your code is: {code})"
        messages.success(request, msg)
        return redirect("verify_otp")

    return render(request, "advisor/register.html")


def verify_otp_view(request):
    """
    OTP verification page. Activates the user and logs them in on success.
    """
    pending_user_id = request.session.get("pending_user_id")
    user = None
    if pending_user_id:
        try:
            user = User.objects.get(id=pending_user_id)
        except User.DoesNotExist:
            user = None

    if not user:
        messages.error(request, "No pending registration found. Please create an account first.")
        return redirect("register")

    if request.method == "POST":
        code = (request.POST.get("otp") or "").strip()
        otp_qs = (
            EmailOTP.objects.filter(user=user, code=code, is_used=False)
            .order_by("-created_at")
        )
        otp = otp_qs.first()

        if not otp:
            messages.error(request, "Invalid verification code. Please try again.")
            return render(request, "advisor/verify_otp.html")

        if otp.is_expired:
            messages.error(request, "This verification code has expired. Please register again to receive a new code.")
            return redirect("register")

        otp.is_used = True
        otp.save()

        user.is_active = True
        user.save()

        login(request, user)
        messages.success(request, "Your account has been verified and you are now logged in.")
        # After login, redirect to profile analysis page
        return redirect("profile_analysis")

    return render(request, "advisor/verify_otp.html")


def login_view(request):
    """Landing/Login page - split screen layout with real auth + guest option."""
    # Allow setting language via querystring (e.g., /login/?lang=ta)
    if request.method == "GET" and request.GET.get("lang"):
        request.session["ui_lang"] = normalize_lang(request.GET.get("lang"))

    if request.method == "POST":
        # Save UI language preference (English/Tamil) for all pages
        request.session["ui_lang"] = normalize_lang(request.POST.get("ui_lang"))

        action = request.POST.get("action")
        if action == "guest":
            # Allow guest access directly to profile analysis
            return redirect("profile_analysis")

        if action == "login":
            username_or_email = (request.POST.get("username") or "").strip()
            password = request.POST.get("password") or ""

            # We store username as email for new registrations
            user = authenticate(request, username=username_or_email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect("profile_analysis")
                messages.error(request, "Your account is not active. Please verify your email.")
            else:
                messages.error(request, "Invalid email or password. Please try again.")

    return render(request, "advisor/login.html")


def profile_analysis_view(request):
    """Profile analysis form - collects student details for AI analysis."""
    return render(request, 'advisor/profile_analysis.html')


def build_career_guidance_context(request):
    """Builds the shared context used by the career guidance HTML + PDF views."""
    ui_lang = get_lang_from_request(request)
    ui = get_ui_strings(ui_lang)

    # --- Collect profile inputs (POST) for AI prompt (future-ready) ---
    profile = {}
    if request.method == "POST":
        # Keep keys stable for later model integration
        for key in [
            "full_name",
            "age",
            "gender",
            "location",
            "language",
            "interest_level",
            "school_board",
            "tenth_percentage",
            "twelfth_stream",
            "twelfth_specialization",
            "twelfth_percentage",
            "current_course",
            "skills",
            "strengths",
            "interests",
        ]:
            profile[key] = (request.POST.get(key) or "").strip()

    # --- Defaults (safe fallback) ---
    if ui_lang == "ta":
        career_recommendations = [
            {
                "title": "மென்பொருள் பொறியாளர்",
                "match_percentage": 92,
                "why_suits": "உங்கள் தர்க்க சிந்தனை, நிரலாக்க ஆர்வம் மற்றும் பிரச்சனை தீர்க்கும் திறன் மென்பொருள் பொறியியலுக்கு மிகவும் பொருந்தும்.",
                "required_skills": ["நிரலாக்கம்", "பிரச்சனை தீர்வு", "தர்க்க சிந்தனை", "குழுப்பணி", "தொடர்பாடல்"],
                "learning_path": "அடிப்படைகள்: தரவுக் கட்டமைப்புகள் & ஆல்கொரிதம் → வலை மேம்பாடு → Full-Stack/AI சிறப்பு → திட்டங்கள் → பயிற்சி வேலை",
            },
            {
                "title": "தரவு விஞ்ஞானி",
                "match_percentage": 85,
                "why_suits": "AI/ML பற்றிய ஆர்வமும் பகுப்பாய்வு திறனும் தரவு விஞ்ஞான துறைக்கு உங்களைத் தயாராக்குகிறது.",
                "required_skills": ["புள்ளியியல்", "Python", "Machine Learning", "தரவு பகுப்பாய்வு", "விசுவலைசேஷன்"],
                "learning_path": "புள்ளியியல் → Python → தரவு பகுப்பாய்வு → ML → DL → திட்டங்கள் → Kaggle",
            },
            {
                "title": "தயாரிப்பு மேலாளர்",
                "match_percentage": 78,
                "why_suits": "உங்கள் தலைமைத்துவம் மற்றும் தொடர்பாடல் திறன் தொழில்நுட்பம்-வணிகம் இடையே பாலமாக இருக்க உதவும்.",
                "required_skills": ["தலைமைத்துவம்", "தொடர்பாடல்", "திட்டமிடல்", "பயனர் ஆராய்ச்சி", "அனலிடிக்ஸ்"],
                "learning_path": "வணிக அடிப்படைகள் → Product Management → UX → Agile/Scrum → Portfolio → Internship → Job",
            },
        ]
        education_path = {
            "degrees": [
                "B.Tech கணினி அறிவியல்",
                "B.Tech தகவல் தொழில்நுட்பம்",
                "B.Sc தரவு அறிவியல்",
                "Integrated M.Tech நிரல்கள்",
            ],
            "certifications": [
                "Full-Stack Web Development",
                "Machine Learning Specialization",
                "Data Structures & Algorithms",
                "Cloud Computing (AWS/Azure)",
            ],
            "skill_development": [
                "நிரலாக்க மொழிகள் (Python, JavaScript)",
                "Version Control (Git)",
                "Database நிர்வாகம்",
                "Software Development Lifecycle",
            ],
        }
        growth_timeline = [
            {"level": "தொடக்க நிலை (0-2 ஆண்டுகள்)", "role": "Junior Software Engineer / Associate Developer", "description": "கற்றல், திட்டங்கள், தொழில் நடைமுறைகள் மீது கவனம்.", "salary": "₹4-8 LPA"},
            {"level": "இடைநிலை (2-5 ஆண்டுகள்)", "role": "Software Engineer / Senior Developer", "description": "அம்சங்களை பொறுப்பேற்று, juniors க்கு வழிகாட்டி, ஒரு துறையில் சிறப்பு.", "salary": "₹8-15 LPA"},
            {"level": "மூத்த நிலை (5-10 ஆண்டுகள்)", "role": "Senior Software Engineer / Tech Lead", "description": "குழு வழிநடத்தல், architecture, தொழில்நுட்ப முடிவுகள்.", "salary": "₹15-30 LPA"},
            {"level": "நிபுணர் நிலை (10+ ஆண்டுகள்)", "role": "Principal Engineer / Engineering Manager / CTO", "description": "திட்டத் திசை, புதுமை, பெரிய அளவிலான அமைப்புகள்.", "salary": "₹30+ LPA"},
        ]
    else:
        career_recommendations = [
            {
                "title": "Software Engineer",
                "match_percentage": 92,
                "why_suits": "Your strong analytical thinking, programming interest, and logical approach align perfectly with software engineering. Your problem-solving skills and technical aptitude make you an ideal candidate for this field.",
                "required_skills": ["Programming", "Problem Solving", "Logical Thinking", "Teamwork", "Communication"],
                "learning_path": "Start with fundamentals: Data Structures & Algorithms → Web Development → Specialize in Full-Stack or AI/ML → Build projects → Apply for internships",
            },
            {
                "title": "Data Scientist",
                "match_percentage": 85,
                "why_suits": "Your interest in AI & Machine Learning, combined with strong analytical skills and mathematical background, positions you well for a career in data science.",
                "required_skills": ["Statistics", "Python", "Machine Learning", "Data Analysis", "Visualization"],
                "learning_path": "Statistics & Probability → Python Programming → Data Analysis → Machine Learning → Deep Learning → Real-world Projects → Kaggle Competitions",
            },
            {
                "title": "Product Manager",
                "match_percentage": 78,
                "why_suits": "Your leadership skills, communication abilities, and creative thinking make you well-suited for product management, where you'll bridge technical and business worlds.",
                "required_skills": ["Leadership", "Communication", "Strategic Thinking", "User Research", "Analytics"],
                "learning_path": "Business Fundamentals → Product Management Courses → User Experience Design → Agile/Scrum → Build a Product Portfolio → Internships → Full-time Roles",
            },
        ]

        education_path = {
            "degrees": [
                "B.Tech in Computer Science",
                "B.Tech in Information Technology",
                "B.Sc in Data Science",
                "Integrated M.Tech Programs",
            ],
            "certifications": [
                "Full-Stack Web Development",
                "Machine Learning Specialization",
                "Data Structures & Algorithms",
                "Cloud Computing (AWS/Azure)",
            ],
            "skill_development": [
                "Programming Languages (Python, JavaScript)",
                "Version Control (Git)",
                "Database Management",
                "Software Development Lifecycle",
            ],
        }
        growth_timeline = [
            {"level": "Entry Level (0-2 years)", "role": "Junior Software Engineer / Associate Developer", "description": "Focus on learning, building projects, and understanding industry practices.", "salary": "₹4-8 LPA"},
            {"level": "Mid Level (2-5 years)", "role": "Software Engineer / Senior Developer", "description": "Take ownership of features, mentor juniors, and specialize in a domain.", "salary": "₹8-15 LPA"},
            {"level": "Senior Level (5-10 years)", "role": "Senior Software Engineer / Tech Lead", "description": "Lead teams, architect solutions, and drive technical decisions.", "salary": "₹15-30 LPA"},
            {"level": "Expert Level (10+ years)", "role": "Principal Engineer / Engineering Manager / CTO", "description": "Shape organizational strategy, innovate, and build scalable systems.", "salary": "₹30+ LPA"},
        ]

    ai_error = None

    # Determine which sub-page we are on (work vs education)
    resolver_match = getattr(request, "resolver_match", None)
    if resolver_match and resolver_match.url_name == "career_guidance_education":
        page_type = "education"
    else:
        # Default to work view (also used for original 'career_guidance' path)
        page_type = "work"

    # --- Gemini integration (server-side) ---
    # IMPORTANT: Do NOT hardcode keys. Set GEMINI_API_KEY in your environment.
    # If key not present or SDK missing, we render the fallback placeholders above.
    if request.method == "POST" and os.environ.get("GEMINI_API_KEY"):
        try:
            from google import genai  # google-genai

            client = genai.Client()  # reads GEMINI_API_KEY from env

            output_language_instruction = (
                "Write all natural language fields in Tamil."
                if ui_lang == "ta"
                else "Write all natural language fields in English."
            )

            prompt = (
                "You are an AI-powered Personalized Career & Educational Advisor for students.\n"
                "Given the student's profile below, generate 3 career recommendations.\n\n"
                f"{output_language_instruction}\n\n"
                "Return ONLY valid JSON with this schema:\n"
                "{\n"
                '  "career_recommendations": [\n'
                "    {\n"
                '      "title": string,\n'
                '      "match_percentage": number (0-100),\n'
                '      "why_suits": string,\n'
                '      "required_skills": [string],\n'
                '      "learning_path": string\n'
                "    }\n"
                "  ],\n"
                '  "education_path": {\n'
                '    "degrees": [string],\n'
                '    "certifications": [string],\n'
                '    "skill_development": [string]\n'
                "  },\n"
                '  "growth_timeline": [\n'
                "    {\n"
                '      "level": string,\n'
                '      "role": string,\n'
                '      "description": string,\n'
                '      "salary": string\n'
                "    }\n"
                "  ]\n"
                "}\n\n"
                f"Student profile:\n{json.dumps(profile, ensure_ascii=False)}\n"
            )

            response = client.models.generate_content(
                model="gemini-2.0-flash-lite",
                contents=prompt,
            )

            # The SDK exposes response.text for convenient access.
            data = json.loads((response.text or "").strip())

            # Validate & apply (best-effort)
            if isinstance(data, dict):
                if isinstance(data.get("career_recommendations"), list) and data["career_recommendations"]:
                    career_recommendations = data["career_recommendations"]
                if isinstance(data.get("education_path"), dict):
                    education_path = data["education_path"]
                if isinstance(data.get("growth_timeline"), list) and data["growth_timeline"]:
                    growth_timeline = data["growth_timeline"]
        except Exception as e:
            ai_error = str(e)

    # Persist a history snapshot so we can show recent career growth information.
    if request.method == "POST":
        # Ensure the session has a key so we can associate guest history.
        if not request.session.session_key:
            request.session.save()
        session_key = request.session.session_key or ""
        history_user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None

        try:
            CareerGuidanceHistory.objects.create(
                user=history_user,
                session_key=session_key,
                ui_lang=ui_lang,
                profile=profile,
                career_recommendations=career_recommendations,
                education_path=education_path,
                growth_timeline=growth_timeline,
            )
        except Exception:
            # History persistence should never break the main flow,
            # so we swallow errors here.
            pass

    return {
        "career_recommendations": career_recommendations,
        "education_path": education_path,
        "growth_timeline": growth_timeline,
        "ai_error": ai_error,
        "ui": ui,
        "ui_lang": ui_lang,
        "page_type": page_type,
    }


def career_guidance_view(request):
    """Career guidance results - AI-ready placeholder data (Gemini optional)."""
    context = build_career_guidance_context(request)
    return render(request, "advisor/career_guidance.html", context)


def career_guidance_pdf_view(request):
    """Generate a PDF download of the current career guidance results."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    context = build_career_guidance_context(request)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="career_guidance_report.pdf"'

    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Basic text settings
    left_margin = 40
    right_margin = 40
    max_width = width - left_margin - right_margin
    font_name = "Helvetica"
    font_size = 11
    line_height = 14

    pdf.setFont(font_name, font_size)

    y = height - 50

    def write_line(text="", leading=line_height):
        """Write a line of text with simple word-wrapping within page margins."""
        nonlocal y
        if text is None:
            text = ""
        text = str(text)

        # Blank line handling
        if text.strip() == "":
            if y < 40:
                pdf.showPage()
                pdf.setFont(font_name, font_size)
                y = height - 50
            y -= leading
            return

        words = text.split()
        current = ""

        for word in words:
            candidate = (current + " " + word).strip()
            text_width = pdf.stringWidth(candidate, font_name, font_size)
            if text_width > max_width and current:
                if y < 40:
                    pdf.showPage()
                    pdf.setFont(font_name, font_size)
                    y = height - 50
                pdf.drawString(left_margin, y, current)
                y -= leading
                current = word
            else:
                current = candidate

        if current:
            if y < 40:
                pdf.showPage()
                pdf.setFont(font_name, font_size)
                y = height - 50
            pdf.drawString(left_margin, y, current)
            y -= leading

    write_line("Career Guidance Report")
    write_line("======================")
    write_line()

    careers = context.get("career_recommendations", [])
    if careers:
        write_line("Career Recommendations")
        write_line("-----------------------")
        for idx, career in enumerate(careers, start=1):
            title = str(career.get("title", ""))
            match = career.get("match_percentage")
            match_text = f"{match}% Match" if match is not None else ""
            why = str(career.get("why_suits", ""))
            skills = career.get("required_skills") or []
            learning = str(career.get("learning_path", ""))

            write_line()
            write_line(f"{idx}. {title} {f'({match_text})' if match_text else ''}")
            if why:
                write_line(f"   Why it suits you: {why}")
            if skills:
                write_line(f"   Required skills: {', '.join(map(str, skills))}")
            if learning:
                write_line(f"   Suggested learning path: {learning}")

        write_line()

    education = context.get("education_path") or {}
    degrees = education.get("degrees") or []
    certs = education.get("certifications") or []
    skills_dev = education.get("skill_development") or []

    if degrees or certs or skills_dev:
        write_line("Education & Learning Path")
        write_line("-------------------------")

        if degrees:
            write_line()
            write_line("Recommended Degrees:")
            for d in degrees:
                write_line(f" - {d}")

        if certs:
            write_line()
            write_line("Online Certifications:")
            for c in certs:
                write_line(f" - {c}")

        if skills_dev:
            write_line()
            write_line("Skill Development Focus Areas:")
            for s in skills_dev:
                write_line(f" - {s}")

        write_line()

    timeline = context.get("growth_timeline") or []
    if timeline:
        write_line("Growth Timeline")
        write_line("---------------")
        for item in timeline:
            level = str(item.get("level", ""))
            role = str(item.get("role", ""))
            desc = str(item.get("description", ""))
            salary = str(item.get("salary", ""))

            write_line()
            if level:
                write_line(level)
            if role:
                write_line(f"Role: {role}")
            if desc:
                write_line(f"Details: {desc}")
            if salary:
                write_line(f"Salary Range: {salary}")

        write_line()

    pdf.showPage()
    pdf.save()
    return response


def chatbot_view(request):
    """
    Simple AJAX chatbot endpoint for the Profile Analysis page.
    Expects JSON: {"message": "<user text>"} and returns {"reply": "<ai text>"}.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    ui_lang = get_lang_from_request(request)
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    user_message = (payload.get("message") or "").strip()
    if not user_message:
        return JsonResponse({"error": "Empty message"}, status=400)

    # If no API key, return a friendly static reply instead of breaking.
    if not os.environ.get("GEMINI_API_KEY"):
        if ui_lang == "ta":
            reply = "இப்போது AI உரையாடல் செயல்பாடு கிடைக்கவில்லை. பின்னர் முயற்சி செய்யவும்."
        else:
            reply = "AI chat is not available right now. Please try again later."
        return JsonResponse({"reply": reply})

    try:
        from google import genai

        client = genai.Client()

        language_instruction = (
            "Reply in Tamil only."
            if ui_lang == "ta"
            else "Reply in English only."
        )

        prompt = (
            "You are a friendly career guidance chatbot for students.\n"
            "Keep answers short (2–4 sentences) and practical.\n"
            f"{language_instruction}\n\n"
            f"User message: {user_message}\n"
        )

        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
        )

        text = (response.text or "").strip()
        if not text:
            if ui_lang == "ta":
                text = "மன்னிக்கவும், இப்போது பதிலை உருவாக்க முடியவில்லை."
            else:
                text = "Sorry, I couldn't generate a response right now."

        return JsonResponse({"reply": text})
    except Exception as exc:
        if ui_lang == "ta":
            msg = "AI உரையாடலின் போது பிழை ஏற்பட்டது. பின்னர் முயற்சி செய்யவும்."
        else:
            msg = "There was an error while talking to the AI. Please try again later."
        return JsonResponse({"reply": msg, "error": str(exc)}, status=500)


def career_history_view(request):
    """
    Show a recent history page of generated career growth information.
    - For logged-in users, history is scoped to their account.
    - For guests, history is scoped to the current browser session.
    """
    ui_lang = get_lang_from_request(request)
    ui = get_ui_strings(ui_lang)

    history_user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None

    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key or ""

    qs = CareerGuidanceHistory.objects.all()
    if history_user:
        qs = qs.filter(user=history_user)
    elif session_key:
        qs = qs.filter(session_key=session_key)
    else:
        qs = qs.none()

    history_items = qs.order_by("-created_at")[:20]

    return render(
        request,
        "advisor/career_history.html",
        {
            "history_items": history_items,
            "ui": ui,
            "ui_lang": ui_lang,
        },
    )
