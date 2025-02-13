# Generated by Django 5.1.5 on 2025-02-12 21:10

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Help",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="Вид помощи")),
                ("description", models.TextField(verbose_name="Описание методики")),
                ("image", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "duration",
                    models.PositiveIntegerField(verbose_name="Время оказания (мин)"),
                ),
                ("is_deleted", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="CustomUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                ("is_moderator", models.BooleanField(default=False)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to.",
                        related_name="customuser_set",
                        related_query_name="customuser",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="customuser_set",
                        related_query_name="customuser",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Lesion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=100, verbose_name="Вид поражения"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Черновик"),
                            ("formed", "Сформирована"),
                            ("completed", "Завершена"),
                            ("rejected", "Отклонена"),
                            ("deleted", "Удалена"),
                        ],
                        default="draft",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("date_formed", models.DateTimeField(blank=True, null=True)),
                ("date_completed", models.DateTimeField(blank=True, null=True)),
                (
                    "disaster_type",
                    models.CharField(max_length=100, verbose_name="Тип ЧС"),
                ),
                (
                    "total_cost",
                    models.DecimalField(decimal_places=2, default=0, max_digits=10),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="created_lesions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "moderator",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="moderated_lesions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="HelpLesion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "application_order",
                    models.PositiveIntegerField(verbose_name="Порядок применения"),
                ),
                (
                    "notes",
                    models.TextField(blank=True, verbose_name="Особенности применения"),
                ),
                ("quantity", models.PositiveIntegerField(default=1)),
                (
                    "help",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="help_lesions",
                        to="main.help",
                    ),
                ),
                (
                    "lesion",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="help_lesions",
                        to="main.lesion",
                    ),
                ),
            ],
            options={
                "ordering": ["application_order"],
            },
        ),
    ]
