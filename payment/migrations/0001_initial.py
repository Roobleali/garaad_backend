# Generated manually for payment app

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('order_number', models.CharField(max_length=50, unique=True)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(choices=[('USD', 'US Dollar'), ('EUR', 'Euro'), ('SOS', 'Somali Shilling')], default='USD', max_length=3)),
                ('payment_method', models.CharField(choices=[('waafi', 'Waafi'), ('zaad', 'Zaad'), ('evcplus', 'EVCPlus'), ('sahal', 'Sahal'), ('credit_card', 'Credit Card'), ('bank_account', 'Bank Account'), ('admin', 'Admin')], max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled'), ('refunded', 'Refunded')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('waafi_transaction_id', models.CharField(blank=True, max_length=100, null=True)),
                ('waafi_reference_id', models.CharField(blank=True, max_length=100, null=True)),
                ('waafi_issuer_transaction_id', models.CharField(blank=True, max_length=100, null=True)),
                ('waafi_order_id', models.CharField(blank=True, max_length=100, null=True)),
                ('metadata', models.JSONField(default=dict)),
                ('customer_name', models.CharField(blank=True, max_length=255, null=True)),
                ('customer_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('customer_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('description', models.TextField(blank=True)),
                ('internal_notes', models.TextField(blank=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PaymentWebhook',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('provider', models.CharField(max_length=50)),
                ('event_type', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('received', 'Received'), ('processed', 'Processed'), ('failed', 'Failed'), ('duplicate', 'Duplicate')], default='received', max_length=20)),
                ('raw_data', models.JSONField()),
                ('processed_data', models.JSONField(default=dict)),
                ('processed_at', models.DateTimeField(blank=True, null=True)),
                ('error_message', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payment.order')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_type', models.CharField(choices=[('subscription', 'Subscription'), ('feature', 'Feature'), ('course', 'Course'), ('other', 'Other')], max_length=20)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subscription_type', models.CharField(blank=True, max_length=20, null=True)),
                ('subscription_start_date', models.DateTimeField(blank=True, null=True)),
                ('subscription_end_date', models.DateTimeField(blank=True, null=True)),
                ('metadata', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='payment.order')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='paymentwebhook',
            index=models.Index(fields=['provider', 'event_type'], name='payment_pay_provide_ac8b6b_idx'),
        ),
        migrations.AddIndex(
            model_name='paymentwebhook',
            index=models.Index(fields=['status'], name='payment_pay_status_c2e7a3_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['user', '-created_at'], name='payment_ord_user_id_0a6b7b_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['status'], name='payment_ord_status_7c8b7f_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['waafi_transaction_id'], name='payment_ord_waafi_t_8b4c9e_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['waafi_reference_id'], name='payment_ord_waafi_r_5d2e8a_idx'),
        ),
    ] 