"""
URL configuration for scraper_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from scraper.views import save_scraped_data, UserRegistrationView, UserLoginView, UserProfileView, RecommendedProfilesView, InteractionView, MatchListView


urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/save_scraped_data/", save_scraped_data, name="save_scraped_data"),
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profiles/recommend/', RecommendedProfilesView.as_view(), name='recommend-profiles'),
    path('profiles/interact/', InteractionView.as_view(), name='interact'),
    path('matches/', MatchListView.as_view(), name='matches'),
]