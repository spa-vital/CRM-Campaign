# Generated by Django 5.0 on 2023-12-29 08:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0001_initial'),
        ('team', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('company', models.CharField(blank=True, max_length=100, null=True)),
                ('job', models.CharField(blank=True, max_length=100, null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clients', to=settings.AUTH_USER_MODEL)),
                ('product_line', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clients', to='product.product')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clients', to='team.team')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='ClientFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('file', models.FileField(upload_to='clientfiles')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='client.client')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_files', to=settings.AUTH_USER_MODEL)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_files', to='team.team')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField(null=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='client.client')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_comments', to=settings.AUTH_USER_MODEL)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_comments', to='team.team')),
            ],
        ),
    ]
