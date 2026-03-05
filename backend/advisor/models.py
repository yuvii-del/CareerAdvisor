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

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        if self.user:
            return f"Career guidance for {self.user} at {self.created_at}"
        return f"Career guidance (guest) at {self.created_at}"

