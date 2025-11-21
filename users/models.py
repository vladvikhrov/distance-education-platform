from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import gettext_lazy as _

from edu.models import Classes, Subjects

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    CHOICES_ROLE = (
    ('S', 'Ученик'),
    ('T', 'Учитель'),
    ('A', 'Администратор'),
    )
    login = models.CharField(_('Логин'), max_length=18, unique=True)
    email = models.EmailField(_('Почта'), max_length=28, blank=True)
    first_name = models.CharField(_('Имя'), max_length=30)
    last_name = models.CharField(_('Фамилия'), max_length=30)
    patronymic = models.CharField(_('Отчество'), max_length=30, blank=True)
    classes_id = models.ForeignKey(Classes, related_name=_('Класс'),
                                   on_delete=models.CASCADE, verbose_name=_('Доступы к классу'),
                                   blank=True, null=True)
    subjects_id = models.ManyToManyField(Subjects, verbose_name=_('Доступы к предметам'), blank=True)
    is_active = models.BooleanField(_('Активный'), default=True)
    role = models.CharField(_('Роль'), max_length=8, choices=CHOICES_ROLE, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'patronymic'] 

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ["last_name"]

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s %s' % (self.first_name, self.last_name, self.patronymic)
        return full_name.strip()
    
    @property
    def is_staff(self):
        return self.is_superuser

    objects = UserManager()