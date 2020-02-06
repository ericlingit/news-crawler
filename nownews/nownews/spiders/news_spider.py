import scrapy
from yarl import URL

class NewsSpider(scrapy.Spider):
    name = 'news'

    def __init__(self, category):
        super()
        self.category = category
        self.url = URL(f'https://www.nownews.com/cat/{category}/page/')

    def start_requests(self):
        # Go to each news category page
        urls = [(self.url/str(i)) for i in range(1, 6)]
        for u in urls:
            yield scrapy.Request(u, callback=self.parse)

    def parse_links(self, response: scrapy.http.TextResponse):
        # Collect links
        response.
        # Follow links
        article_links = []
        for i in article_links:
            yield scrapy.Request(i, callback=self.parse_page)

    def parse_page(self, response: scrapy.http.TextResponse):
        # Extract article text
        pass
'''
https://www.nownews.com/cat/politics/page/1/
https://www.nownews.com/cat/finance/page/1/
https://www.nownews.com/cat/sport/page/1/
https://www.nownews.com/cat/entertainment/page/1/
'''

if __name__ == '__main__':
    x = NewsSpider('politics')
    x.start_requests()