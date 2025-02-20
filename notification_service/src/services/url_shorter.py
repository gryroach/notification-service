# stdlib
import logging

# thirdparty
import pyshorteners
from pydantic import HttpUrl, ValidationError

# project
from core.config import ShortenerService, settings

logger = logging.getLogger(__name__)


class URLShortener:
    def __init__(self, service: ShortenerService = settings.shortener_service):
        self.shortener = pyshorteners.Shortener(api_key=settings.shortener_api_key, login=settings.shortener_login)
        self.service = service

    def shorten_url(self, url: str) -> str:
        try:
            HttpUrl(url)
        except ValidationError:
            logger.warning(f"Invalid URL: {url}")
            return url
        try:
            method = getattr(self.shortener, self.service)
            short_url = method.short(url)
            return short_url
        except Exception as e:
            logger.warning(f"Failed to shorten URL {url}: {e}", exc_info=True)
            return url
