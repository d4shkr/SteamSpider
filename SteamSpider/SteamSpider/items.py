import scrapy


class SteamspiderItem(scrapy.Item):
    name = scrapy.Field()
    categories = scrapy.Field()
    review_count = scrapy.Field()
    release_date = scrapy.Field()
    developers = scrapy.Field()
    tags = scrapy.Field()
    price = scrapy.Field()
    platforms = scrapy.Field()
