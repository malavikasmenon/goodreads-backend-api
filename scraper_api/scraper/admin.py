from django.contrib import admin
from .models import UserProfile, ScrapedBook

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("profile_name", "created_at")  # Columns in the admin list view
    search_fields = ("profile_name",)  # Enable search by name
    ordering = ("-created_at",)  # Show newest profiles first


@admin.register(ScrapedBook)
class ScrapedBookAdmin(admin.ModelAdmin):
    list_display = ("goodreads_profile", "title", "author", "shelf", "created_at")
    search_fields = ("title", "author", "goodreads_profile__profile_name")  # Enable search
    list_filter = ("shelf",)  # Filter books by shelf (read, to-read, etc.)
    ordering = ("-created_at",)  # Show newest books first
