from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from scraper.models import ScrapedBook, UserProfile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegistrationSerializer, UserLoginSerializer

@csrf_exempt
def save_scraped_data(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print(request)
            print(request.body)
            profile_name = data.get("profile_name")
            goodreads_profile = data.get("goodreads_profile")
            books = data.get("books", [])
            print(data)
            print(profile_name, goodreads_profile)
            print("here")
            # Create user profile if it doesn't exist
            user, created = UserProfile.objects.get_or_create(goodreads_profile=goodreads_profile, defaults={"profile_name": profile_name})
            print("here too")
            # Bulk create books
            book_objects = [
                ScrapedBook(title=book["title"], author=book["author"], shelf=book["shelf"], goodreads_profile=user, isbn=book["isbn"])
                for book in books
            ]
            ScrapedBook.objects.bulk_create(book_objects)

            return JsonResponse({"message": "Data saved successfully"}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)


# User Registration API
class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully", "user_id": user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# User Login API
class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
