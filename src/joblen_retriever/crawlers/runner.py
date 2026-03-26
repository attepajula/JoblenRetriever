import logging
import sys

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from .settings import *  # noqa: F401, F403 — populate scrapy settings module

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s", datefmt="%H:%M:%S")

SPIDERS = {
    "linkedin": "joblen_retriever.crawlers.spiders.linkedin.LinkedInSpider",
}


def main():
    names = sys.argv[1:] or list(SPIDERS)
    process = CrawlerProcess(settings={
        "BOT_NAME": "joblen",
        "SPIDER_MODULES": ["joblen_retriever.crawlers.spiders"],
        "DOWNLOADER_MIDDLEWARES": {
            "joblen_retriever.crawlers.middlewares.CurlCffiMiddleware": 543,
            "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": None,
        },
        "ITEM_PIPELINES": {
            "joblen_retriever.crawlers.pipelines.PostgresPipeline": 300,
        },
        "DOWNLOAD_DELAY": 2,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "AUTOTHROTTLE_ENABLED": True,
        "ROBOTSTXT_OBEY": False,
        "LOG_LEVEL": "INFO",
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    })

    for name in names:
        if name not in SPIDERS:
            print(f"Unknown spider: {name}. Available: {', '.join(SPIDERS)}")
            continue
        spider_cls_path = SPIDERS[name]
        module, cls_name = spider_cls_path.rsplit(".", 1)
        import importlib
        cls = getattr(importlib.import_module(module), cls_name)
        process.crawl(cls)

    process.start()


if __name__ == "__main__":
    main()
