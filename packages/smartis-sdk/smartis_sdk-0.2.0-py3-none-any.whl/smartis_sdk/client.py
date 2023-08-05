"""Дополнительные методы Smartis API"""
import json
import time
from enum import Enum

import requests
from pydantic import ValidationError, BaseModel

from .entity import Ads, Ad, Payload
from .entity import Campaigns, Campaign
from .entity import Channels, Placements
from .entity import Keywords, Keyword
from .common import Method
import logging


class ContentType(Enum):
    application = "application/json"


class Client:
    TRY_REQUEST = 10
    REQUEST_PAUSE = 1
    FORCE_PAUSE = 600

    def __init__(self, api_key: str, dev: bool = False) -> None:
        self.api_key = api_key
        self.header = {'Authorization': f"Bearer {api_key}", "Content-Type": ContentType.application.value, }
        if dev:
            self.host = "https://dev.smartis.bi/api/"
        else:
            self.host = "https://my.smartis.bi/api/"

    def get_other(self, method: Method) -> []:
        response = self._prepare(method)
        return response.json()[method.value.location]

    def _prepare(self, method: Method, parameters: str | None = None) -> requests.Response:
        if parameters:
            resp = requests.post(f"{self.host}{method.value.method}", headers=self.header, data=parameters)
        else:
            resp = requests.post(f"{self.host}{method.value.method}", headers=self.header)

        if resp.status_code != 200:
            raise ConnectionError(f"status code: {resp.status_code}")

        return resp

    def get_channels(self) -> Channels:
        response = self._prepare(Method.get_channels)
        try:
            return Channels.model_validate(response.json())
        except ValidationError as e:
            raise ValueError from e

    def get_placements(self) -> Placements:
        response = self._prepare(Method.get_placements)
        try:
            return Placements.model_validate(response.json())
        except ValidationError as e:
            raise ValueError from e

    def get_campaigns(self, campaigns_ids: list) -> list[Campaign]:
        all_campaigns: list[Campaign] = []
        items: Campaigns = self._get_entity(campaigns_ids, Method.get_campaigns, Campaigns)
        all_campaigns.extend(items.campaigns)
        return all_campaigns

    def get_ads(self, ads_ids: list) -> list[Ad]:
        all_ads: list[Ad] = []
        items: Ads = self._get_entity(ads_ids, Method.get_ads, Ads)
        all_ads.extend(items.ads)
        return all_ads

    def _get_entity(self, ids: list, method: Method, model: BaseModel) -> BaseModel:
        ids = json.dumps({"ids": ids})
        response = self._prepare(method, parameters=ids)
        if response.status_code != 200:
            raise ConnectionError(f"status code: {str(response.status_code)}")
        try:
            return model.model_validate(response.json())
        except ValidationError as e:
            raise ValueError from e

    def get_keywords(self, keywords_ids: list) -> list[Keyword]:
        all_keywords: list[Keyword] = []
        items: Keywords = self._get_entity(keywords_ids, Method.get_keywords, Keywords)
        all_keywords.extend(items.keywords)
        return all_keywords

    def status_code_handler(self, response: requests.Response, retry: int) -> None:
        """Обработка статус кодов"""
        if response.status_code == 429:
            if int(response.headers['X-Ratelimit-Remaining']) == 0:
                logging.warning(f"Status code: {response.status_code}. "
                                f"Причина: {response.reason}. "
                                f"Пауза: {response.headers['Retry-After']} с.")
                time.sleep(int(response.headers['Retry-After']))
                logging.info(f"Повтор запроса: {(self.TRY_REQUEST - retry + 1)}"
                             f"/{self.TRY_REQUEST}")
        elif response.status_code in {500, 502}:
            logging.warning(f"Status code: {response.status_code}. "
                            f"Причина: {response.reason}. "
                            f"Пауза: 60 с.")
            time.sleep(60)
        elif response.status_code != 200:
            logging.critical(f" Необработанное исключение. "
                             f"Status code: {response.status_code}. "
                             f"Причина: {response.reason}. ")
            logging.info(response.headers)
            time.sleep(60)

    def get_report(self, payload: Payload, retry: int = TRY_REQUEST) -> requests.Response:
        """Выполнение запросов с обработкой ошибок"""
        payload_json = payload.to_json()
        try:
            time.sleep(self.REQUEST_PAUSE)
            answer = requests.post(f"{self.host}reports/getReport", headers=self.header, data=payload_json)
            self.status_code_handler(answer, self.TRY_REQUEST)
        except Exception as er:
            if retry != 0:
                logging.warning(f"Необработанное исключение. error: {er}")
                logging.info(f"Повтор запроса: {self.TRY_REQUEST - retry + 1}/{self.TRY_REQUEST}")
                return self.get_report(payload, retry=retry - 1)
            else:
                logging.info("Количество ошибок больше заданного! Пауза 10 мин")
                time.sleep(self.FORCE_PAUSE)
                return self.get_report(payload)
        else:
            if answer.status_code == 200:
                return answer
            if retry:
                return self.get_report(payload, retry=(retry - 1))
            logging.warning(f"Количество ошибок подряд достигло {self.TRY_REQUEST}, "
                            f"пауза {self.FORCE_PAUSE / 60} минут")
            time.sleep(self.FORCE_PAUSE)
            self.get_report(payload)
