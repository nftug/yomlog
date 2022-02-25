# Generated by Django 3.2.8 on 2022-02-25 08:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_auto_20220201_1755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='books', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='book',
            name='total',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='book',
            name='total_page',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='note',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='statuslog',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='status_log', to=settings.AUTH_USER_MODEL),
        ),
    ]
