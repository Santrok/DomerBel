from django.contrib import admin, auth
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.postgres.fields import ArrayField
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _


# Create your models here.


class CustomUserManager(BaseUserManager):
    """Менеджер модели User.
        Переопределен способ регистрации
         пользователя с username на email."""
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Создает и сохраняет пользователя с указанным адресом электронной почты и паролем.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

    def with_perm(
        self, perm, is_active=True, include_superusers=True, backend=None, obj=None
    ):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    "You have multiple authentication backends configured and "
                    "therefore must provide the `backend` argument."
                )
        elif not isinstance(backend, str):
            raise TypeError(
                "backend must be a dotted import path string (got %r)." % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, "with_perm"):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Модель пользователя"""
    email = models.EmailField(_('email address'), unique=True)
    entity = models.BooleanField('Юридическое лицо', default=False)
    first_name = models.CharField('Контактное лицо', max_length=255)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    phone_number = models.CharField('Номер телефона', max_length=50)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    is_staff = models.BooleanField(_("staff status"),
                                   default=False,
                                   help_text=_("Designates whether the user can log into this admin site."),
                                   )
    is_active = models.BooleanField(_("active"),
                                    default=True,
                                    help_text=_("Designates whether this user should be treated as active. "
                                                "Unselect this instead of deleting accounts."
                                                ),
                                    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    @admin.display
    def set_input(self):
        return format_html(
            "<input type='text'>"
        )

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def check_user_permission_in_group(self):
        """
        Проверяет, принадлежит ли пользователь к группе юридических лиц
        """
        permission = self.groups.filter(name='Юридические лица').exists()
        return permission


class UserFavorites(models.Model):
    """
    Модель хранения избранного пользователя.
    Модели: User(O2O)
    """
    user = models.OneToOneField(get_user_model(), verbose_name="Пользователь", on_delete=models.CASCADE)
    favorites = ArrayField(models.IntegerField(), verbose_name="Список избранного", default=list, blank=True)
    notes_for_favorites = models.JSONField(verbose_name="Список заметок для избранного", default=dict, blank=True)

    class Meta:
        verbose_name = "Избранное пользователя"
        verbose_name_plural = "Избранное пользователя"

    def __str__(self):
        return f'Избранное для {self.user}'


class UserFavoritesAdmin(admin.ModelAdmin):
    """
    Класс управления отображения в админ панели сущности: UserFavorites
    """
    pass
