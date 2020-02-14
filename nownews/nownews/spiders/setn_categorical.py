import scrapy
import json
import re
from pathlib import Path
from yarl import URL

'''
- SETn
    - 42 links per page
    - go from page 1-4 so that we'd have around 160 articles per cat

    - politic 6
    - https://www.setn.com/ViewAll.aspx?PageGroupID=6
    - https://www.setn.com/ViewAll.aspx?PageGroupID=6&p=2
    - https://www.setn.com/ViewAll.aspx?PageGroupID=6&p=2

    - finance 2
    - https://www.setn.com/ViewAll.aspx?PageGroupID=2
    - https://www.setn.com/ViewAll.aspx?PageGroupID=2&p=2

    - entertainment 8
    - https://www.setn.com/ViewAll.aspx?PageGroupID=8
    - https://www.setn.com/ViewAll.aspx?PageGroupID=8&p=2
    - NEED SPECIAL HANDLING TO FILTER other categories of news
    - KEEP these: 娛樂, 電影, 日韓, 名家, 音樂

    - sport 34
    - https://www.setn.com/ViewAll.aspx?PageGroupID=34
    - https://www.setn.com/ViewAll.aspx?PageGroupID=34&p=2

    links
        div clacc="row NewsList" > div > div > h3 > a

    article category
        referer URL: {
            6: 'politic',
            2: 'finance',
            8: 'entertainment',
            34: 'sport'
        }
    article title
        div > h1 class="news-title-3"
    article date
        div class="page-title-text" > time
    article body text
        article > div id="Content1" > p
'''

class NewsSpider(scrapy.Spider):
    name = 'setn_categorical'

    def __init__(self):
        super()
        self.url = f'https://www.setn.com'
        # Create `output` dir
        self.out_dir = Path('./output/news_categorical')
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.category_id_name = {
            # '6': 'politic',
            '2': 'finance',
            '8': 'entertainment',
            '34': 'sport',
        }

    def start_requests(self):
        # Go to each search result page
        categories = self.category_id_name.keys()
        urls = [f'{self.url}/ViewAll.aspx?PageGroupID={c}&p={i}' for c in categories for i in range(1, 5)]
        for u in urls:
            yield scrapy.Request(u, callback=self.parse_links)

    def parse_links(self, response: scrapy.http.TextResponse):
        '''
        select links
            div clacc="row NewsList" > div > div > h3 > a

        skip links whose title starts with '影》'
        '''
        # Ensure 'entertainment' links are free of unrelated categories
        if 'ID=8' in response.url:
            a = []
            # Get all rows
            rows = response.xpath('//div[@class="row NewsList"]/div/div')
            for r in rows:
                # Accept only these tags
                if any(x in r.get() for x in ['娛樂', '電影', '日韓', '名家', '音樂']):
                    a.append(r.xpath('h3/a'))
        else:
            # Collect links as usual
            a = response.xpath('//div[@class="row NewsList"]/div/div/h3/a')
        # `a` is a list of Selector objects
        # Call `a[0].attrib['href']` to get the href attribute of item 0
        # eg: <Selector xpath='//h3/a' data='<a href="https://www.chinatimes.com/...'>
        article_links = [elem.attrib['href'] for elem in a]

        # Follow links
        for link in article_links:
            yield response.follow(link, callback=self.parse_page)

    def parse_page(self, response: scrapy.http.TextResponse):
        '''
        article title
            div > h1 class="news-title-3"
        article date
            div class="page-title-text" > time
        article body text
            article > div id="Content1" > p
        '''

        # Extract category
        # https://www.setn.com/ViewAll.aspx?PageGroupID=8&p=2
        # Regex: ID=[\d]+
        referer = response.request.headers.get(b'Referer').decode() # eg https://www.chinatimes.com/sports/total?page=4
        cat_id = re.search(r'ID=[\d]+', referer).group().split('=')[-1]
        category = self.category_id_name[cat_id]
        # Handle entertainment news differently
        if cat_id == '8':
            # Extract title
            title = response.xpath('//div/h1[@id="newsTitle"]')[0].get()
            # Extract datetime
            date = response.xpath('//div[@class="titleBtnBlock"]/div[@class="time"]')[0].get()
            # Extract paragraphs
            p = response.xpath('//article[@class="articleLay"]/div/div/p')
            txt_list = [tag.get() for tag in p]
            txt = ''.join(txt_list)
        else:
            # Extract title
            title = response.xpath('//div/h1[@class="news-title-3"]')[0].get()
            # Extract datetime
            date = response.xpath('//div[@class="page-title-text"]/time')[0].get()
            # Extract paragraphs
            p = response.xpath('//article/div[@id="Content1"]/p')
            txt_list = [tag.get() for tag in p]
            txt = ''.join(txt_list)
        # Prepare scraped data for saving
        # https://www.setn.com/News.aspx?NewsID=689753
        article_link = response.url
        article_id = article_link.split('=')[-1]
        content = {
            'category': category,
            'url': response.url,
            'title': title,
            'date': date,
            'text': txt,
        }
        # Write each article to file
        (self.out_dir/'setn').mkdir(parents=True, exist_ok=True)
        with open(f'{self.out_dir}/setn/{article_id}.json', 'w') as f:
            f.write(json.dumps(content, ensure_ascii=False, indent=2))

'''
To crawl, your current directory must be where scrapy.cfg resides.
Make sure to call the crawler class's name attribute.

So we'd need to run this in a terminal:

    cd nownews
    scrapy crawl setn_categorical

No need to handle duplicate links, scrapy does it for you!
'''