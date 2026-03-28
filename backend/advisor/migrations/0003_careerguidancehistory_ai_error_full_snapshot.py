from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("advisor", "0002_studentprofile"),
    ]

    operations = [
        migrations.AddField(
            model_name="careerguidancehistory",
            name="ai_error",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="careerguidancehistory",
            name="full_snapshot",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
