
# FOSS Hack Specific Details
- Frontend Repo Link: https://github.com/malavikasmenon/goodreads-dating-app
- LICENSE: GPL-3.0
- Demo: https://drive.google.com/drive/u/0/folders/17aWuOr3sP_-PEi4cBTT3WCM3V3qHkPUq

# Project Overview
### Inspiration
You must have seen that one shot repititively used in rom-coms across cultures - the lead characters are in a bookstore/library, coincidentally about to take the same book at the same time. They notice each other suddenly and thus begins the spark of love. In an increasingly digital world, this might be a little hard to achieve, and this project is our humble attempt to recreate this. 

Our Goodreads Dating App is exactly what it sounds like - use your Goodreads logs to match with people. If there are people reading the same books as you are, enjoying the same authors as you are and even have an overlap in your wishlists, chances are you all might have a lot in common to talk about & those conversations could potentially lead to something more. 

### Why Goodreads?
Despite its minimal UI and limited features, it remains one of the most popular tools to log your reads and has considerable number of users on board. 

### User Notes
Since Goodreads don't have an active API set to be used, the public user profiles need to be scraped in order to get your logged information. So, to be able to use the application it is required that users have a public Goodreads profile.


# Implementation Details

### Tech Stack
- [Scrapy](https://docs.scrapy.org/en/latest/) is used for crawling the public user profiles on Goodreads.
- Django for setting up APIs for the application including - registration, authentication, fetching & swiping on profiles
- React is used for setting up the web application

This repo contains the Scrapy Spider and the Django APIs, the frontend code can be accessed [here]().

### Algorithm for Recommended Profiles
- Filtering based on preferred age/gender input by user.
- Browse through 3 Goodreads shelves - to-read, read, currently-reading. Filter out if there are less than 2 books in common across the three shelfes

### Setting up & running the spider
```
python3 -m venv testenv
source testenv/bin/activate
pip install -r requirements.txt
cd scraping
scrapy crawl goodreads_profile -s ROBOTSTXT_OBEY=False -a start_url="input-profile-url" -o output.json
```

### Setting up Django
```
python3 -m venv testenv
source testenv/bin/activate
pip install -r requirements.txt
cd scraper_api
python manage.py runserver
```

### API Documentation

- admin/: To view Django admin & monitors objects created as part of the application.
- register/: To setup user profile & provide Goodreads profile URL as input
- login/: Authentication
- api/save_scraped_data/: To scrape data using the Scrapy spider as part of the user registration process. 
- profile/: To view your own profile
- profiles/recommend/: To view profiles that are recommended for you, this is where the filtering algorithm using the 3 Goodreads shelves come into play.
- profiles/interact/: To like/pass on recommended profiles.
- matches/: To view matches (mutual likes)


