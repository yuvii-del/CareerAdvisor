"""
Views for Career & Educational Advisor Platform.
AI-ready: context variables prepared for future API integration.
"""

import json
import os
import random
import string
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView as BasePasswordResetView
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .career_normalize import normalize_required_skills
from .i18n import normalize_lang, get_ui_strings, get_lang_from_request
from .models import EmailOTP, CareerGuidanceHistory, StudentProfile


def _generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


def _to_decimal(value: str | None):
    if value is None:
        return None
    value = str(value).strip()
    if not value:
        return None
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None


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

        required_profile_fields = [
            "age",
            "gender",
            "location",
            "language",
            "school_board",
            "tenth_percentage",
            "twelfth_stream",
            "twelfth_specialization",
            "twelfth_percentage",
        ]

        if not full_name or not email or not password:
            messages.error(request, "All fields are required.")
            return render(request, "advisor/register.html")
        if any(not (request.POST.get(k) or "").strip() for k in required_profile_fields):
            messages.error(request, "Please complete all required basic and academic details.")
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

        # Persist full signup profile details so user does not re-enter after login.
        profile, _ = StudentProfile.objects.get_or_create(user=user)
        raw_age = (request.POST.get("age") or "").strip()
        profile.age = int(raw_age) if raw_age.isdigit() else None
        profile.gender = (request.POST.get("gender") or "").strip()
        profile.location = (request.POST.get("location") or "").strip()
        profile.preferred_language = (request.POST.get("language") or "").strip()
        profile.school_board = (request.POST.get("school_board") or "").strip()
        profile.tenth_percentage = _to_decimal(request.POST.get("tenth_percentage"))
        profile.twelfth_stream = (request.POST.get("twelfth_stream") or "").strip()
        profile.twelfth_specialization = (request.POST.get("twelfth_specialization") or "").strip()
        profile.twelfth_percentage = _to_decimal(request.POST.get("twelfth_percentage"))
        profile.current_course = (request.POST.get("current_course") or "").strip()
        profile.subjects = (request.POST.get("subjects") or "").strip()
        profile.save()

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
        # After login, go directly to preferences page.
        return redirect("preferences")

    return render(request, "advisor/verify_otp.html")


class PasswordResetView(BasePasswordResetView):
    """Store reset link in session when DEBUG so user can click it from the done page."""

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        if getattr(settings, "DEBUG", False):
            users = User.objects.filter(email__iexact=email, is_active=True)
            for user in users[:1]:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                path = reverse(
                    "password_reset_confirm",
                    kwargs={"uidb64": uid, "token": token},
                )
                protocol = "https" if self.request.is_secure() else "http"
                domain = self.request.get_host()
                reset_link = f"{protocol}://{domain}{path}"
                self.request.session["password_reset_link"] = reset_link
                break
        return super().form_valid(form)


def password_reset_done_view(request):
    """Show done page and, in DEBUG, the clickable reset link from session."""
    reset_link = request.session.pop("password_reset_link", None)
    return render(
        request,
        "advisor/password_reset_done.html",
        {"reset_link": reset_link},
    )


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
            # Allow guest access directly to preferences page
            return redirect("preferences")

        if action == "login":
            username_or_email = (request.POST.get("username") or "").strip()
            password = request.POST.get("password") or ""

            # We store username as email for new registrations
            user = authenticate(request, username=username_or_email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect("preferences")
                messages.error(request, "Your account is not active. Please verify your email.")
            else:
                messages.error(request, "Invalid email or password. Please try again.")

    return render(request, "advisor/login.html")


def logout_view(request):
    """Simple logout flow."""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")


def profile_analysis_view(request):
    """Legacy route: redirect to new preferences flow."""
    return redirect("preferences")


def preferences_view(request):
    """
    Preferences page after login.
    Uses stored signup details and asks only preference-related inputs.
    """
    profile = None
    if getattr(request, "user", None) and request.user.is_authenticated:
        profile, _ = StudentProfile.objects.get_or_create(user=request.user)

    context = {
        "profile": profile,
    }
    return render(request, "advisor/preferences.html", context)


def edit_profile_view(request):
    """
    Edit saved basic + academic details for logged-in users.
    """
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        messages.error(request, "Please login to edit your profile.")
        return redirect("login")

    profile, _ = StudentProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        full_name = (request.POST.get("full_name") or "").strip()
        raw_age = (request.POST.get("age") or "").strip()

        required_fields = [
            full_name,
            raw_age,
            (request.POST.get("gender") or "").strip(),
            (request.POST.get("location") or "").strip(),
            (request.POST.get("language") or "").strip(),
            (request.POST.get("school_board") or "").strip(),
            (request.POST.get("tenth_percentage") or "").strip(),
            (request.POST.get("twelfth_stream") or "").strip(),
            (request.POST.get("twelfth_specialization") or "").strip(),
            (request.POST.get("twelfth_percentage") or "").strip(),
        ]
        if any(not item for item in required_fields):
            messages.error(request, "Please complete all required fields.")
            return render(request, "advisor/edit_profile.html", {"profile": profile})

        request.user.first_name = full_name
        request.user.save(update_fields=["first_name"])

        profile.age = int(raw_age) if raw_age.isdigit() else None
        profile.gender = (request.POST.get("gender") or "").strip()
        profile.location = (request.POST.get("location") or "").strip()
        profile.preferred_language = (request.POST.get("language") or "").strip()
        profile.school_board = (request.POST.get("school_board") or "").strip()
        profile.tenth_percentage = _to_decimal(request.POST.get("tenth_percentage"))
        profile.twelfth_stream = (request.POST.get("twelfth_stream") or "").strip()
        profile.twelfth_specialization = (request.POST.get("twelfth_specialization") or "").strip()
        profile.twelfth_percentage = _to_decimal(request.POST.get("twelfth_percentage"))
        profile.current_course = (request.POST.get("current_course") or "").strip()
        profile.subjects = (request.POST.get("subjects") or "").strip()
        profile.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("preferences")

    return render(request, "advisor/edit_profile.html", {"profile": profile})


def build_career_guidance_context(request):
    """Builds the shared context used by the career guidance HTML + PDF views."""
    ui_lang = get_lang_from_request(request)
    ui = get_ui_strings(ui_lang)

    # --- Build profile from stored signup details + submitted preferences ---
    profile = {}
    stored_profile = None
    if getattr(request, "user", None) and request.user.is_authenticated:
        stored_profile = StudentProfile.objects.filter(user=request.user).first()

    if stored_profile:
        profile = {
            "full_name": request.user.first_name or request.user.username,
            "age": str(stored_profile.age or ""),
            "gender": stored_profile.gender or "",
            "location": stored_profile.location or "",
            "language": stored_profile.preferred_language or "",
            "interest_level": stored_profile.interest_level or "",
            "school_board": stored_profile.school_board or "",
            "tenth_percentage": str(stored_profile.tenth_percentage or ""),
            "twelfth_stream": stored_profile.twelfth_stream or "",
            "twelfth_specialization": stored_profile.twelfth_specialization or "",
            "twelfth_percentage": str(stored_profile.twelfth_percentage or ""),
            "current_course": stored_profile.current_course or "",
            "subjects": stored_profile.subjects or "",
            "skills": stored_profile.skills or "",
            "strengths": stored_profile.strengths or "",
            "interests": stored_profile.interests or "",
            "other_interest": stored_profile.other_interest or "",
        }

    if request.method == "POST":
        for key in ["interest_level", "skills", "strengths", "interests", "other_interest"]:
            profile[key] = (request.POST.get(key) or "").strip()

        # Support guests/legacy by reading full fields if posted.
        for key in [
            "full_name",
            "age",
            "gender",
            "location",
            "language",
            "school_board",
            "tenth_percentage",
            "twelfth_stream",
            "twelfth_specialization",
            "twelfth_percentage",
            "current_course",
            "subjects",
        ]:
            posted = (request.POST.get(key) or "").strip()
            if posted:
                profile[key] = posted

        if stored_profile:
            stored_profile.interest_level = profile.get("interest_level", "")
            stored_profile.skills = profile.get("skills", "")
            stored_profile.strengths = profile.get("strengths", "")
            stored_profile.interests = profile.get("interests", "")
            stored_profile.other_interest = profile.get("other_interest", "")
            stored_profile.save()

    # --- Defaults (safe fallback) ---
    if ui_lang == "ta":
        career_recommendations = [
            {
                "title": "மென்பொருள் பொறியாளர்",
                "match_percentage": 92,
                "why_suits": "உங்கள் தர்க்க சிந்தனை, நிரலாக்க ஆர்வம் மற்றும் பிரச்சனை தீர்க்கும் திறன் மென்பொருள் பொறியியலுக்கு மிகவும் பொருந்தும்.",
                "required_skills": ["நிரலாக்கம்", "பிரச்சனை தீர்வு", "தர்க்க சிந்தனை", "குழுப்பணி", "தொடர்பாடல்", "ஆப் வடிவமைப்பு", "API ஒருங்கிணைப்பு", "பதிப்பு கட்டுப்பாடு (Git)", "சோதனை & பிழைத்திருத்தம்", " Agile முறைகள்"],
                "learning_path": "அடிப்படைகள்: தரவுக் கட்டமைப்புகள் & ஆல்கொரிதம் → வலை மேம்பாடு → Full-Stack/AI சிறப்பு → திட்டங்கள் → பயிற்சி வேலை",
            },
            {
                "title": "தரவு விஞ்ஞானி",
                "match_percentage": 85,
                "why_suits": "AI/ML பற்றிய ஆர்வமும் பகுப்பாய்வு திறனும் தரவு விஞ்ஞான துறைக்கு உங்களைத் தயாராக்குகிறது.",
                "required_skills": ["புள்ளியியல்", "Python", "Machine Learning", "தரவு பகுப்பாய்வு", "விசுவலைசேஷன்", "SQL", "Deep Learning", "NLP அடிப்படைகள்", "பெரிய தரவு கருவிகள்", "மாதிரி நிறுத்தல்"],
                "learning_path": "புள்ளியியல் → Python → தரவு பகுப்பாய்வு → ML → DL → திட்டங்கள் → Kaggle",
            },
            {
                "title": "தயாரிப்பு மேலாளர்",
                "match_percentage": 78,
                "why_suits": "உங்கள் தலைமைத்துவம் மற்றும் தொடர்பாடல் திறன் தொழில்நுட்பம்-வணிகம் இடையே பாலமாக இருக்க உதவும்.",
                "required_skills": ["தலைமைத்துவம்", "தொடர்பாடல்", "திட்டமிடல்", "பயனர் ஆராய்ச்சி", "அனலிடிக்ஸ்", "சந்தை பகுப்பாய்வு", "வழி நடத்துதல்", "Agile/Scrum", "தரவு முடிவுகள்", "ஆக்ரோக்கமான சிந்தனை"],
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
                "required_skills": ["Programming", "Problem Solving", "Logical Thinking", "Teamwork", "Communication", "App Design", "API Integration", "Version Control (Git)", "Testing & Debugging", "Agile Methodologies"],
                "learning_path": "Start with fundamentals: Data Structures & Algorithms → Web Development → Specialize in Full-Stack or AI/ML → Build projects → Apply for internships",
            },
            {
                "title": "Data Scientist",
                "match_percentage": 85,
                "why_suits": "Your interest in AI & Machine Learning, combined with strong analytical skills and mathematical background, positions you well for a career in data science.",
                "required_skills": ["Statistics", "Python", "Machine Learning", "Data Analysis", "Visualization", "SQL", "Deep Learning", "NLP Basics", "Big Data Tools", "Model Deployment"],
                "learning_path": "Statistics & Probability → Python Programming → Data Analysis → Machine Learning → Deep Learning → Real-world Projects → Kaggle Competitions",
            },
            {
                "title": "Product Manager",
                "match_percentage": 78,
                "why_suits": "Your leadership skills, communication abilities, and creative thinking make you well-suited for product management, where you'll bridge technical and business worlds.",
                "required_skills": ["Leadership", "Communication", "Strategic Thinking", "User Research", "Analytics", "Market Analysis", "Roadmapping", "Agile/Scrum", "Data-Driven Decisions", "Critical Thinking"],
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

    # Subject-aware tuning of fallback (e.g., Math + Computer Science for school students)
    subjects_text = (profile.get("subjects") or "").lower()
    if request.method == "POST" and subjects_text:
        has_math = "math" in subjects_text
        has_cs = "computer" in subjects_text or "cs" in subjects_text
        if has_math and has_cs:
            if ui_lang == "ta":
                career_recommendations = [
                    {
                        "title": "மென்பொருள் உருவாக்குனர் (Software Developer)",
                        "match_percentage": 95,
                        "why_suits": "நீங்கள் கணிதமும் கணினி அறிவியலும் படிப்பதால், பெரிய பிரச்சனைகளை சிறு படிகளாகப் பிழிந்து தீர்க்கும் திறன் உங்களுக்கு உள்ளது. இந்த திறன் மென்பொருள், வலைத்தளம், மொபைல் அப்புகளை உருவாக்க மிகவும் உதவும்.",
                        "required_skills": [
                            "அடிப்படை கணிதம்",
                            "நிரலாக்கம் (Programming)",
                            "பிரச்சனை தீர்க்கும் திறன்",
                            "கவனச்சீர்மை",
                            "ஆல்கொரிதம் வடிவமைப்பு",
                            "குறியாக்க பிழைத்திருத்தம்",
                            "Version Control அடிப்படைகள்",
                            "மென்பொருள் சோதனை",
                        ],
                        "learning_path": "பள்ளி கணிதப் பாடங்கள் → C/Python போன்ற மொழிகளில் நிரலாக்க அடிப்படைகள் → சிறிய project-கள் (calculator, game, website) → internship / part-time projects.",
                    },
                    {
                        "title": "டேட்டா விஞ்ஞானி (Data Scientist)",
                        "match_percentage": 90,
                        "why_suits": "நீங்கள் எண்கள், கிராஃப்கள், தரவுகளை விரும்பினால், கணிதமும் நிரலாக்கமும் சேர்ந்த இந்த துறை உங்களுக்கு பொருந்தும். நீங்கள் தரவிலிருந்து பயனுள்ள தகவல்களை கண்டுபிடிப்பீர்கள்.",
                        "required_skills": [
                            "புள்ளியியல் அடிப்படைகள்",
                            "Python நிரலாக்கம்",
                            "தரவு பகுப்பாய்வு",
                            "தர்க்க சிந்தனை",
                            "Machine Learning அடிப்படைகள்",
                            "SQL database வினவல்கள்",
                            "தரவு சுத்தம் செய்யும் நுட்பங்கள்",
                            "புள்ளியியல் மாதிரி உருவாக்கம்",
                        ],
                        "learning_path": "அடிப்படை புள்ளியியல் மற்றும் probability → Python → data analysis (pandas, Excel) → சிறிய data projects → கல்லூரியில் Data Science / AI பாடநெறி.",
                    },
                    {
                        "title": "கேம் டெவலப்பர் (Game Developer)",
                        "match_percentage": 85,
                        "why_suits": "வீடியோ கேம்கள், animation போன்றவற்றில் ஆர்வம் இருந்தால், கணிதம் (movement, score, physics) மற்றும் கணினி நிரலாக்கம் இரண்டும் இங்கு முக்கியம். நீங்கள் குழந்தைகளுக்கும் இளைஞர்களுக்கும் புதுசாக கேம்களை உருவாக்கலாம்.",
                        "required_skills": [
                            "கணித அடிப்படைகள் (geometry, logic)",
                            "நிரலாக்கம் (C#, C++, Python)",
                            "படைப்பாற்றல்",
                            "குழுப்பணி",
                            "கேம் இயற்பியல் புரிதல்",
                            "3D கிராபிக்ஸ் அடிப்படைகள்",
                            "நிலை வடிவமைப்பு கொள்கைகள்",
                            "வீரர் அனுபவ வடிவமைப்பு",
                        ],
                        "learning_path": "பள்ளி கணிதத்தை நன்றாகக் கற்றல் → game engines (Unity, Unreal) அறிதல் → சிறிய game projects → கல்லூரியில் Game Dev / Computer Science degree.",
                    },
                ]
                education_path = {
                    "degrees": [
                        "B.Sc / B.Tech கணினி அறிவியல்",
                        "B.Tech தகவல் தொழில்நுட்பம்",
                        "B.Sc Mathematics + Computer Science",
                    ],
                    "certifications": [
                        "Intro to Programming (Python/JavaScript)",
                        "Data Science / Analytics அடிப்படை course",
                        "Game Development (Unity / Unreal)",
                    ],
                    "skill_development": [
                        "தினசரி programming பயிற்சி (small problems)",
                        "ஆன்லைன் math & coding challenges",
                        "Team projects மற்றும் hackathon அனுபவம்",
                    ],
                }
                growth_timeline = [
                    {
                        "level": "தொடக்க நிலை (0-2 ஆண்டுகள்)",
                        "role": "Junior Developer / Intern",
                        "description": "அடிப்படைகளை கற்றுக்கொண்டு, சிறிய project-களில் பங்கேற்று, seniors-ிடம் இருந்து கற்றுக்கொள்வது.",
                        "salary": "₹3-6 LPA (மாறுபடும்)",
                    },
                    {
                        "level": "இடைநிலை (2-5 ஆண்டுகள்)",
                        "role": "Software Engineer / Data Analyst / Game Developer",
                        "description": "முக்கிய அம்சங்களை செய்யும் பொறுப்பு, real-world systems-இல் வேலை.",
                        "salary": "₹6-12 LPA (மாறுபடும்)",
                    },
                    {
                        "level": "மூத்த நிலை (5+ ஆண்டுகள்)",
                        "role": "Senior Engineer / Tech Lead",
                        "description": "குழுக்களை வழிநடத்தல், வடிவமைப்பு முடிவுகள் எடுப்பது, இளம் developers-க்கு வழிகாட்டுதல்.",
                        "salary": "₹12+ LPA (மாறுபடும்)",
                    },
                ]
            else:
                career_recommendations = [
                    {
                        "title": "Software Developer / Programmer",
                        "match_percentage": 95,
                        "why_suits": "You study Math and Computer Science, so you are already used to thinking step-by-step and solving puzzles. This career lets you turn ideas into apps, websites, and tools that real people use.",
                        "required_skills": [
                            "Basic mathematics",
                            "Programming (e.g. Python, JavaScript)",
                            "Logical thinking",
                            "Problem solving",
                            "Attention to detail",
                            "Algorithm design",
                            "Code debugging",
                            "Version control basics",
                        ],
                        "learning_path": "School Math → Learn one programming language well → Build small projects (calculator, simple website, mini game) → Contribute to bigger projects and internships.",
                    },
                    {
                        "title": "Data Scientist",
                        "match_percentage": 90,
                        "why_suits": "You like numbers and logic from Math, and you know how to code from Computer Science. As a data scientist you use both to understand data and help people make better decisions.",
                        "required_skills": [
                            "Statistics and probability basics",
                            "Python programming",
                            "Data analysis and visualization",
                            "Curiosity about patterns in data",
                            "Machine learning fundamentals",
                            "SQL database queries",
                            "Data cleaning techniques",
                            "Statistical modeling",
                        ],
                        "learning_path": "Learn statistics basics → Learn Python for data → Practice with small datasets and charts → Study machine learning in college or online courses.",
                    },
                    {
                        "title": "Game Developer",
                        "match_percentage": 85,
                        "why_suits": "If you enjoy games and creativity, Math helps you with movement, scoring and physics, while Computer Science helps you build the game itself. You can create fun experiences for other people.",
                        "required_skills": [
                            "Math basics (especially geometry and logic)",
                            "Programming (C#, C++, or similar)",
                            "Creative thinking",
                            "Teamwork",
                            "Game physics understanding",
                            "3D graphics basics",
                            "Level design principles",
                            "Player experience design",
                        ],
                        "learning_path": "Strengthen school Math → Learn a language used in games (e.g. C# with Unity) → Build tiny games and experiments → Study Computer Science / Game Development after school.",
                    },
                ]
                education_path = {
                    "degrees": [
                        "B.Sc / B.Tech in Computer Science",
                        "B.Tech in Information Technology",
                        "B.Sc Mathematics with Computer Science",
                    ],
                    "certifications": [
                        "Intro to Programming (Python / JavaScript)",
                        "Beginner Data Science / Analytics course",
                        "Game Development with Unity or Unreal",
                    ],
                    "skill_development": [
                        "Regular coding practice (small problems daily)",
                        "Online math and coding challenges",
                        "Team projects and hackathon experience",
                    ],
                }
                growth_timeline = [
                    {
                        "level": "Entry Level (0-2 years)",
                        "role": "Junior Developer / Intern",
                        "description": "You learn foundations, fix bugs, and build small features while getting used to real-world projects.",
                        "salary": "₹3-6 LPA (varies)",
                    },
                    {
                        "level": "Mid Level (2-5 years)",
                        "role": "Software Engineer / Data Analyst / Game Developer",
                        "description": "You own full features end-to-end and work more independently on important parts of products.",
                        "salary": "₹6-12 LPA (varies)",
                    },
                    {
                        "level": "Senior Level (5+ years)",
                        "role": "Senior Engineer / Tech Lead",
                        "description": "You design systems, guide junior teammates, and help decide technical direction.",
                        "salary": "₹12+ LPA (varies)",
                    },
                ]

    ai_error = None

    # Determine which sub-page we are on (work vs education)
    resolver_match = getattr(request, "resolver_match", None)
    if resolver_match and resolver_match.url_name == "career_guidance_work":
        page_type = "work"
    elif resolver_match and resolver_match.url_name == "career_guidance_education":
        page_type = "education"
    else:
        # Default to education view
        page_type = "education"

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
                    for c in career_recommendations:
                        if isinstance(c, dict):
                            c["required_skills"] = normalize_required_skills(c.get("required_skills"))
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
            full_snapshot = {
                "profile": profile,
                "career_recommendations": career_recommendations,
                "education_path": education_path,
                "growth_timeline": growth_timeline,
                "ai_error": ai_error,
                "ui_lang": ui_lang,
            }
            history_item = CareerGuidanceHistory.objects.create(
                user=history_user,
                session_key=session_key,
                ui_lang=ui_lang,
                profile=profile,
                career_recommendations=career_recommendations,
                education_path=education_path,
                growth_timeline=growth_timeline,
                ai_error=ai_error or "",
                full_snapshot=full_snapshot,
            )
            request.session["last_history_id"] = history_item.id
        except Exception:
            # History persistence should never break the main flow,
            # so we swallow errors here.
            pass
    else:
        # For GET requests (tabs/PDF), reuse last generated snapshot if available.
        history_item = None
        last_history_id = request.session.get("last_history_id")
        if last_history_id:
            history_item = CareerGuidanceHistory.objects.filter(id=last_history_id).first()
        if not history_item:
            if not request.session.session_key:
                request.session.save()
            session_key = request.session.session_key or ""
            history_user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
            qs = CareerGuidanceHistory.objects.all()
            if history_user:
                qs = qs.filter(user=history_user)
            elif session_key:
                qs = qs.filter(session_key=session_key)
            history_item = qs.order_by("-created_at").first()
        if history_item:
            profile = history_item.profile or profile
            career_recommendations = history_item.career_recommendations or career_recommendations
            education_path = history_item.education_path or education_path
            growth_timeline = history_item.growth_timeline or growth_timeline
            # Also restore AI error state from history
            ai_error = history_item.ai_error or ai_error

    # Build skill roadmap from AI results dynamically
    skill_roadmap_data = {"beginner": None, "intermediate": None, "advanced": None}
    if career_recommendations and isinstance(career_recommendations, list):
        # Extract skills from all recommended careers to build dynamic roadmap
        all_skills = []
        for career in career_recommendations:
            if isinstance(career, dict):
                skills = normalize_required_skills(career.get("required_skills", []))
                all_skills.extend(skills)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in all_skills:
            skill_key = skill.lower()
            if skill_key not in seen:
                seen.add(skill_key)
                unique_skills.append(skill)
        
        # Categorize skills into roadmap stages based on complexity
        if unique_skills:
            # Split skills into three stages with better distribution
            # Ensure each stage has at least 5 skills for pagination to trigger
            n = len(unique_skills)
            
            # Simple split: divide into roughly equal thirds
            # But ensure minimum of 5 skills per stage when possible
            third = max(5, (n + 2) // 3)  # Round up division
            
            skill_roadmap_data["beginner"] = {
                "title": ui["roadmap_beginner"],
                "description": ui["roadmap_beginner_desc"],
                "skills": unique_skills[:third],
            }
            skill_roadmap_data["intermediate"] = {
                "title": ui["roadmap_intermediate"],
                "description": ui["roadmap_intermediate_desc"],
                "skills": unique_skills[third:third*2],
            }
            skill_roadmap_data["advanced"] = {
                "title": ui["roadmap_advanced"],
                "description": ui["roadmap_advanced_desc"],
                "skills": unique_skills[third*2:],
            }

    return {
        "career_recommendations": career_recommendations,
        "education_path": education_path,
        "growth_timeline": growth_timeline,
        "ai_error": ai_error,
        "ui": ui,
        "ui_lang": ui_lang,
        "page_type": page_type,
        "profile": profile,
        "skill_roadmap_data": skill_roadmap_data,
    }


def career_guidance_view(request):
    """Career guidance results - AI-ready placeholder data (Gemini optional)."""
    context = build_career_guidance_context(request)
    return render(request, "advisor/career_guidance.html", context)


def career_guidance_pdf_view(request):
    """Generate a PDF download of the current career guidance results."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import os

    context = build_career_guidance_context(request)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="career_guidance_report.pdf"'

    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Try to register Vijaya font for Tamil Unicode support
    vijaya_font_registered = False
    vijaya_font_path = None
    
    # Common paths where Vijaya font might be located
    possible_font_paths = [
        r"C:\Windows\Fonts\Vijaya.ttf",
        r"C:\Windows\Fonts\vijaya.ttf",
        os.path.join(os.path.expanduser("~"), "AppData", "Local", "Microsoft", "Windows", "Fonts", "Vijaya.ttf"),
        os.path.join(settings.BASE_DIR, "static", "fonts", "Vijaya.ttf"),
    ]
    
    for font_path in possible_font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('Vijaya', font_path))
                vijaya_font_registered = True
                vijaya_font_path = font_path
                break
            except Exception:
                continue

    # Basic text settings
    left_margin = 40
    right_margin = 40
    max_width = width - left_margin - right_margin
    
    # Use Vijaya font for Tamil language, Helvetica for English
    is_tamil = context.get("ui_lang") == "ta"
    if is_tamil and vijaya_font_registered:
        font_name = "Vijaya"
        font_size = 14  # Vijaya needs larger size for readability
        line_height = 18
    else:
        font_name = "Helvetica"
        font_size = 11
        line_height = 14
    
    # Fallback message if Tamil font not available
    tamil_font_warning = None
    if is_tamil and not vijaya_font_registered:
        tamil_font_warning = "Tamil font not found. Installing Vijaya font will improve Tamil text rendering."

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

    profile = context.get("profile") or {}
    if profile:
        write_line("Student Profile & Preferences")
        write_line("------------------------------")
        basic_fields = [
            ("Name", profile.get("full_name")),
            ("Age", profile.get("age")),
            ("Gender", profile.get("gender")),
            ("Location", profile.get("location")),
            ("Preferred Language", profile.get("language")),
            ("School Board", profile.get("school_board")),
            ("10th Percentage", profile.get("tenth_percentage")),
            ("12th Stream", profile.get("twelfth_stream")),
            ("12th Specialization", profile.get("twelfth_specialization")),
            ("12th Percentage", profile.get("twelfth_percentage")),
            ("Current Course", profile.get("current_course")),
            ("Subjects", profile.get("subjects")),
            ("Interest Level", profile.get("interest_level")),
            ("Skills", profile.get("skills")),
            ("Strengths", profile.get("strengths")),
            ("Interests", profile.get("interests")),
            ("Other Interest", profile.get("other_interest")),
        ]
        for label, value in basic_fields:
            if value:
                write_line(f"{label}: {value}")
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
            skills = normalize_required_skills(career.get("required_skills"))
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
    AJAX chatbot for profile / preferences pages.
    Expects JSON: {"message": "<user text>"} and returns {"reply": "<ai text>"}.
    Uses GEMINI_API_KEY (Google Gemini) when set.
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

        student_context = ""
        if getattr(request, "user", None) and request.user.is_authenticated:
            sp = StudentProfile.objects.filter(user=request.user).first()
            if sp:
                ctx = {
                    "name": request.user.first_name or request.user.username,
                    "age": sp.age,
                    "location": sp.location,
                    "preferred_language": sp.preferred_language,
                    "school_board": sp.school_board,
                    "subjects": sp.subjects,
                    "interest_level": sp.interest_level,
                    "skills": sp.skills,
                    "strengths": sp.strengths,
                    "interests": sp.interests,
                    "other_interest": sp.other_interest,
                }
                student_context = (
                    "\nThe student has saved this profile (use only if relevant; do not repeat it verbatim):\n"
                    f"{json.dumps(ctx, ensure_ascii=False)}\n"
                )

        prompt = (
            "You are a friendly career guidance chatbot for students.\n"
            "Keep answers short (2–4 sentences) and practical.\n"
            f"{language_instruction}\n"
            f"{student_context}\n"
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


def _history_record_allowed(request, history_item: CareerGuidanceHistory) -> bool:
    """Logged-in users may only open their own rows; guests only session rows."""
    user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
    if user:
        return history_item.user_id == user.id
    if history_item.user_id is not None:
        return False
    if not request.session.session_key:
        request.session.save()
    sk = request.session.session_key or ""
    return bool(sk and history_item.session_key == sk)


def career_history_detail_view(request, pk: int):
    """Full saved guidance result for one history row."""
    item = CareerGuidanceHistory.objects.filter(pk=pk).first()
    if not item or not _history_record_allowed(request, item):
        messages.error(request, "You cannot view this history entry.")
        return redirect("career_history")

    snap = item.full_snapshot or {}
    profile = snap.get("profile") if isinstance(snap.get("profile"), dict) else (item.profile or {})
    career_recommendations = snap.get("career_recommendations") or item.career_recommendations or []
    education_path = snap.get("education_path") if isinstance(snap.get("education_path"), dict) else (item.education_path or {})
    growth_timeline = snap.get("growth_timeline") or item.growth_timeline or []
    ai_error = snap.get("ai_error") if snap.get("ai_error") is not None else (item.ai_error or None)

    ui_lang = normalize_lang(item.ui_lang or get_lang_from_request(request))
    ui = get_ui_strings(ui_lang)

    return render(
        request,
        "advisor/career_history_detail.html",
        {
            "item": item,
            "profile": profile,
            "career_recommendations": career_recommendations,
            "education_path": education_path,
            "growth_timeline": growth_timeline,
            "ai_error": ai_error,
            "ui": ui,
            "ui_lang": ui_lang,
        },
    )


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
