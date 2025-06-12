from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(default='USD', max_length=3)),
                ('payment_type', models.CharField(choices=[('local', 'Local'), ('diaspora', 'Diaspora')], default='local', max_length=20)),
                ('transaction_id', models.CharField(max_length=100, unique=True)),
                ('waafipay_reference', models.CharField(blank=True, max_length=100, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('refunded', 'Refunded')], default='pending', max_length=20)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='accounts.user')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=False)),
                ('start_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('auto_renew', models.BooleanField(default=True)),
                ('subscription_type', models.CharField(choices=[('local', 'Local'), ('diaspora', 'Diaspora')], default='local', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='subscription', to='accounts.user')),
            ],
        ),
    ] 