from django.db import models


class UserProfile(models.Model):
    """Stores unique user profiles from Goodreads."""
    profile_name = models.CharField(max_length=255)  # Ensure no duplicate profiles
    created_at = models.DateTimeField(auto_now_add=True)
    goodreads_profile = models.URLField(unique=True, primary_key=True)

    def __str__(self):
        return self.profile_name


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