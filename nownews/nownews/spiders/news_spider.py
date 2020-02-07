import scrapy
import json
from pathlib import Path

class NewsSpider(scrapy.Spider):
    name = 'news_spider'

    def __init__(self, category):
        super()
        self.category = category
        self.url = f'https://www.nownews.com/cat/{category}/page/'
        # Collect scraped data
        self.links = []
        self.title = []
        self.text = []
        # Create `output` dir
        self.out_dir = Path('./output')
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def start_requests(self):
        # Go to each news category page
        urls = [f'{self.url}/{str(i)}/' for i in range(1, 6)]
        for u in urls:
            yield scrapy.Request(u, callback=self.parse_links)

    def parse_links(self, response: scrapy.http.TextResponse):
        # Collect links
        a = response.xpath('//div[@id="nn-news-list"]/div/div/div/div/div/div/div/div/h3/a')
        # `a` is a list of Selector objects
        # Call `a[0].attrib['href']` to get the href attribute of item 0
        # eg: <Selector xpath='//div[@id="nn-news-list"]/div/div/div/div/div/div/div/div/h3/a' data='<a href="https://www.nownews.com/news...'>
        article_links = {elem.attrib['href']: elem.attrib['title'] for elem in a}

        # # Save links to file
        # with open('./output/article-links.txt', 'a') as f:
        #     out = ''.join([f'{k}\t{v}\n' for k,v in article_links.items()])
        #     f.write(out)

        # Follow links
        for link in list(article_links.keys()):
            yield scrapy.Request(link, callback=self.parse_page)

    def parse_page(self, response: scrapy.http.TextResponse):
        # Extract title
        title = response.xpath('//h1[@class="entry-title"]').get()
        # Extract article text
        p = response.xpath('//span/p')
        txt_list = [tag.get() for tag in p]
        txt = ''.join(txt_list)
        # Add to collection
        self.links.append(response.url)
        self.title.append(title)
        self.text.append(txt)

    def closed(self, reason):
        '''This runs after the spider exits.'''
        # Format collected data
        data = {
            'url': self.links,
            'title': self.title,
            'text': self.text
        }
        # Save collected data to disk
        with open(f'./output/scraped_{self.category}.json', 'w') as f:
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
    scrapy crawl news_spider

And you'd get an error because I forgot to supply the argument `category`.

To supply an argument, do this:

    scrapy crawl news_spider -a category=sport

No need to handle duplicate links, scrapy does it for you!
'''