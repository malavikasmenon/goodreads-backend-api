from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from scraper.models import ScrapedBook, UserProfile

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
