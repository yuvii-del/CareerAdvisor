"""
Very lightweight i18n layer (English / Tamil) for templates.

Why this approach:
- No heavy Django .po translation workflow needed right now
- Works well for a small, fixed set of UI strings
- Session-based language preference (set on /login/)
"""

SUPPORTED_LANGS = ("en", "ta")
DEFAULT_LANG = "en"


UI_STRINGS = {
    "en": {
        # Global
        "platform_name": "Career & Educational Advisor",
        "back_to_login": "← Back to Login",
        # Login
        "login_title": "Career & Educational Advisor",
        "email_or_username": "Email / Username",
        "enter_email_or_username": "Enter your email or username",
        "password": "Password",
        "enter_password": "Enter your password",
        "login": "Login",
        "continue_guest": "Continue as Guest",
        "forgot_password": "Forgot Password",
        "forgot_password_title": "Reset your password",
        "forgot_password_instructions": "Enter your email and we'll send you a link to reset your password.",
        "send_reset_link": "Send reset link",
        "reset_email_sent": "If an account exists with that email, we've sent password reset instructions.",
        "set_new_password": "Set new password",
        "new_password": "New password",
        "confirm_password_label": "Confirm new password",
        "reset_password_btn": "Reset password",
        "reset_complete_title": "Password reset complete",
        "reset_complete_message": "Your password has been set. You can now log in.",
        "create_account": "Create Account",
        "ui_language": "UI Language",
        "english": "English",
        "tamil": "Tamil",
        "hero_title": "Welcome to the Personalized Career and Educational Advisor Platform",
        "hero_subtitle": "Start your career with a great vision.",
        # Profile analysis
        "profile_analysis": "Profile Analysis",
        "profile_subtitle": "Help us understand you better to provide personalized career guidance",
        "basic_details": "Basic Details",
        "educational_details": "Educational Details",
        "full_name": "Full Name",
        "age": "Age",
        "gender": "Gender",
        "select_gender": "Select Gender",
        "male": "Male",
        "female": "Female",
        "other": "Other",
        "prefer_not_to_say": "Prefer not to say",
        "city_state": "City / State",
        "location_placeholder": "e.g., Chennai, Tamil Nadu",
        "preferred_language": "Preferred Language",
        "select_language": "Select Language",
        "both": "Both",
        "career_interest_level": "Career Interest Level",
        "select_level": "Select Level",
        "beginner": "Beginner",
        "exploring": "Exploring",
        "focused": "Focused",
        "next_educational": "Next: Educational Details",
        "back": "Back",
        "school_board": "School Board",
        "select_board": "Select Board",
        "tenth_percentage": "10th Percentage",
        "tenth_placeholder": "e.g., 85.5",
        "twelfth_stream": "12th Stream",
        "select_stream": "Select Stream",
        "science": "Science",
        "commerce": "Commerce",
        "arts": "Arts",
        "twelfth_specialization": "12th Specialization",
        "select_specialization": "Select Specialization",
        "twelfth_percentage": "12th Percentage",
        "twelfth_placeholder": "e.g., 88.5",
        "current_course": "Current Degree / Course",
        "current_course_placeholder": "e.g., B.Tech Computer Science",
        "subjects_multiselect": "Favourite School Subjects (multi-select)",
        "skills_multiselect": "Skills (multi-select)",
        "strengths_multiselect": "Strengths (Logical / Creative / Communication / Leadership)",
        "interests_multiselect": "Areas of Interest (AI, Web Dev, Medicine, Business, Govt Jobs, etc.)",
        "other_interest": "Any other area of interest",
        "other_interest_placeholder": "e.g. Gaming, Sports, Law, Journalism...",
        "analyze_profile": "Analyze My Profile",
        "analyzing": "Analyzing...",
        # Career guidance
        "results_title": "Your Career Guidance Results",
        "results_subtitle": "Based on your profile, here are personalized career recommendations",
        "ai_unavailable_title": "AI is not available right now",
        "ai_unavailable_subtitle": "Showing fallback results.",
        "match_score": "Match Score",
        "why_suits": "Why This Career Suits You",
        "required_skills": "Required Skills",
        "suggested_learning_path": "Suggested Learning Path",
        "education_learning_path": "📚 Education & Learning Path",
        "recommended_degrees": "Recommended Degrees",
        "formal_paths": "Formal education paths to consider:",
        "online_certifications": "Online Certifications",
        "boost_skills": "Boost your skills with these courses:",
        "skill_development": "Skill Development",
        "focus_areas": "Focus areas for growth:",
        "skill_roadmap": "Skill Roadmap",
        "roadmap_beginner": "Beginner",
        "roadmap_beginner_desc": "Learn fundamentals, basic programming, and core concepts",
        "roadmap_beginner_bullets": (
            "Learn fundamentals",
            "Basic programming",
            "Core concepts",
        ),
        "roadmap_intermediate": "Intermediate",
        "roadmap_intermediate_desc": "Build projects, learn frameworks, and gain practical experience",
        "roadmap_intermediate_bullets": (
            "Build real projects",
            "Frameworks and industry tools",
            "Internships or team experience",
        ),
        "roadmap_advanced": "Advanced",
        "roadmap_advanced_desc": "Specialize, contribute to open source, and mentor others",
        "roadmap_advanced_bullets": (
            "Deep specialization",
            "Open source and complex systems",
            "Mentor and lead technically",
        ),
        "growth_timeline": " Career Growth Timeline",
        "download_report": "Download Career Report",
        "explore_another": " Explore Another Career Path",
        "update_profile": " Update Profile",
        "download_soon": "Career Report download feature will be available soon!",
        # History
        "view_history": " View History",
        "history_title": "Recent Career Guidance History",
        "history_subtitle": "Review the latest career guidance results generated for you.",
        "no_history": "No history yet",
        "no_history_subtitle": "Generate your first career guidance result to see it here.",
    },
    "ta": {
        # Global
        "platform_name": "தொழில் & கல்வி ஆலோசகர்",
        "back_to_login": "← உள்நுழைவு பக்கத்திற்கு திரும்ப",
        # Login
        "login_title": "தொழில் & கல்வி ஆலோசகர்",
        "email_or_username": "மின்னஞ்சல் / பயனர் பெயர்",
        "enter_email_or_username": "உங்கள் மின்னஞ்சல் அல்லது பயனர் பெயரை உள்ளிடுங்கள்",
        "password": "கடவுச்சொல்",
        "enter_password": "உங்கள் கடவுச்சொல்லை உள்ளிடுங்கள்",
        "login": "உள்நுழைவு",
        "continue_guest": "விருந்தினராக தொடருங்கள்",
        "forgot_password": "கடவுச்சொல் மறந்துவிட்டதா?",
        "forgot_password_title": "கடவுச்சொல்லை மீட்டமைக்கவும்",
        "forgot_password_instructions": "உங்கள் மின்னஞ்சலை உள்ளிடுங்கள்; கடவுச்சொல்லை மீட்டமைக்க இணைப்பு அனுப்புவோம்.",
        "send_reset_link": "மீட்டமைப்பு இணைப்பு அனுப்பு",
        "reset_email_sent": "அந்த மின்னஞ்சலுடன் கணக்கு இருந்தால், கடவுச்சொல் மீட்டமைப்பு வழிமுறைகளை அனுப்பியுள்ளோம்.",
        "set_new_password": "புதிய கடவுச்சொல்லை அமைக்கவும்",
        "new_password": "புதிய கடவுச்சொல்",
        "confirm_password_label": "புதிய கடவுச்சொல்லை உறுதிசெய்",
        "reset_password_btn": "கடவுச்சொல்லை மீட்டமைக்கவும்",
        "reset_complete_title": "கடவுச்சொல் மீட்டமைப்பு முடிந்தது",
        "reset_complete_message": "உங்கள் கடவுச்சொல் அமைக்கப்பட்டது. இப்போது உள்நுழையலாம்.",
        "create_account": "புதிய கணக்கு உருவாக்கு",
        "ui_language": "மொழி (UI)",
        "english": "ஆங்கிலம்",
        "tamil": "தமிழ்",
        "hero_title": "தனிப்பயன் தொழில் மற்றும் கல்வி ஆலோசகர் தளத்திற்கு வரவேற்கிறோம்",
        "hero_subtitle": "சிறந்த பார்வையுடன் உங்கள் பயணத்தை தொடங்குங்கள்.",
        # Profile analysis
        "profile_analysis": "சுயவிவர பகுப்பாய்வு",
        "profile_subtitle": "உங்களுக்கு ஏற்புடைய தொழில் ஆலோசனையை வழங்க உங்கள் தகவலை பகிருங்கள்",
        "basic_details": "அடிப்படை விவரங்கள்",
        "educational_details": "கல்வி விவரங்கள்",
        "full_name": "முழுப் பெயர்",
        "age": "வயது",
        "gender": "பாலினம்",
        "select_gender": "பாலினத்தைத் தேர்வு செய்க",
        "male": "ஆண்",
        "female": "பெண்",
        "other": "மற்றவை",
        "prefer_not_to_say": "சொல்ல விரும்பவில்லை",
        "city_state": "நகரம் / மாநிலம்",
        "location_placeholder": "உதா., சென்னை, தமிழ்நாடு",
        "preferred_language": "விருப்பமான மொழி",
        "select_language": "மொழியைத் தேர்வு செய்க",
        "both": "இரண்டும்",
        "career_interest_level": "தொழில் ஆர்வ நிலை",
        "select_level": "நிலையைத் தேர்வு செய்க",
        "beginner": "தொடக்க நிலை",
        "exploring": "ஆராயும் நிலை",
        "focused": "கவனம் செலுத்தும் நிலை",
        "next_educational": "அடுத்து: கல்வி விவரங்கள்",
        "back": "திரும்ப",
        "school_board": "பள்ளி கல்வி வாரியம்",
        "select_board": "வாரியத்தைத் தேர்வு செய்க",
        "tenth_percentage": "10ஆம் வகுப்பு சதவீதம்",
        "tenth_placeholder": "உதா., 85.5",
        "twelfth_stream": "12ஆம் வகுப்பு பிரிவு",
        "select_stream": "பிரிவைத் தேர்வு செய்க",
        "science": "அறிவியல்",
        "commerce": "வர்த்தகம்",
        "arts": "கலை",
        "twelfth_specialization": "12ஆம் வகுப்பு சிறப்புப்பிரிவு",
        "select_specialization": "சிறப்புப்பிரிவைத் தேர்வு செய்க",
        "twelfth_percentage": "12ஆம் வகுப்பு சதவீதம்",
        "twelfth_placeholder": "உதா., 88.5",
        "current_course": "தற்போதைய பட்டம் / பாடநெறி",
        "current_course_placeholder": "உதா., B.Tech கணினி அறிவியல்",
        "subjects_multiselect": "விருப்பமான பாடங்கள் (பல தேர்வு)",
        "skills_multiselect": "திறன்கள் (பல தேர்வு)",
        "strengths_multiselect": "வலுவுகள் (தர்க்கம் / படைப்பாற்றல் / தொடர்பாடல் / தலைமைத்துவம்)",
        "interests_multiselect": "ஆர்வத் துறைகள் (AI, Web Dev, Medicine, Business, Govt Jobs, போன்றவை)",
        "other_interest": "வேறு ஆர்வத் துறை",
        "other_interest_placeholder": "உதா. கேமிங், விளையாட்டு, சட்டம், பத்திரிகை...",
        "analyze_profile": "என் சுயவிவரத்தை பகுப்பாய்வு செய்க",
        "analyzing": "பகுப்பாய்வு செய்யப்படுகிறது...",
        # Career guidance
        "results_title": "உங்கள் தொழில் ஆலோசனை முடிவுகள்",
        "results_subtitle": "உங்கள் சுயவிவரத்தின் அடிப்படையில் தனிப்பயன் பரிந்துரைகள்",
        "ai_unavailable_title": "இப்போது AI கிடைக்கவில்லை",
        "ai_unavailable_subtitle": "மாற்று (fallback) முடிவுகள் காட்டப்படுகின்றன.",
        "match_score": "பொருத்த மதிப்பெண்",
        "why_suits": "ஏன் இது உங்களுக்கு பொருந்தும்",
        "required_skills": "தேவையான திறன்கள்",
        "suggested_learning_path": "பரிந்துரைக்கப்படும் கற்றல் பாதை",
        "education_learning_path": "📚 கல்வி & கற்றல் பாதை",
        "recommended_degrees": "பரிந்துரைக்கப்படும் பட்டங்கள்",
        "formal_paths": "கருத்தில் கொள்ள வேண்டிய கல்விப் பாதைகள்:",
        "online_certifications": "ஆன்லைன் சான்றிதழ்கள்",
        "boost_skills": "இந்த பாடநெறிகளால் திறன்களை மேம்படுத்துங்கள்:",
        "skill_development": "திறன் வளர்ச்சி",
        "focus_areas": "வளர்ச்சிக்கான கவனம் துறைகள்:",
        "skill_roadmap": "திறன் சாலைவரைபடம்",
        "roadmap_beginner": "தொடக்க நிலை",
        "roadmap_beginner_desc": "அடிப்படைகள், தொடக்க நிரலாக்கம் மற்றும் முக்கிய கருத்துகள்",
        "roadmap_beginner_bullets": (
            "அடிப்படைகளைக் கற்றுக்கொள்ளுங்கள்",
            "அடிப்படை நிரலாக்கம் செய்யுங்கள்",
            "முக்கிய கருத்துகளைப் புரிந்து கொள்ளுங்கள்",
        ),
        "roadmap_intermediate": "இடைநிலை நிலை",
        "roadmap_intermediate_desc": "திட்டங்களை உருவாக்குங்கள், கருவிகளைப் பயன்படுத்துங்கள், அனுபவம் பெறுங்கள்",
        "roadmap_intermediate_bullets": (
            "நிஜத் திட்டங்களைச் செய்யுங்கள்",
            "தொழில்நுட்பக் கருவிகளைக் கற்றுக்கொள்ளுங்கள்",
            "பயிற்சி அல்லது குழு அனுபவம் பெறுங்கள்",
        ),
        "roadmap_advanced": "மேம்பட்ட நிலை",
        "roadmap_advanced_desc": "சிறப்புப் புலத்தில் ஆழமாகப் படியுங்கள், சிக்கலான அமைப்புகளைக் கையாளுங்கள்",
        "roadmap_advanced_bullets": (
            "ஆழமான சிறப்புப் பயிற்சி",
            "திறந்த மூல மற்றும் பெரிய அமைப்புகள்",
            "வழிகாட்டுதல் மற்றும் தலைமை ஏற்குதல்",
        ),
        "growth_timeline": "தொழில் வளர்ச்சி நேரக்கோடு",
        "download_report": "தொழில் அறிக்கையைப் பதிவிறக்குக",
        "explore_another": "வேறொரு தொழில் பாதையை ஆராய்க",
        "update_profile": "சுயவிவரத்தைப் புதுப்பிக்க",
        "download_soon": "தொழில் அறிக்கை பதிவிறக்க வசதி விரைவில்!",
        # History
        "view_history": " வரலாற்றைப் பார்க்கவும்",
        "history_title": "சமீபத்திய தொழில் ஆலோசனை வரலாறு",
        "history_subtitle": "உங்களுக்கு உருவாக்கப்பட்ட சமீபத்திய தொழில் ஆலோசனை முடிவுகளை இங்கு பார்க்கலாம்.",
        "no_history": "இன்னும் வரலாறு இல்லை",
        "no_history_subtitle": "முதற்கண் தொழில் ஆலோசனை முடிவை உருவாக்கி இங்கு பார்க்கவும்.",
        # Chatbot
        "chatbot_open": "Career chat",
        "chatbot_you": "நீங்கள்:",
        "chatbot_bot": "Bot:",
        "chatbot_typing": "Bot எழுதுகிறது...",
        "chatbot_error": "AI உரையாடலில் பிழை. பின்னர் முயற்சிக்கவும்.",
    },
}


def normalize_lang(value: str | None) -> str:
    if not value:
        return DEFAULT_LANG
    value = value.strip().lower()
    if value in ("ta", "tamil"):
        return "ta"
    if value in ("en", "english", "en-us", "en_us"):
        return "en"
    return DEFAULT_LANG


def get_lang_from_request(request) -> str:
    # Priority: session -> querystring -> default
    session_lang = request.session.get("ui_lang")
    if session_lang:
        return normalize_lang(session_lang)
    q_lang = request.GET.get("lang")
    if q_lang:
        return normalize_lang(q_lang)
    return DEFAULT_LANG


def get_ui_strings(lang: str) -> dict:
    lang = normalize_lang(lang)
    return UI_STRINGS.get(lang, UI_STRINGS[DEFAULT_LANG])

