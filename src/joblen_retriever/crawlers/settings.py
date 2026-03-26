BOT_NAME = "joblen"
SPIDER_MODULES = ["joblen_retriever.crawlers.spiders"]

# Be polite — randomised delay between requests
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10

# Use curl_cffi for all HTTP — bypasses TLS fingerprinting / Cloudflare
DOWNLOADER_MIDDLEWARES = {
    "joblen_retriever.crawlers.middlewares.CurlCffiMiddleware": 543,
    # disable Scrapy's built-in HTTP handler
    "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": None,
}

# Store jobs straight to Postgres
ITEM_PIPELINES = {
    "joblen_retriever.crawlers.pipelines.PostgresPipeline": 300,
}

ROBOTSTXT_OBEY = False
LOG_LEVEL = "INFO"
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
