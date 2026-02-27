"""
URL routing for advisor app.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('profile-analysis/', views.profile_analysis_view, name='profile_analysis'),
    path('career-guidance/', views.career_guidance_view, name='career_guidance'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
]
