import logging
import random

from curl_cffi import requests as cffi_requests
from scrapy.http import HtmlResponse, TextResponse

logger = logging.getLogger(__name__)

# Rotate between common browser profiles to avoid fingerprint consistency
IMPERSONATIONS = [
    "chrome124", "chrome120", "chrome110",
    "safari17_0", "safari15_5",
    "firefox133",
]


class CurlCffiMiddleware:
    """Replace Scrapy's HTTP engine with curl_cffi.

    curl_cffi impersonates real browser TLS/JA3 fingerprints,
    bypassing Cloudflare and other bot-detection layers.
    """

    def process_request(self, request, spider):
        impersonate = random.choice(IMPERSONATIONS)
        logger.debug("curl_cffi [%s] %s", impersonate, request.url)

        # Scrapy headers have list values — flatten to strings for curl_cffi
        headers = {
            k.decode() if isinstance(k, bytes) else k:
            (v[-1].decode() if isinstance(v[-1], bytes) else v[-1])
            for k, v in request.headers.items()
            if v
        }

        try:
            resp = cffi_requests.get(
                request.url,
                headers=headers,
                impersonate=impersonate,
                timeout=30,
                allow_redirects=True,
            )
        except Exception as e:
            logger.warning("curl_cffi error for %s: %s", request.url, e)
            raise

        content_type = resp.headers.get("content-type", "")
        cls = HtmlResponse if "html" in content_type else TextResponse

        # Flatten headers — curl_cffi may return multi-value lists
        headers = {k: v if isinstance(v, str) else v[-1] if isinstance(v, list) else str(v)
                   for k, v in resp.headers.items()}

        return cls(
            url=resp.url,
            status=resp.status_code,
            headers=headers,
            body=resp.content,
            encoding="utf-8",
            request=request,
        )
