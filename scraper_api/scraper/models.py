from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
import uuid
from datetime import datetime
from django.contrib.auth.hashers import make_password, check_password



class UserProfile(models.Model):
    """Stores unique user profiles from Goodreads."""
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)  # Store hashed passwords
    id = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, default='')
    profile_name = models.CharField(max_length=255)  # Ensure no duplicate profiles
    created_at = models.DateTimeField(auto_now_add=True)
    goodreads_profile = models.URLField(unique=True, primary_key=True)
    gender_choices = [('male', 'Male'), ('female', 'Female'), ('non-binary', 'Non Binary'), ('other', 'Other'), ('prefer-not-to-say', 'Prefer Not To Say')]
    gender = models.CharField(max_length=20, choices=gender_choices, default='prefer_not_to_say')
    date_of_birth = models.DateField(default=datetime(2000, 1, 1))
    location = models.CharField(max_length=255, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    looking_for = models.CharField(max_length=20, choices=gender_choices, default='prefer_not_to_say')
    min_age_preference = models.IntegerField(default=18)
    max_age_preference = models.IntegerField(default=100)


    def __str__(self):
        return self.username
    
    
    def set_password(self, raw_password):
        """Hash the password before saving"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verify password"""
        return check_password(raw_password, self.password)
    


class ScrapedBook(models.Model):
    """Stores books scraped for each profile."""
    goodreads_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True, blank=True)
    author = models.CharField(max_length=255, null=True, blank=True)
    isbn = models.CharField(max_length=50, null=True, blank=True)
    shelf = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.shelf})"