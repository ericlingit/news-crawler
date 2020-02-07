import scrapy

class NewsSpider(scrapy.Spider):
    name = 'news_spider'

    def __init__(self, category):
        super()
        self.category = category
        self.url = f'https://www.nownews.com/cat/{category}/page/'

    def start_requests(self):
        # Go to each news category page
        urls = [f'{self.url}/{str(i)}/' for i in range(1, 3)]
        for u in urls:
            yield scrapy.Request(u, callback=self.parse_links)

    def parse_links(self, response: scrapy.http.TextResponse):
        # Collect links
        a = response.xpath('//div[@id="nn-news-list"]/div/div/div/div/div/div/div/div/h3/a')
        # `a` is a list of Selector objects
        # Call `a[0].attrib['href']` to get the href attribute of item 0
        # eg: <Selector xpath='//div[@id="nn-news-list"]/div/div/div/div/div/div/div/div/h3/a' data='<a href="https://www.nownews.com/news...'>
        # article_links = [elem.attrib['href'] for elem in a]

        # Save links to file
        article_links = [(elem.attrib['href'], elem.attrib['title']) for elem in a]
        with open('./article-links.txt', 'w') as f:
            f.write('\n'.join(article_links))

        # # Follow links
        # for link in article_links:
        #     yield scrapy.Request(link, callback=self.parse_page)

    # def parse_page(self, response: scrapy.http.TextResponse):
    #     # Extract article text
    #     pass
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

'''