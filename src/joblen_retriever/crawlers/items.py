import scrapy


class JobItem(scrapy.Item):
    source_name = scrapy.Field()
    external_id = scrapy.Field()
    title       = scrapy.Field()
    company     = scrapy.Field()
    location    = scrapy.Field()
    url         = scrapy.Field()
    description = scrapy.Field()
    tags        = scrapy.Field()
    salary_range = scrapy.Field()
    posted_at   = scrapy.Field()
    country     = scrapy.Field()
