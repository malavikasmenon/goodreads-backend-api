import scrapy
import sys
import os
import django

# Dynamically set the path to find Django project
# Set the correct base directory (the project root)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))  # Moves up to goodreads-scrape/
PROJECT_DIR = os.path.join(BASE_DIR, "scraper_api")  # Path to Django project

# Ensure Django project is in Python path
sys.path.insert(0, BASE_DIR)  
sys.path.insert(0, PROJECT_DIR)  
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scraper_api.settings")
django.setup()

from scraper.models import ScrapedBook, UserProfile  # Import Django models


class GoodreadsProfileSpider(scrapy.Spider):
    name = "goodreads_profile"
    allowed_domains = ["goodreads.com"]
    # start_urls = ["https://www.goodreads.com/user/show/103608396-varun-krishna-s"]

    def __init__(self, start_url=None, *args, **kwargs):
        super(GoodreadsProfileSpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_url] if start_url else []
        self.user_data = {"profile_name": None, "goodreads_profile": start_url, "books": []}  # Store scraped data


    def parse(self, response):
        """
        Scrape three main categories sequentially:
        1. Currently Reading
        2. Want to Read
        3. Read
        """
        profile_name = response.xpath('//*[@id="profileNameTopHeading"]/text()').get()
        if profile_name:
            profile_name = profile_name.strip()
            # profile, created = UserProfile.objects.get_or_create(name=profile_name)
            user_data = {
                "profile_name": profile_name.strip() if profile_name else None,
                "goodreads_profile": self.start_urls[0],
                "books": []
            }
            
            yield from self.parse_current_reads(response, user_data=user_data)
    
    def parse_current_reads(self, response, user_data):
        shelf = "currently-reading"
        shelf_xpath = f"//a[contains(@href, 'shelf={shelf}')]/@href"
        link = response.xpath(shelf_xpath).get()
        
        if link:
            full_url = response.urljoin(link)
            yield scrapy.Request(full_url, callback=self.parse_books, meta={
                "user_data": user_data,
                "next_callback": self.parse_to_read,
                "shelf": "currently-reading"
            })
        else:
            yield from self.parse_to_read(response, user_data)
    
    def parse_to_read(self, response, user_data):
        shelf = "to-read"
        shelf_xpath = f"//a[contains(@href, 'shelf={shelf}')]/@href"
        link = response.xpath(shelf_xpath).get()
        
        if link:
            full_url = response.urljoin(link)
            yield scrapy.Request(full_url, callback=self.parse_books, meta={
                "user_data": user_data,
                "next_callback": self.parse_read,
                "shelf": "to-read"
            })
        else:
            yield from self.parse_read(response, user_data)
    
    def parse_read(self, response, user_data):
        shelf = "read"
        shelf_xpath = f"//a[contains(@href, 'shelf={shelf}')]/@href"
        link = response.xpath(shelf_xpath).get()
        
        if link:
            full_url = response.urljoin(link)
            yield scrapy.Request(full_url, callback=self.parse_books, meta={
                "user_data": user_data,
                "next_callback": None,
                "shelf": "read"
            })
        else:
            yield user_data
    
    def parse_books(self, response):
        """
        Extract book details from a given shelf.
        """
        book_rows = response.xpath("//tbody/tr[contains(@class, 'bookalike')]")
        user_data = response.meta["user_data"]
        next_callback = response.meta["next_callback"]
        shelf = response.meta["shelf"]

        for row in book_rows:
            book_title = row.xpath(".//td[contains(@class, 'title')]/div/a/@title").get()
            book_isbn = row.xpath(".//td[contains(@class, 'isbn')]/div/text()").get()
            book_author = row.xpath(".//td[contains(@class, 'author')]/div/a/text()").get()
            
            book_logged = {
                "title": book_title.strip() if book_title else None,
                "isbn": book_isbn.strip() if book_isbn else None,
                "author": book_author.strip() if book_author else None,
                "shelf": response.url.split("shelf=")[-1]
            }
            # book_logged["goodreads_profile"] = response.meta["user_data"]
            user_data["books"].append(book_logged)
            # ScrapedBook.objects.create(**book_logged)

        next_page = response.xpath("//a[contains(@class, 'next_page')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_books, meta={
                "user_data": user_data,
                "next_callback": next_callback,
                "shelf": shelf
            })
        elif next_callback:
            yield from next_callback(response, user_data)
        else:
            yield user_data
