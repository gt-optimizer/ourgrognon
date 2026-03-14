from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):

    def create_user(self, email, pseudo, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, pseudo=pseudo, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, pseudo, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, pseudo, password, **extra_fields)


class User(AbstractUser):
    username = None
    objects = UserManager()
    email = models.EmailField(unique=True, verbose_name="Adresse email")
    pseudo = models.CharField(max_length=50, unique=True, verbose_name="Pseudo")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['pseudo']

    class Meta:
        verbose_name = "Membre"
        verbose_name_plural = "Membres"

    def __str__(self):
        return self.pseudo