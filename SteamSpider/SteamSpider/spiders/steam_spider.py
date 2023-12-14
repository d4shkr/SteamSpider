import scrapy
from SteamSpider.items import SteamspiderItem


class SteamSpider(scrapy.Spider):
    name = "SteamSpider"
    allowed_domains = ['store.steampowered.com']
    queries = ['minecraft', 'головоломка', 'инди']

    def start_requests(self):
        # нашла API, которым пользуется поиск Steam для подгрузки новых игр. ищем только 100 игр, без бандлов
        search_url = 'https://store.steampowered.com/search/results/?query&start=0&count=100&category1=998&term=' 

        for query in self.queries:
            yield scrapy.Request(url=search_url + query, callback=self.find_games)

    def find_games(self, response):
        game_urls = response.xpath('//div[@id="search_resultsRows"]/a/@href').getall()
        for game_url in game_urls:
            yield scrapy.Request(url=game_url, callback=self.parse)

    def parse(self, response):
        item = SteamspiderItem()
        try:
            name = response.xpath('//div[@id="appHubAppName"]/text()').extract()
            if name:
                name = name[0]
            else:
                name = 'No name'
        except:
            name = 'error'

        try:
            categories = response.xpath('//div[@class="blockbg"]/a/text()').extract()[1:]
        except:
            categories = ['error']
        
        try:
            review_count = response.xpath('//span[@class="nonresponsive_hidden responsive_reviewdesc"]/text()').extract()
            if review_count:
                review_count = review_count[-1].strip()[2:]
            else:
                review_count = 'No reviews'
        except:
            review_count = 'error'

        try:
            release_date = response.xpath('//div[@class="release_date"]/div[@class="date"]/text()').extract()
            if release_date:
                release_date = release_date[0]
            else:
                release_date = 'No release date'
        except:
            release_date = 'error'

        try:
            developers = response.xpath('//div[@id="developers_list"]/a/text()').extract()
        except:
            developers = ['error']

        try:
            tags = list(map(lambda x : x.strip(), response.xpath('//div[@class="glance_tags popular_tags"]/a/text()').extract()))
        except:
            tags = ['error']

        try:
            price_container = response.xpath('//div[@class="game_purchase_action_bg"]') # берем первый, если есть, следующие могут быть для других версий/саундтрека итд
            if price_container:
                price = price_container[0].xpath('.//div[@class="game_purchase_price price"]/text()').extract()
                if price:
                    price = price[0].strip()
                else: # если игра по скидке
                    price = price_container[0].xpath('.//div[@class="discount_block game_purchase_discount"]/div[@class="discount_prices"]/div[@class="discount_final_price"]/text()').extract()
                    if price:
                        price = price[0].strip()
                    else:
                        price = "No price"
            else:
                price = 'No price' # если игра не вышла, например https://store.steampowered.com/app/1030300/Hollow_Knight_Silksong/
        except:
            price = 'error'

        try:
            platforms_container = response.xpath('//div[@class="game_area_purchase_platform"]') # берем первый, если есть, следующие могут быть для других версий/саундтрека итд
            if platforms_container:
                platforms = list(map(lambda x : x.split()[-1], platforms_container[0].xpath('.//span/@class').extract()))
            else:
                platforms = []
        except:
            platforms = ['error']
        
        item['name'] = name
        item['categories'] = categories
        item['review_count'] = review_count
        item['release_date'] = release_date
        item['developers'] = developers
        item['tags'] = tags
        item['price'] = price
        item['platforms'] = platforms

        yield item