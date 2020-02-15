import scrapy
import json
from pathlib import Path
from yarl import URL

'''
- WantWant
    - https://www.chinatimes.com/Search/韓國瑜
    - 1,189 pages for tag 韓國瑜.
    - 20 articles per page
    From https://www.chinatimes.com/Search/韓國瑜?page=1
    to https://www.chinatimes.com/Search/韓國瑜?page=1181
'''

class NewsSpider(scrapy.Spider):
    name = 'wantwant_kfish'

    def __init__(self):
        super()
        self.url = f'https://www.chinatimes.com/Search/韓國瑜'
        # # Collect scraped data
        # self.links = []
        # self.title = []
        # self.date = []
        # self.text = []
        # Create `output` dir
        self.out_dir = Path('./output')
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def start_requests(self):
        # Go to each search result page
        urls = [f'{self.url}?page={i}' for i in range(1, 1_173)]
        for u in urls:
            yield scrapy.Request(u, callback=self.parse_links)

    def parse_links(self, response: scrapy.http.TextResponse):
        '''
        select links
            h3 > a

        skip links whose title starts with '影》'
        '''
        # Collect links
        a = response.xpath('//h3/a')
        # `a` is a list of Selector objects
        # Call `a[0].attrib['href']` to get the href attribute of item 0
        # eg: <Selector xpath='//h3/a' data='<a href="https://www.chinatimes.com/...'>
        article_links = [elem.attrib['href'] for elem in a]

        # Follow links
        for link in article_links:
            yield scrapy.Request(link, callback=self.parse_page)

    def parse_page(self, response: scrapy.http.TextResponse):
        '''
        select title
            header class="article-header" > h1 class="article-title"
        select datetime
            header class="article-header" > div > div > div > div class="meta-info" > time
        select text
            div class="article-body" > p

        skip article whose body contain 子瑜
        '''
        try:
            # Extract title
            title = response.xpath('//header[@class="article-header"]/h1')[0].get()
            # Extract datetime
            date = response.xpath('//header[@class="article-header"]/div/div/div/div[@class="meta-info"]/time')[0].attrib['datetime']
            # Extract paragraphs
            p = response.xpath('//div[@class="article-body"]/p')
        except Exception as e:
            print(e)
            return
        txt_list = [tag.get() for tag in p]
        txt = ''.join(txt_list)
        # Prepare scraped data for saving
        article_link = response.url
        article_id = URL(article_link).parts[-1]
        content = {
            'url': response.url,
            'title': title,
            'date': date,
            'text': txt,
        }
        # Create output folder
        (self.out_dir/'wantwant').mkdir(parents=True, exist_ok=True)
        # Write each article to file
        with open(f'./output/wantwant/{article_id}.json', 'w') as f:
            f.write(json.dumps(content, ensure_ascii=False, indent=2))

        # # Add to collection
        # self.links.append(response.url)
        # self.title.append(title)
        # self.date.append(date)
        # self.text.append(txt)

    # def closed(self, reason):
    #     '''This runs after the spider exits.'''
    #     # Format collected data
    #     data = {
    #         'url': self.links,
    #         'title': self.title,
    #         'date': self.date,
    #         'text': self.text
    #     }
    #     # Save collected data to disk
    #     with open(f'./output/scraped_woof.json', 'w') as f:
    #         json.dump(data, f, ensure_ascii=False, indent=2)

'''
- WantWant
    - https://www.chinatimes.com/Search/韓國瑜
    - 1,181 pages for tag 韓國瑜. From https://www.chinatimes.com/Search/韓國瑜?page=1 to https://www.chinatimes.com/Search/韓國瑜?page=1181

To crawl, your current directory must be where scrapy.cfg resides.
Make sure to call the crawler class's name attribute.

For example, our crawler class NewsSpider has name = 'woof_spider'.

So we'd need to run this in a terminal:

    cd nownews
    scrapy crawl woof_spider

No need to handle duplicate links, scrapy does it for you!
'''