from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
import uuid
from datetime import datetime
from django.contrib.auth.hashers import make_password, check_password


from django.contrib.auth.models import BaseUserManager

class UserProfileManager(BaseUserManager):
    def create_user(self, username, email, password=None, goodreads_profile=''):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(username=username, email=email, goodreads_profile=goodreads_profile)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, goodreads_profile):
        user = self.create_user(username, email, password, goodreads_profile)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, email):
        """This method is needed for Django admin login to work"""
        return self.get(email=email)
    


class UserProfile(models.Model):
    """Stores unique user profiles from Goodreads."""
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)  # Store hashed passwords
    user_id = models.UUIDField(default=uuid.uuid4, editable=False)
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
    is_active = models.BooleanField(default=True)  # Required by Django
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserProfileManager()


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "password", "goodreads_profile"]


    def get_by_natural_key(self):
        return self.email  #


    def __str__(self):
        return self.username
    
    def set_password(self, raw_password):
        """Hash the password before saving"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verify password"""
        return check_password(raw_password, self.password)
    
    def get_user_id(self):  
        return self.user_id 
    
    @property
    def is_authenticated(self):
        """Django expects this property to check if the user is authenticated."""
        return True  # Always True for logged-in users

    @property
    def is_anonymous(self):
        """Django expects this property for unauthenticated users."""
        return False  # Always False for real users
    
    # ✅ Required for permissions to work
    def has_perm(self, perm, obj=None):
        """Check if the user has a specific permission."""
        return self.is_superuser  # Superusers have all permissions

    def has_module_perms(self, app_label):
        """Check if the user has permissions for a specific app."""
        return self.is_superuser  # Superusers have all module permission


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
    

class Interaction(models.Model):
    LIKED = 'like'
    PASSED = 'pass'
    
    ACTION_CHOICES = [
        (LIKED, 'Liked'),
        (PASSED, 'Passed'),
    ]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="given_interactions")
    target_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="received_interactions")
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'target_user')  # A user can interact with another user only once

    def __str__(self):
        return f"{self.user} {self.action} {self.target_user}"

class Match(models.Model):
    user1 = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="matches_initiated")
    user2 = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="matches_received")
    goodreads_score = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')  # Ensure a match is unique

    def __str__(self):
        return f"Match: {self.user1} ❤️ {self.user2}"