import gzip
import json
import random
import time
from functools import reduce
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from commons.configuration_reader import read_configuration, Config
from commons.countable_processor import CountableProcessor, ExceptionStrategy
from commons.logger import get_logger
from commons.optional import of
from dict_util import get_path_or_default


class LoadException(Exception):
    pass


class ApiResponse:

    def __init__(self, content, headers):
        self.content = content
        self.headers = headers

    def content_encoding(self):
        return self.headers['content-encoding'] if 'content-encoding' in self.headers else ""


class HttpClient:

    def call(self, req) -> ApiResponse:
        pass


class UrlHttpClient(HttpClient):

    def __init__(self):
        self.logger = get_logger("UrlHttpClient")

    def call(self, req):
        try:
            response = urlopen(req)
            return ApiResponse(response.read(), response.headers)
        except HTTPError as e:
            self.logger.error("call", f"Call {req.full_url} failed. Reason: {e.reason} body: {e.read()}")
            raise e


class RequestFactory:

    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger("RequestFactory")

    def items_request(self, iterable) -> Request:
        url = self._prepare_items_api_url(iterable)
        return self._prepare_request(url)

    def details_request(self, item) -> Request:
        url = self._prepare_details_api_url(item)
        return self._prepare_request(url)

    def _prepare_request(self, url: str) -> Request:
        self.logger.info("_prepare_request", f'{url}')
        req = Request(url)
        self._add_headers(req)
        return req

    def _prepare_items_api_url(self, iterable):
        url = self.config.get_value("items_api.url")
        placeholders = self.config.get_value("items_api.placeholders", {})
        placeholders_global = self.config.get_value("api.placeholders", {})
        url = self._resolve_placeholders(url, placeholders_global, iterable=iterable)
        url = self._resolve_placeholders(url, placeholders, iterable=iterable)
        params = self._resolve_query_params(iterable)
        url += "?" + "&".join(params)
        return url

    def _prepare_details_api_url(self, item: dict):
        url = self.config.get_value("details_api.url")
        placeholders = self.config.get_value("details_api.placeholders", {})
        placeholders_global = self.config.get_value("api.placeholders", {})
        url = self._resolve_placeholders(url, placeholders_global, item=item)
        url = self._resolve_placeholders(url, placeholders, item=item)
        return url

    def _add_headers(self, req):
        headers_map = self.config.get_value("api.headers.map", {})
        for key in headers_map:
            req.add_header(key, headers_map[key])
        headers_curl = self.config.get_value("api.headers.curl")
        for header in headers_curl.split(" -H "):
            if header != '':
                header_parts = header[1:][:-1].split(":", 1)
                req.add_header(header_parts[0].strip(), header_parts[1].strip())

    def _resolve_query_params(self, iterable):
        query_params = self.config.get_value("items_api.query_params", {})
        params = []
        for key in query_params:
            value = query_params[key]
            if value == '{iterable}':
                value = iterable
            params.append(f'{key}={value}')
        return params

    def _resolve_placeholders(self, url, placeholders, iterable=None, item=None):
        for key in placeholders:
            value = placeholders[key]
            if value == '{iterable}':
                value = iterable
            if value.startswith("$"):
                value = get_path_or_default(item, value, "")
            url = url.replace("{" + key + "}", value)
        return url


class ItemLoader:

    def __init__(self, config: Config, client: HttpClient):
        self.config = config
        self.client = client
        self.request_factory = RequestFactory(config)
        self.logger = get_logger("ItemLoader")

    def load_items(self, stored_items_by_id: dict) -> list[dict]:
        all_items = self._get_pages()
        return CountableProcessor(lambda x: self._load(x, stored_items_by_id), strategy=ExceptionStrategy.ASK).run(
            all_items)

    def _get_pages(self) -> list:
        current_page = 0
        page = self._get_page(current_page)
        first_page_items = get_path_or_default(page, self.config.get_value("items_api.response.return"), [])
        total_pages = get_path_or_default(page, self.config.get_value("items_api.response.total_pages"), 0)
        executions = []
        for i in range(total_pages):
            executions.append(i + 1)
        items = CountableProcessor(lambda x: self._get_page_items(x), strategy=ExceptionStrategy.ASK).run(
            executions)
        items.append(first_page_items)
        return reduce(list.__add__, items)

    def _load(self, item, cached_items: dict) -> dict:
        items_save_as = self.config.get_value("items_api.save_as")
        details_save_as = self.config.get_value("details_api.save_as")
        id_provider = self.config.get_value("items_api.response.id")
        item_id = get_path_or_default(item, id_provider, "")
        if item_id in cached_items:
            self.logger.info("_load", f"Details {item_id} is cached")
            return cached_items[item_id]
        details = self._get_details(item)
        return {"id": item_id, items_save_as: item, details_save_as: details}

    def _get_page_items(self, current_page):
        page = self._get_page(current_page)
        return get_path_or_default(page, self.config.get_value("items_api.response.return"), [])

    def _get_page(self, iterable: int) -> dict:
        delay = of(self.config.get_value("items_api.delay", None))
        delay.if_present(lambda x: time.sleep(random.randint(x['min'], x['max'])))
        request = self.request_factory.items_request(iterable)
        response = self.client.call(request)
        return self._get_response(response)

    def _get_details(self, item: dict):
        try:
            delay = of(self.config.get_value("details_api.delay", None))
            delay.if_present(lambda x: time.sleep(random.randint(x['min'], x['max'])))
            request = self.request_factory.details_request(item)
            response = self.client.call(request)
            return self._get_response(response)
        except Exception as e:
            self.logger.error("_load", f"An exception occurred when get details. {e}")
            raise LoadException(f"An exception occurred when get details")

    def _get_response(self, response):
        if response.content_encoding() == "gzip":
            return json.loads(gzip.decompress(response.content))
        return json.loads(response.content)


if __name__ == '__main__':
    config = read_configuration("config").get('loader')
    items = ItemLoader(config, UrlHttpClient()).load_items({})
    print(str(items))
