from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("advisor", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("age", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("gender", models.CharField(blank=True, max_length=30)),
                ("location", models.CharField(blank=True, max_length=120)),
                ("preferred_language", models.CharField(blank=True, max_length=20)),
                ("school_board", models.CharField(blank=True, max_length=40)),
                ("tenth_percentage", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ("twelfth_stream", models.CharField(blank=True, max_length=40)),
                ("twelfth_specialization", models.CharField(blank=True, max_length=80)),
                ("twelfth_percentage", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ("current_course", models.CharField(blank=True, max_length=120)),
                ("subjects", models.CharField(blank=True, max_length=255)),
                ("interest_level", models.CharField(blank=True, max_length=30)),
                ("skills", models.CharField(blank=True, max_length=255)),
                ("strengths", models.CharField(blank=True, max_length=255)),
                ("interests", models.CharField(blank=True, max_length=255)),
                ("other_interest", models.CharField(blank=True, max_length=255)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
