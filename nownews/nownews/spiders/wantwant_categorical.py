import scrapy
import json
from pathlib import Path
from yarl import URL

'''
- WantWant
    - https://www.chinatimes.com/politic/total
    - https://www.chinatimes.com/star/total
    - https://www.chinatimes.com/money/total
    - https://www.chinatimes.com/sports/total

    - https://www.chinatimes.com/politic/total?page=2
    - https://www.chinatimes.com/politic/total?page=10
    - article list: section class="article-list" > ul > li > div > div > h3 > a

- SETn
    - https://www.setn.com/ViewAll.aspx?PageGroupID=6


'''

class NewsSpider(scrapy.Spider):
    name = 'wantwant_categorical'

    def __init__(self):
        super()
        self.url = f'https://www.chinatimes.com'
        # Create `output` dir
        self.out_dir = Path('./output/news_categorical')
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def start_requests(self):
        # Go to each search result page
        categories = ['politic', 'star', 'money', 'sports']
        urls = [f'{self.url}/{c}/total?page={i}' for c in categories for i in range(1, 6)]
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
            yield response.follow(link, callback=self.parse_page)

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
            # Extract category
            referer = response.request.headers.get(b'Referer').decode() # eg https://www.chinatimes.com/sports/total?page=4
            category = referer.split('/')[-2]
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
            'category': category,
            'url': response.url,
            'title': title,
            'date': date,
            'text': txt,
        }
        # Write each article to file
        with open(f'{self.out_dir}/{article_id}.json', 'w') as f:
            f.write(json.dumps(content, ensure_ascii=False, indent=2))

'''
To crawl, your current directory must be where scrapy.cfg resides.
Make sure to call the crawler class's name attribute.

So we'd need to run this in a terminal:

    cd nownews
    scrapy crawl wantwant_categorical

No need to handle duplicate links, scrapy does it for you!
'''