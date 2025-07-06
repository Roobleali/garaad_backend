from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0005_user_referral_code_user_referral_points_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_active',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ] 