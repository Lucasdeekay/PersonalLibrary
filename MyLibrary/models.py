from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class CustomUser(AbstractUser):
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.username


class Book(models.Model):
    user = models.ForeignKey(CustomUser, blank=False, on_delete=models.CASCADE)
    title = models.CharField(max_length=250, blank=False)
    author = models.CharField(max_length=250)
    isbn = models.CharField(max_length=100)
    publication_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title
