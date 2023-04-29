# Generated by Django 4.1.5 on 2023-04-24 18:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('web', '0015_delete_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_x', models.IntegerField(default=1)),
                ('address_y', models.IntegerField(default=1)),
                ('pack_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.CharField(default='processing', max_length=50)),
                ('ups_username', models.CharField(blank=True, default='', max_length=50)),
                ('count', models.IntegerField(default=1)),
                ('is_processed', models.BooleanField(default=False)),
                ('is_packed', models.BooleanField(default=False)),
                ('is_loaded', models.BooleanField(default=False)),
                ('is_delivered', models.BooleanField(default=False)),
                ('generate_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('truck_id', models.IntegerField(default=-1)),
                ('is_truck_requested', models.BooleanField(default=False)),
                ('is_truck_arrived', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='packages', to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='web.product')),
                ('warehouse', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='packages', to='web.warehouse')),
            ],
        ),
    ]
