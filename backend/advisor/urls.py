"""
URL routing for advisor app.
"""

from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("verify-otp/", views.verify_otp_view, name="verify_otp"),
    path("profile-analysis/", views.profile_analysis_view, name="profile_analysis"),
    path("career-guidance/", views.career_guidance_view, name="career_guidance"),  # default (work view)
    path("career-guidance/work/", views.career_guidance_view, name="career_guidance_work"),
    path("career-guidance/education/", views.career_guidance_view, name="career_guidance_education"),
    path("career-guidance/report/pdf/", views.career_guidance_pdf_view, name="career_guidance_pdf"),
    path("career-history/", views.career_history_view, name="career_history"),
    path("chatbot/", views.chatbot_view, name="chatbot"),
]
