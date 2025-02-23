import subprocess
from django.db.models.signals import post_save
from django.dispatch import receiver
from .scraper.models import UserProfile

@receiver(post_save, sender=UserProfile)
def trigger_scrapy_spider(sender, instance, created, **kwargs):
    """Run Scrapy spider after user creation"""
    if created and instance.goodreads_profile:
        command = f"scrapy crawl goodreads_profile -s ROBOTSTXT_OBEY=False -a start_url='{instance.goodreads_profile}'"
        subprocess.Popen(command, shell=True)