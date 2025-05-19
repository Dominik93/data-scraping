import gzip
import json
import random
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from configuration_reader import read_configuration
from count_executor import provide_countable
from dict_util import _get_path_or_default


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

    def call(self, req):
        try:
            response = urlopen(req)
            return ApiResponse(response.read(), response.headers)
        except HTTPError as he:
            print(he.reason)
            print(he.read())
            raise


class ItemLoader:

    def __init__(self, config: dict, client: HttpClient):
        self.config = config
        self.client = client

    def load_items(self, cached_items: dict) -> list[dict]:
        items = self._get_pages()
        return provide_countable(items, lambda x: self._load(x, cached_items))

    def _load(self, item, cached_items: dict) -> dict:
        items_save_as = self.config['items_api']['save_as']
        details_save_as = self.config['details_api']['save_as']
        id_provider = self.config['items_api']['response']['id']
        item_id = _get_path_or_default(item, id_provider, "")
        if item_id in cached_items:
            print(f"Details {item_id} is cached")
            return cached_items[item_id]
        details = self._get_details(item)
        return {"id": item_id, items_save_as: item, details_save_as: details}

    def _get_pages(self) -> list:
        response = self.config['items_api']['response']
        items = []
        current_page = 0
        page = self._get_page(current_page)
        items.extend(_get_path_or_default(page, response['return'], []))
        total_pages = _get_path_or_default(page, response['total_pages'], 0)
        while current_page < total_pages:
            current_page += 1
            next_page = self._get_page(current_page)
            items.extend(_get_path_or_default(next_page, response['return'], []))
            print(f"{current_page}/{total_pages}")
        return items

    def _get_page(self, iterable: int) -> dict:
        delay = self.config['items_api']['delay']
        url = self._prepare_items_api_url(iterable)
        print(f'{url}')
        time.sleep(random.randint(delay['min'], delay['max']))
        req = self._prepare_request(url)
        response = self.client.call(req)
        return self._get_response(response)

    def _prepare_items_api_url(self, iterable):
        url = self.config['items_api']['url']
        placeholders = self.config['items_api']['placeholders']
        query_params = self.config['items_api']['query_params']
        for key in placeholders:
            value = placeholders[key]
            if value == '{iterable}':
                value = iterable
            url = url.replace("{" + key + "}", value)
        params = []
        for key in query_params:
            value = query_params[key]
            if value == '{iterable}':
                value = iterable
            params.append(f'{key}={value}')
        url += "?" + "&".join(params)
        return url

    def _prepare_details_api_url(self, item: dict):
        url = self.config['details_api']['url']
        placeholders = self.config['details_api']['placeholders']
        for key in placeholders:
            value = placeholders[key]
            if value.startswith("$"):
                value = _get_path_or_default(item, value, "")
            url = url.replace("{" + key + "}", value)
        return url

    def _get_details(self, item: dict):
        try:
            url = self._prepare_details_api_url(item)
            print(f'{url}')
            req = self._prepare_request(url)
            delay = self.config['details_api']['delay']
            time.sleep(random.randint(delay['min'], delay['max']))
            response = self.client.call(req)
            return self._get_response(response)
        except Exception as e:
            print(f"An exception occurred when get details. {e}")
            raise LoadException(f"An exception occurred when get details")

    def _get_response(self, response):
        if response.content_encoding() == "gzip":
            return json.loads(gzip.decompress(response.content))
        return json.loads(response.content)

    def _prepare_request(self, url: str) -> Request:
        req = Request(url)
        headers = self.config['api']['headers']
        for key in headers:
            req.add_header(key, headers[key])
        return req


if __name__ == '__main__':
    config = read_configuration()['loader']
    items = ItemLoader(config, UrlHttpClient()).load_items({})
    print(str(items))
