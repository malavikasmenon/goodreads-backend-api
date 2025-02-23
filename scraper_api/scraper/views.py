from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from scraper.models import ScrapedBook, UserProfile, Interaction, Match
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer, InteractionSerializer, MatchSerializer
from rest_framework import generics, permissions
from django.utils.timezone import now



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
            return Response({"message": "User registered successfully", "user_id": user.user_id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# User Login API
class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Get user profile
class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return UserProfile.objects.get(user_id=self.request.user.user_id)


# # Get Recommended Profiles
# class RecommendedProfilesView(generics.ListAPIView):
#     serializer_class = UserProfileSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         return UserProfile.objects.exclude(user_id=user.user_id)  # TODO: Improve with book-based matching
    

class RecommendedProfilesView(generics.ListAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        # Calculate user's age
        today = now().date()
        user_age = today.year - user.date_of_birth.year - (
            (today.month, today.day) < (user.date_of_birth.month, user.date_of_birth.day)
        )

        # Get users that match gender preference
        gender_matches = UserProfile.objects.filter(
            looking_for=user.gender,  
            gender=user.looking_for
        )

        # Filter based on age preferences
        age_filtered = gender_matches.filter(
            min_age_preference__lte=user_age,  
            max_age_preference__gte=user_age  
        )

        # Exclude current user from recommendations
        filtered_profiles = age_filtered.exclude(user_id=user.user_id)

        # Book-based matching
        recommended_profiles = []
        user_books = ScrapedBook.objects.filter(goodreads_profile=user)

        user_current_reads = set(user_books.filter(shelf="currently-reading"))
        user_to_read = set(user_books.filter(shelf="to-read"))
        user_read = set(user_books.filter(shelf="read"))


        for target_user in filtered_profiles:
            target_books = ScrapedBook.objects.filter(goodreads_profile=target_user)

            target_current_reads = set(target_books.filter(shelf="currently-reading"))
            target_to_read = set(target_books.filter(shelf="to-read"))
            target_read = set(target_books.filter(shelf="read"))

            # Calculate book matching points
            points = len(user_current_reads & target_current_reads) + len(user_to_read & target_to_read) + len(user_read & target_read)

            if points > 2:
                recommended_profiles.append(target_user)

        return recommended_profiles



# Like/Pass a Profile
class InteractionView(generics.CreateAPIView):
    serializer_class = InteractionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        target_username = request.data.get("target_username")
        action = request.data.get("action")

        if not target_username or action not in ["like", "pass"]:
            return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

        target_user = UserProfile.objects.get(username=target_username)

        interaction, created = Interaction.objects.get_or_create(user=user, target_user=target_user, defaults={"action": action})

        # Check if mutual "like" → Create a match
        if action == "like" and Interaction.objects.filter(user=target_user, target_user=user, action="like").exists():
            Match.objects.get_or_create(user1=user, user2=target_user)

        return Response(InteractionSerializer(interaction).data, status=status.HTTP_201_CREATED)


# Get Matches
class MatchListView(generics.ListAPIView):
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Match.objects.filter(user1=self.request.user) | Match.objects.filter(user2=self.request.user)
