import base64
import json
from collections import defaultdict
from itertools import chain
from typing import Any, List, Optional
from urllib.parse import urlparse

import django.urls.exceptions
import redis
import requests
from decouple import config
from melon_translate_client.common.exceptions import (
    TranslationKeyNotFound,
    TranslationObjectNotFound,
)
from melon_translate_client.utils.logging import log
from redis.client import Pipeline
from rest_framework.exceptions import ValidationError


class Client:
    """TranslateClient utils class."""

    timeout = config("REQUESTS_TIMEOUT", default=30, cast=int)

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(
        self,
        service_address: str = config(
            "TRANSLATE_ADDRESS", default="127.0.0.1", cast=str
        ),
        service_port: int = config("TRANSLATE_PORT", default=80, cast=int),
        cache_address: str = config("REDIS_HOST", default="127.0.0.1", cast=str),
        cache_port: int = config("REDIS_PORT", default=6379, cast=int),
        cache_view_ttl: int = config("CACHE_VIEW_TTL", default=2700, cast=int),
        cache_occurrence_ttl: int = config(
            "CACHE_OCCURRENCE_TTL", default=2700, cast=int
        ),
        cache_group_key_ttl: int = config(
            "CACHE_GROUP_KEY_TTL", default=2700, cast=int
        ),
    ):
        """
        Constructor method for melon-translate.Client class.

        :param service_address: Host address for melon-translate.
        :param service_port: Host port for melon-translate.
        :param cache_address: Host address for REDIS.
        :param cache_port: Host port for REDIS.
        :param cache_view_ttl: TTL for views reverse map cached in REDIS
        :param cache_occurrence_ttl: TTL for occurrences reverse map cached in REDIS
        :param cache_group_key_ttl: General TTL value
        """
        self.address = service_address
        self.port = service_port
        self.cache_address = cache_address
        self.cache_port = cache_port
        self.cache = redis.Redis(
            host=cache_address,
            port=cache_port,
            decode_responses=True,
            socket_timeout=15,
            socket_connect_timeout=15,
            max_connections=7500,
        )
        self.cache_view_ttl = cache_view_ttl
        self.cache_occurrence_ttl = cache_occurrence_ttl
        self.cache_group_key_ttl = cache_group_key_ttl
        self.pipeline = self.cache.pipeline()

    @staticmethod
    def __stringify(collection: List[Any]) -> List[str]:
        """Ensure items of a collection are stringified."""
        return [str(item) for item in collection]

    @staticmethod
    def __build_params(
        views: List[str],
        occurrences: List[str],
        snake_keys: List[str],
        page_size: int = None,
        page: int = None,
    ) -> dict:
        """Build HTTP params."""
        params = {}
        if views:
            params["views"] = views

        if occurrences:
            params["occurrences"] = occurrences

        if snake_keys:
            params["snake_keys"] = snake_keys

        if page_size and page:
            params["page_size"] = page_size
            params["page"] = page

        return params

    def __hash(self, *hashes) -> str:
        """Hash a collection."""
        return base64.b64encode(
            bytes(":".join(self.__stringify(hashes)), "utf-8")
        ).decode("utf-8")

    def __expire(self, *hashes: List[str]):
        """Expire given hash maps in cache."""
        for _hash in hashes:
            self.cache.expire(_hash, self.cache_group_key_ttl)

    def _filter_url(self, language) -> str:
        """Get service filter URL location.

        :returns: url for the `filter` request
        """
        _url = urlparse(f"{self.address}:{self.port}/api/v1/translations/{language}/")
        return _url.geturl()

    def __set_view(self, language: str, view: str, ids: List[str]) -> Pipeline:
        """Set view with specified TTL."""
        return self.pipeline.set(
            f"{self.__hash(language, view)}",
            ",".join(self.__stringify(ids)),
            ex=self.cache_view_ttl,
        )

    def __set_occurrence(
        self, language: str, occurence: str, ids: List[str]
    ) -> Pipeline:
        """Set occurrence with specified TTL."""
        return self.pipeline.set(
            f"{self.__hash(language, occurence)}",
            ",".join(self.__stringify(ids)),
            ex=self.cache_occurrence_ttl,
        )

    def __load_keys(self, keys: List[str]) -> dict:
        """Load keys from cache."""
        if isinstance(keys, str):
            keys = keys.split(",")

        _records = [json.loads(self.cache.get(key)) for key in keys]

        return {record.get("id"): record for record in _records}

    def _get_all_pages(
        self,
        language: str,
        views: Optional[List[str]] = None,
        occurrences: Optional[List[str]] = None,
        snake_keys: Optional[List[str]] = None,
        page_size: int = 500,
        page: int = 1,
        chain_together: bool = True,
    ) -> Optional[list]:
        """
        This method paginates response and returns list of lists of pages
        """
        url: str = self._filter_url(language)
        params = self.__build_params(views, occurrences, snake_keys, page_size, page)

        response = requests.get(url, params=params, timeout=Client.timeout).json()
        if not response.get("results"):
            return None

        results = [
            response,
        ]
        count = response.get("count")
        next_page = response.get("links", {}).get("next")

        while next_page:
            response = requests.get(next_page, timeout=Client.timeout).json()
            results.append(response)

            page_num = response.get("pages").get("current")
            next_page = response.get("links", {}).get("next")
            log.debug(f"Page {page_num} for {language} language.")

        log.debug(
            f"There are no more pages. Total count is {count} translations with {params.get('views')} views \n"
            f"for {language} language."
        )

        if chain_together:
            return list(
                chain.from_iterable([result.get("results") for result in results])
            )

        return results

    def _remove_existing_keys(self, language: str, translations: List[dict]):
        """
        Check if  retrieved translations are already cached in REDIS.
        Returns a list of translations that are not cached.
        """
        _SNAKE_NAME_MAP = f"{language}_snake_name"

        _already_cached = []
        _new_keys = []
        snake_name_map = self.cache.hgetall(_SNAKE_NAME_MAP)

        for translate in translations:
            _id = translate.get("id")
            _key = translate.get("key")
            _snake = _key.get("snake_name")
            _views = _key.get("views")
            _occurrences = _key.get("occurrences")

            if not _id:
                break
            if not _views and not _occurrences:
                continue

            if _snake in snake_name_map.keys():
                _already_cached.append(_id)
            else:
                _new_keys.append(translate)

        log.info(f"Number of already cached translations: {len(_already_cached)}")
        log.info(f"Number of new translations to cache: {len(_new_keys)}")

        return _new_keys, _already_cached

    def snake_key(self, language: str, key: str) -> Optional[dict]:
        """Retrieve a snake key."""
        _SNAKE_NAME_MAP = f"{language}_snake_name"
        _VIEWS_ID_MAP = f"{language}_views"
        _OCCURRENCES_ID_MAP = f"{language}_occurrences"

        record_id = self.cache.hget(_SNAKE_NAME_MAP, key)
        if not record_id:
            log.debug(f"Key {key} could not be found.")
            raise TranslationKeyNotFound(
                f"No keys were found in REDIS hash map {_SNAKE_NAME_MAP} for key {key}"
            )

        record = json.loads(self.cache.get(record_id))
        if not record or not record.get("key"):
            raise TranslationObjectNotFound(
                f"No objects were found in REDIS for {record_id} and key {key}"
            )

        # NOTE: 1. Compute which views needs refreshing and refresh them and all associations.
        keys_views = record.get("key").get("views") or []

        # Extract views and cache them if they are not present in hash map
        views = [
            view
            for view in keys_views
            if not self.cache.exists(self.__hash([language, view]))
        ]
        if views and not self.cache.hget(_VIEWS_ID_MAP, record_id):
            log.debug(f"Caching views {views} for {language} language")
            _ = self.filter(language, views=views)

        # NOTE: 2. Compute which occurrences need refreshing and refresh them and all associations.
        key_occurrences = record.get("key").get("occurrences") or []

        # Extract occurrences and cache them if they are not present in hash map
        occurrences = [
            occurrence
            for occurrence in key_occurrences
            if not self.cache.exists(self.__hash([language, occurrence]))
        ]
        if occurrences and not self.cache.hget(_OCCURRENCES_ID_MAP, record_id):
            log.debug(f"Caching occurrences {occurrences} for {language} language")
            _ = self.filter(
                language,
                occurrences=occurrences,
            )

        return record

    def id_name(self, language: str, key: str) -> Optional[dict]:
        """Retrieve a id_name."""
        _ID_NAME_MAP = f"{language}_id_name"
        _VIEWS_ID_MAP = f"{language}_views"
        _OCCURRENCES_ID_MAP = f"{language}_occurrences"

        record_id = self.cache.hget(_ID_NAME_MAP, key)
        if not record_id:
            log.debug(f"Key {key} could not be found.")
            raise TranslationKeyNotFound(
                f"No keys were found in REDIS hash map {_ID_NAME_MAP} for key {key}"
            )

        record = json.loads(self.cache.get(record_id))
        if not record or not record.get("key"):
            raise TranslationObjectNotFound(
                f"No objects were found in REDIS for {record_id} and key {key}"
            )

        # NOTE: 1. Compute which views needs refreshing and refresh them and all associations.
        keys_views = record.get("key").get("views") or []

        # Extract views and cache them if they are not present in hash map
        views = [
            view
            for view in keys_views
            if not self.cache.exists(self.__hash([language, view]))
        ]
        if views and not self.cache.hget(_VIEWS_ID_MAP, record_id):
            log.debug(f"Caching views {views} for {language} language")
            _ = self.filter(language, views=views)

        # NOTE: 2. Compute which occurrences need refreshing and refresh them and all associations.
        key_occurrences = record.get("key").get("occurrences") or []

        # Extract occurrences and cache them if they are not present in hash map
        occurrences = [
            occurrence
            for occurrence in key_occurrences
            if not self.cache.exists(self.__hash([language, occurrence]))
        ]
        if occurrences and not self.cache.hget(_OCCURRENCES_ID_MAP, record_id):
            log.debug(f"Caching occurrences {occurrences} for {language} language")
            _ = self.filter(
                language,
                occurrences=occurrences,
            )

        return record

    def filter(
        self,
        language: str,
        views: Optional[List[str]] = None,
        occurrences: Optional[List[str]] = None,
        snake_keys: Optional[List[str]] = None,
        keys_number: int = 500,
        no_cache: bool = False,
        page_size: int = 500,
        page: int = 1,
    ):
        """
        Filters translations by language, views and occurrences, and caches then in REDIS.
        """

        if not language:
            raise django.urls.exceptions.NoReverseMatch("No language selected.")

        if (
            views is None and occurrences is None and snake_keys is None
        ):  # NOTE: If no filtering parameters given, query service directly.
            no_cache = True

        # NOTE: This part potentially still needs auto-pagination for the query
        if no_cache:
            return requests.get(
                self._filter_url(language),
                params=self.__build_params(
                    views, occurrences, snake_keys, page_size, page
                ),
                timeout=Client.timeout,
            )

        if snake_keys and len(snake_keys) > keys_number:
            raise ValidationError(
                f"Number of keys is greater than {keys_number}. Override the keys_number parameter."
            )

        # NOTE: Reverse indexes for lookup of individual keys through `snake_name` or `id_name`.
        # One instance always needs to exists, therefore we never set the TTL on them.
        # However, during the fetching we always check if the `id` exists in grouped indices,
        # which has TTL set to `CACHE_GROUP_KEY_TTL`.
        _SNAKE_NAME_MAP = f"{language}_snake_name"
        _ID_NAME_MAP = f"{language}_id_name"

        # NOTE: Group (and reverse) indexes of views and occurrences for a language.
        _VIEWS_ID_MAP = f"{language}_views"
        _OCCURRENCES_ID_MAP = f"{language}_occurrences"

        def _cache_update(params):
            _cache = {}
            for param in params:
                new_hash = self.__hash(language, param)
                if new_hash in self.cache:
                    _cache.update(self.__load_keys(self.cache.get(new_hash)))

                    # NOTE: Fetched from cache. Remove from fetching list.
                    params.remove(param)

            return _cache

        def _cache_warmup():
            """Closure for prebuilding the result object."""
            _cache = {}

            # 1. Check if any of the specified views is cached.
            if views:
                _cache = _cache_update(views)

            # 2. Check if any of the specified occurrences is cached.
            if occurrences:
                _cache = _cache_update(occurrences)

            # 3. Check if any of the specified snake_keys are cached.
            if snake_keys:
                _cache = _cache_update(snake_keys)

            return _cache

        def _cache_translations(translations: List[dict]):
            """Cache retrieved translations"""
            _cache = {}

            # 4. Compute the caching.
            views, occurrences = defaultdict(list), defaultdict(list)

            for translate in translations:
                _id = translate.get("id")
                if not _id:
                    continue
                _cache[_id] = translate
                _key = translate.get("key")
                _snake = _key.get("snake_name")
                _id_name = _key.get("id_name")
                _views = _key.get("views") or []
                _occurrences = _key.get("occurrences") or []

                data = json.dumps(translate)
                self.pipeline.set(_id, data)

                if _snake:
                    self.pipeline.hset(_SNAKE_NAME_MAP, _snake, _id)

                if _id_name:
                    self.pipeline.hset(_ID_NAME_MAP, _id_name, _id)

                for view in _views:
                    views[view].append(_id)
                    self.pipeline.hset(_VIEWS_ID_MAP, _id, view)

                for occurrence in _occurrences:
                    occurrences[occurrence].append(_id)
                    self.pipeline.hset(_OCCURRENCES_ID_MAP, _id, occurrence)

            # NOTE: Cache freshly retrieved items.
            for view, keys in views.items():
                self.__set_view(language, view, ids=keys)

            for occurrence, keys in occurrences.items():
                self.__set_occurrence(language, occurrence, ids=keys)

            self.pipeline.execute()
            self.__expire(_VIEWS_ID_MAP)
            self.__expire(_OCCURRENCES_ID_MAP)

            return _cache

        # 5. Fetch the remaining items.
        translations = self._get_all_pages(
            language, views, occurrences, snake_keys, page_size, page
        )
        if not translations:
            raise RuntimeError(
                "missing translations - initialize translation with management command"
            )

        result = _cache_warmup()

        log.info(f"Number of fetched translations: {len(translations)}")

        translations_for_caching, cached_ids = self._remove_existing_keys(
            language, translations
        )

        if translations_for_caching:
            # 6. Cache new translations and assemble output.
            log.info(
                f"Caching {len(translations_for_caching)} translations for {language} language..."
            )
            result = {**result, **_cache_translations(translations_for_caching)}
            log.info(f"Done. Cached {len(result.items())} translation items.")
        else:
            if views:
                for view in views:
                    for _id in cached_ids:
                        if not self.cache.hget(_VIEWS_ID_MAP, _id):
                            self.pipeline.hset(_VIEWS_ID_MAP, _id, view)
            if occurrences:
                for occ in occurrences:
                    for _id in cached_ids:
                        if not self.cache.hget(_OCCURRENCES_ID_MAP, _id):
                            self.pipeline.hset(_OCCURRENCES_ID_MAP, _id, occ)
            self.pipeline.execute()
            self.__expire(_VIEWS_ID_MAP)
            self.__expire(_OCCURRENCES_ID_MAP)

            result = {}
            log.info("There are no new translations to cache!")

        return result

    def get_translation_keys(self, language, view) -> dict:
        """
        Get translation keys dictionary with snake_names and translations from REDIS for a provided language and view
        """

        _SNAKE_NAME_MAP = f"{language}_snake_name"
        keys_dict = {}

        snake_names = self.cache.hgetall(_SNAKE_NAME_MAP)
        temp_pipeline = self.cache.pipeline()

        for value in snake_names.values():
            temp_pipeline.get(value)

        obj_list = temp_pipeline.execute()

        for obj in obj_list:
            obj = json.loads(obj)
            keys = obj.get("key")
            views = keys.get("views") or []
            if view in views:
                keys_dict[keys.get("snake_name")] = obj.get("translation")

        return keys_dict
