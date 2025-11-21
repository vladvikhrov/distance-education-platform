from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, login, password, **extra_fields):
        """
        Creates and saves a User with the given login and password.
        """
        if not login:
            raise ValueError('The given login must be set')
        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, login, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(login, password, **extra_fields)

    def create_superuser(self, login, password, **extra_fields):

        if not extra_fields.get('first_name'):
            raise ValueError('Superuser must have first_name')
        if not extra_fields.get('last_name'):
            raise ValueError('Superuser must have last_name')
        if not extra_fields.get('patronymic'):
            raise ValueError('Superuser must have patronymic')
        
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'A')
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self._create_user(login, password, **extra_fields)