# Generated by Django 3.2.4 on 2022-06-29 19:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum', '0002_auto_20220629_2016'),
    ]

    operations = [
        migrations.CreateModel(
            name='ViewTopic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('true', 'true'), ('false', 'false')], default='true', max_length=50, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('topic', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='view_topic', to='forum.postes')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='view_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('true', 'true'), ('false', 'false')], default='true', max_length=50, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('comment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='like_comment', to='forum.postes')),
                ('replycomment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='like_replycomment', to='forum.postes')),
                ('topic', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='like_topic', to='forum.postes')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='like_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DisLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('true', 'true'), ('false', 'false')], default='true', max_length=50, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('comment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dislike_comment', to='forum.postes')),
                ('replycomment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dislike_replycomment', to='forum.postes')),
                ('topic', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dislike_topic', to='forum.postes')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dislike_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]