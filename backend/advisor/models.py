from django.conf import settings
from django.db import models
from django.utils import timezone


class EmailOTP(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_otps",
    )
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"OTP for {self.user} ({self.code})"

    @property
    def is_expired(self) -> bool:
        # OTP valid for 10 minutes
        return self.created_at < timezone.now() - timezone.timedelta(minutes=10)


class CareerGuidanceHistory(models.Model):
    """
    Stores a snapshot of generated career guidance so we can show
    a recent history page for each user or browser session.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="career_guidance_history",
    )
    # Fallback for guests – ties history to the browser session.
    session_key = models.CharField(max_length=40, blank=True)

    ui_lang = models.CharField(max_length=5, default="en")

    profile = models.JSONField(default=dict, blank=True)
    career_recommendations = models.JSONField(default=list, blank=True)
    education_path = models.JSONField(default=dict, blank=True)
    growth_timeline = models.JSONField(default=list, blank=True)

    # Optional: AI failure message when Gemini was used but errored.
    ai_error = models.TextField(blank=True)
    # Complete snapshot for history detail view and auditing (mirrors main fields + meta).
    full_snapshot = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        if self.user:
            return f"Career guidance for {self.user} at {self.created_at}"
        return f"Career guidance (guest) at {self.created_at}"


class StudentProfile(models.Model):
    """
    Persistent user details captured during signup so students
    do not need to re-enter the same information each session.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )

    age = models.PositiveSmallIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=120, blank=True)
    preferred_language = models.CharField(max_length=20, blank=True)

    school_board = models.CharField(max_length=40, blank=True)
    tenth_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    twelfth_stream = models.CharField(max_length=40, blank=True)
    twelfth_specialization = models.CharField(max_length=80, blank=True)
    twelfth_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    current_course = models.CharField(max_length=120, blank=True)
    subjects = models.CharField(max_length=255, blank=True)

    # Preferences that can be updated on preferences page.
    interest_level = models.CharField(max_length=30, blank=True)
    skills = models.CharField(max_length=255, blank=True)
    strengths = models.CharField(max_length=255, blank=True)
    interests = models.CharField(max_length=255, blank=True)
    other_interest = models.CharField(max_length=255, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Student profile for {self.user}"

