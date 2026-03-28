"""
URL routing for advisor app.
"""

from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("verify-otp/", views.verify_otp_view, name="verify_otp"),
    path(
        "password-reset/",
        views.PasswordResetView.as_view(
            template_name="advisor/password_reset_form.html",
            email_template_name="advisor/password_reset_email.html",
            success_url=reverse_lazy("password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        views.password_reset_done_view,
        name="password_reset_done",
    ),
    path(
        "password-reset/confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="advisor/password_reset_confirm.html",
            success_url=reverse_lazy("password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="advisor/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
    path("profile-analysis/", views.profile_analysis_view, name="profile_analysis"),
    path("preferences/", views.preferences_view, name="preferences"),
    path("profile/edit/", views.edit_profile_view, name="edit_profile"),
    path("career-guidance/", views.career_guidance_view, name="career_guidance"),  # default (work view)
    path("career-guidance/work/", views.career_guidance_view, name="career_guidance_work"),
    path("career-guidance/education/", views.career_guidance_view, name="career_guidance_education"),
    path("career-guidance/report/pdf/", views.career_guidance_pdf_view, name="career_guidance_pdf"),
    path("career-history/", views.career_history_view, name="career_history"),
    path("career-history/<int:pk>/", views.career_history_detail_view, name="career_history_detail"),
    path("chatbot/", views.chatbot_view, name="chatbot"),
]
