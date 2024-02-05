from django.contrib.auth.models import User
from django.db import models

# Create your models here.

""" Model that extends the functionality of the built-in User model.
"""
class UserProfile(models.Model):
    # OneToOneFiled that creates a direct link between the current model and the existing User model.
    # Ensures a one-to-one relationship between instances of the current model and the User model.
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Additional fields that are used for setup or require quick access throught the application.
    setup_complete = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.user.username