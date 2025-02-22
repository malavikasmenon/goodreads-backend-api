# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter


# class ScrapingPipeline:
#     def process_item(self, item, spider):
#         return item


import requests
import json

class DjangoPipeline:
    API_URL = "http://127.0.0.1:8000/api/save_scraped_data/"

    def process_item(self, item, spider):
        """Send Scrapy data to Django API"""
        print("item", item)
        try:
            response = requests.post(self.API_URL, data=json.dumps(item), headers={"Content-Type": "application/json"})
            response.raise_for_status()
            print(response.content)
        except requests.exceptions.RequestException as e:
            spider.logger.error(f"Failed to send data to Django: {e}")

        return item
