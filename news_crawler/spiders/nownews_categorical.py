import scrapy
import json
from pathlib import Path

class NOWNewsSpider(scrapy.Spider):
    name = 'nownews'

    def __init__(self):
        super()
        self.url = f'https://www.nownews.com'
        # Collect scraped data
        self.links = []
        self.title = []
        self.text = []
        self.category = []
        # Create `output` dir
        self.out_dir = Path('./output')
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def start_requests(self):
        '''Collect article links from these pages:
        https://www.nownews.com/cat/politics/page/1/
        https://www.nownews.com/cat/finance/page/1/
        https://www.nownews.com/cat/sport/page/1/
        https://www.nownews.com/cat/entertainment/page/1/
        '''
        # Go to each news category page
        categories = ['politics', 'finance', 'sport', 'entertainment']
        urls = [f'{self.url}/cat/{c}/page/{i}' for c in categories for i in range(1, 6)]
        for u in urls:
            yield scrapy.Request(u, callback=self.parse_links)

    def parse_links(self, response: scrapy.http.TextResponse):
        # Select link elements
        a = response.xpath('//div[@id="nn-news-list"]/div/div/div/div/div/div/div/div/h3/a')

        # Extract article URLs from elements
        # `a` is a list of Selector objects
        # Call `a[0].attrib['href']` to get the href attribute of item 0
        # eg: <Selector xpath='//div[@id="nn-news-list"]/div/div/div/div/div/div/div/div/h3/a' data='<a href="https://www.nownews.com/news...'>
        article_links = {elem.attrib['href']: elem.attrib['title'] for elem in a}

        # Follow links
        for link in list(article_links.keys()):
            yield response.follow(link, callback=self.parse_page, cb_kwargs={'title': article_links[link]})
            # Set `dont_filter=True` to force scrape duplicate links

    def parse_page(self, response: scrapy.http.TextResponse, title=''):
        # Current category
        article_category = response.headers.get(b'Referer').decode()
        # Make 'politics' singular
        if article_category == 'politics':
            article_category = 'politic'

        # Extract article text
        p = response.xpath('//span/p')
        txt_list = [tag.get() for tag in p]
        txt = ''.join(txt_list)
        # Add to collection
        self.links.append(response.url)
        self.title.append(title)
        self.text.append(txt)
        self.category.append(article_category)

    def closed(self, reason):
        '''This runs after the spider exits.'''
        # Format collected data
        data = {
            'url': self.links,
            'title': self.title,
            'text': self.text,
            'category': self.category,
        }
        # Save collected data to disk
        with open('./output/wantwant-raw/wantwant4categories.json', 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

'''
https://www.nownews.com/cat/politics/page/1/
https://www.nownews.com/cat/finance/page/1/
https://www.nownews.com/cat/sport/page/1/
https://www.nownews.com/cat/entertainment/page/1/

To crawl, your current directory must be where scrapy.cfg resides.
Make sure to call the crawler class's name attribute.

For example, our crawler class NewsSpider has name = 'news_spider'.

So we'd need to run this in a terminal:

    cd nownews
    scrapy crawl nownews

No need to handle duplicate links, scrapy does it for you!
'''