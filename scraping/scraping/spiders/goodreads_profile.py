import scrapy


class GoodreadsProfileSpider(scrapy.Spider):
    name = "goodreads_profile"
    allowed_domains = ["goodreads.com"]
    start_urls = ["https://www.goodreads.com/user/show/103608396-varun-krishna-s"]

    def parse(self, response):
        """
        Scrape three main categories
        1. Want to read
        2. Currently Reading
        3. Read
        """
        profile_name = response.xpath('//*[@id="profileNameTopHeading"]/text()').get()
        shelves = ["currently-reading", "to-read", "read"]
        user_data = {
            "profile_name": profile_name.strip() if profile_name else None,
            "currently-reading": [],
            "to-read": [],
            "read": []
        }
        
        for shelf in shelves:
            shelf_xpath = f"//a[contains(@href, 'shelf={shelf}')]/@href"
            print(shelf_xpath)
            link = response.xpath(shelf_xpath).get()
            print(link)
            full_url = response.urljoin(link)  # Convert relative to absolute URL
            print(full_url)
            yield scrapy.Request(full_url, callback=self.parse_shelf, meta={"user_data": user_data, "shelf": shelf})


        # yield {"name": profile_name}

    def parse_shelf(self, response):
        """
        Book Title
        Book Author
        Book Rating
        """
        book_rows = response.xpath("//tbody/tr[contains(@class, 'bookalike')]")
        user_data = response.meta["user_data"]
        shelf = response.meta["shelf"]
        
        for row in book_rows:
            book_title = row.xpath(".//td[contains(@class, 'title')]/div/a/@title").get()
            book_isbn = row.xpath(".//td[contains(@class, 'isbn')]/div/text()").get()
            book_author = row.xpath(".//td[contains(@class, 'author')]/div/a/text()").get()
            book_logged = {
                "title": book_title.strip() if book_title else None,
                "isbn": book_isbn.strip() if book_isbn else None,
                "author": book_author.strip() if book_author else None,
            }
            user_data[shelf].append(book_logged)

        next_page = response.xpath("//a[contains(@class, 'next_page')]/@href").get()
    
        if next_page:
            yield response.follow(next_page, callback=self.parse_shelf, meta={"user_data": user_data, "shelf": shelf})
        
        if all(user_data[s] for s in ["currently-reading", "to-read", "read"]):
            yield user_data
