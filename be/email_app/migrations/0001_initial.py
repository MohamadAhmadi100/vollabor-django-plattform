# Generated by Django 3.2.4 on 2022-07-15 19:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, null=True)),
                ('slug', models.SlugField(max_length=400, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('visible', 'Visible'), ('deleted', 'Deleted')], default='visible', max_length=10, null=True)),
                ('last_editor', models.TextField(default=',', null=True)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_category_template', to=settings.AUTH_USER_MODEL)),
                ('deletor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deletor_category_template', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=200)),
                ('state', models.CharField(max_length=200)),
                ('city', models.CharField(max_length=200)),
                ('street_number', models.CharField(max_length=200)),
                ('building_number', models.CharField(max_length=200)),
                ('unit', models.CharField(max_length=200)),
                ('zip_code', models.CharField(max_length=200)),
                ('size', models.CharField(max_length=200)),
                ('company_website_link', models.CharField(max_length=200)),
                ('outsource', models.TextField(null=True)),
                ('services', models.TextField(null=True)),
                ('products', models.TextField(null=True)),
                ('current_need', models.TextField(null=True)),
                ('future_need', models.TextField(null=True)),
                ('last_editor', models.TextField(default=',', null=True)),
                ('deleted_user', models.CharField(max_length=200, null=True)),
                ('status', models.CharField(choices=[('visible', 'Visible'), ('deleted', 'Deleted')], default='visible', max_length=10, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='HistorySendEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('template_name', models.TextField()),
                ('subject', models.CharField(max_length=100)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='users_send', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SendEmailProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(null=True)),
                ('img', models.ImageField(blank=True, null=True, upload_to='email/img/')),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UploadImg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, null=True)),
                ('img', models.FileField(blank=True, null=True, upload_to='email/img/')),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='TemplateEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(null=True)),
                ('title', models.CharField(max_length=200, null=True)),
                ('img', models.ImageField(blank=True, null=True, upload_to='email/template/img')),
                ('template', models.FileField(blank=True, null=True, upload_to='email/template')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('visible', 'Visible'), ('deleted', 'Deleted')], default='visible', max_length=10, null=True)),
                ('last_editor', models.TextField(default=',', null=True)),
                ('categories', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='category_template', to='email_app.categorytemplate')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_template', to=settings.AUTH_USER_MODEL)),
                ('deletor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deletor_template', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SendEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=100, null=True)),
                ('sent', models.BooleanField(default=False, null=True)),
                ('history', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='history_emails', to='email_app.historysendemail')),
            ],
        ),
        migrations.CreateModel(
            name='ReminderEmails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=200, null=True)),
                ('text', models.CharField(max_length=200, null=True)),
                ('send_date', models.DateTimeField(null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('emaillist', models.CharField(max_length=70000, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Institute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institute_name', models.CharField(max_length=200)),
                ('location', models.CharField(max_length=200)),
                ('web_address', models.CharField(max_length=200)),
                ('last_editor', models.TextField(default=',', null=True)),
                ('status', models.CharField(choices=[('visible', 'Visible'), ('deleted', 'Deleted')], default='visible', max_length=10, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('country', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='country_institute', to='email_app.country')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_institute', to=settings.AUTH_USER_MODEL)),
                ('deletor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deletor_institute', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EmailsInstitute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=200, null=True)),
                ('position', models.CharField(max_length=200, null=True)),
                ('degree', models.CharField(max_length=200, null=True)),
                ('gender', models.CharField(choices=[('Female', 'Female'), ('Male', 'Male')], max_length=6, null=True, verbose_name='Gender')),
                ('email_address', models.EmailField(max_length=200, null=True)),
                ('laboratory_website', models.CharField(max_length=200, null=True)),
                ('google_scholar', models.CharField(max_length=200, null=True)),
                ('department', models.CharField(max_length=200, null=True)),
                ('last_editor', models.TextField(blank=True, default=',', null=True)),
                ('status', models.CharField(choices=[('visible', 'Visible'), ('deleted', 'Deleted')], default='visible', max_length=10, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('linkdin', models.CharField(max_length=200, null=True)),
                ('linkdin_nick', models.CharField(max_length=200, null=True)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_email_institute', to=settings.AUTH_USER_MODEL)),
                ('deletor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deletor_email_institute', to=settings.AUTH_USER_MODEL)),
                ('institute', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='emails_institute', to='email_app.institute')),
            ],
        ),
        migrations.CreateModel(
            name='Emails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_agent_first_name', models.CharField(max_length=200, null=True)),
                ('company_agent_surname', models.CharField(max_length=200, null=True)),
                ('agent_position', models.CharField(max_length=200, null=True)),
                ('agent_academic_degree', models.CharField(max_length=200, null=True)),
                ('gender', models.CharField(choices=[('Female', 'Female'), ('Male', 'Male')], max_length=6, null=True, verbose_name='Gender')),
                ('agent_email_address', models.EmailField(max_length=200, null=True)),
                ('last_editor', models.TextField(blank=True, default=',', null=True)),
                ('deleted_user', models.CharField(blank=True, max_length=200, null=True)),
                ('status', models.CharField(choices=[('visible', 'Visible'), ('deleted', 'Deleted')], default='visible', max_length=10, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='company_email', to='email_app.company')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_email', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DepartmentInstitu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('approove', models.BooleanField(default=False, null=True)),
                ('created', models.DateField(auto_now_add=True)),
                ('viwed', models.BooleanField(default=False, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CompanySocialMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('link', models.CharField(max_length=200)),
                ('company', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='CompanySocialMedia_compony', to='email_app.company')),
            ],
        ),
        migrations.AddField(
            model_name='company',
            name='country',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='country_compony', to='email_app.country'),
        ),
        migrations.AddField(
            model_name='company',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_company', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='category_compony', to='email_app.company')),
            ],
        ),
        migrations.CreateModel(
            name='AdRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_company', models.BooleanField(blank=True, default=False, verbose_name='Create company')),
                ('edit_delete_company', models.BooleanField(blank=True, default=False, verbose_name='Edit, delete compnay')),
                ('create_category', models.BooleanField(blank=True, default=False, verbose_name='Create category')),
                ('create_email', models.BooleanField(blank=True, default=False, verbose_name='Create email')),
                ('edit_delete_email', models.BooleanField(blank=True, default=False, verbose_name='Edit, delete email')),
                ('create_template', models.BooleanField(blank=True, default=False, verbose_name='Create template')),
                ('edit_delete_template', models.BooleanField(blank=True, default=False, verbose_name='Edit, delete template')),
                ('create_template_category', models.BooleanField(blank=True, default=False, verbose_name='Create category template')),
                ('edit_delete_template_category', models.BooleanField(blank=True, default=False, verbose_name='Edit, delete category template')),
                ('send_email', models.BooleanField(blank=True, default=False, verbose_name='Send email')),
                ('send_email_template', models.BooleanField(blank=True, default=False, verbose_name='Send email template')),
                ('upload_image', models.BooleanField(blank=True, default=False, verbose_name='Upload image')),
                ('research_workshop_projects', models.BooleanField(blank=True, default=False, verbose_name='Research & Workshop projects')),
                ('create_institute', models.BooleanField(blank=True, default=False, verbose_name='Create institute')),
                ('edit_delete_institute', models.BooleanField(blank=True, default=False, verbose_name='Edit, delete institute')),
                ('create_email_institute', models.BooleanField(blank=True, default=False, verbose_name='Create email institute')),
                ('edit_delete_email_institute', models.BooleanField(blank=True, default=False, verbose_name='Edit, delete email institute')),
                ('Director', models.BooleanField(blank=True, default=False, verbose_name='aprrove departments')),
                ('is_staff', models.BooleanField(blank=True, default=False, verbose_name='Is staff')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
