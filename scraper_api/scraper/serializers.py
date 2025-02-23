from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile, Interaction, Match, ScrapedBook
import subprocess


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'password', 'gender', 'date_of_birth', 'location', 
                  'goodreads_profile', 'looking_for', 'min_age_preference', 'max_age_preference']

    def create(self, validated_data):
        user = UserProfile(
            email=validated_data['email'],
            username=validated_data['username'],
            gender=validated_data['gender'],
            date_of_birth=validated_data['date_of_birth'],
            location=validated_data.get('location', ''),
            goodreads_profile=validated_data['goodreads_profile'],
            looking_for=validated_data['looking_for'],
            min_age_preference=validated_data['min_age_preference'],
            max_age_preference=validated_data['max_age_preference'],
        )
        user.set_password(validated_data['password'])  # Hash password
        user.save()
        import os
        print(os.getcwd())
        if user.goodreads_profile:
            command = f"cd ../scraping && scrapy crawl goodreads_profile -s ROBOTSTXT_OBEY=False -a start_url='{user.goodreads_profile}'"
            subprocess.Popen(command, shell=True)
        return user
    


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            user = UserProfile.objects.get(email=email)
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError({"non_field_errors": ["Invalid email or password"]})

        if not user.check_password(password):
            raise serializers.ValidationError({"non_field_errors": ["Invalid email or password"]})

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return {
            "user_id": user.user_id,
            "username": user.username,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapedBook
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ['email', 'username']

    # def update(self, instance, validated_data):
    #     favorite_books = validated_data.pop('favorite_books', [])
    #     instance.favorite_books.set(favorite_books)  # Update many-to-many relationship
    #     return super().update(instance, validated_data)


class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = '__all__'


class MatchSerializer(serializers.ModelSerializer):
    user1 = UserProfileSerializer()
    user2 = UserProfileSerializer()

    class Meta:
        model = Match
        fields = ['id', 'user1', 'user2', 'created_at']