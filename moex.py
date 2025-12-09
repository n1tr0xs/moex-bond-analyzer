import time
import logging
import requests
from schemas import *

logger = logging.getLogger("MOEX")


class MOEX_API:
    API_DELAY = round(60 / 50, 1)
    BOARDGROUPS = [7, 58, 105]

    def __init__(self):
        """
        Inits MOEX_API.
        """
        self.last_api_request = None
        self.session = requests.Session()

    def get_bonds(self) -> list[Bond]:
        """
        Returns all bonds from all boardgroups specified in `MOEX_API.BOARDGROUPS`.
        """
        bonds = []
        for b in self.BOARDGROUPS:
            bonds.extend(self.get_boardgroup_bonds(b))
        return bonds

    def get_boardgroup_bonds(self, boardgroup: str) -> list[Bond]:
        """
        Returns all bonds from specified boardgroup.
        """
        logger.info(f"Запрос данных для группы {boardgroup}.")
        bonds = []
        securities = self.fetch_boardgroup_securities(boardgroup)
        logger.info(f"В группе {boardgroup} обнаружено {len(securities)} бумаг.")
        for i, ISIN in enumerate(securities, start=1):
            logger.info(f"Обработка {i}/{len(securities)} - {ISIN}.")

            bond_data = securities[ISIN]
            try:
                bonds.append(Bond.from_list(bond_data))
            except Exception as e:
                logger.warning(
                    f"Ошибка при получении информации по {ISIN}. Информация по облигации: {bond_data}."
                )
                logger.exception(e)

        return bonds

    def fetch_boardgroup_securities(self, boardgroup: str) -> dict:
        """
        Returns dictionary of securities found on specified boardgroup.
        Format of dictionary: ISIN -> security_data
        """
        url = f"https://iss.moex.com/iss/engines/stock/markets/bonds/boardgroups/{boardgroup}/securities.json"
        params = {
            "iss.dp": "comma",
            "iss.meta": "off",
            "iss.only": "securities",
            "securities.columns": "SECID,SHORTNAME,FACEVALUE,COUPONVALUE,COUPONPERIOD,MATDATE,PREVLEGALCLOSEPRICE,ACCRUEDINT,FACEUNIT",
        }
        json = self._get_json(url, params=params)
        securities = json.get("securities", {}).get("data", {})
        return {item[0]: item for item in securities}

    def _get_json(self, url: str, params: dict | None = None) -> dict:
        """
        Returns JSON from the specified URL, taking into account the delay between requests.
        """
        self._respect_rate_limit()
        response = self._send_request(url, params=params)
        if not response:
            return {}
        return self._parse_json(response)

    def _respect_rate_limit(self) -> None:
        """
        Waits time if needed to respect requests rate limit.
        """
        now = datetime.datetime.now()
        if self.last_api_request:
            delta = (now - self.last_api_request).total_seconds()
            wait_time = self.API_DELAY - delta
            if wait_time > 0:
                logger.info(f"Ожидание {wait_time:.2f} секунд...")
                time.sleep(self.API_DELAY - delta)

        self.last_api_request = datetime.datetime.now()

    def _send_request(
        self, url: str, params: dict | None = None
    ) -> requests.Response | None:
        r = requests.Request("GET", url, params=params)
        prepared = self.session.prepare_request(r)

        logger.info(f"Запрос к {prepared.url}.")

        try:
            response = self.session.send(prepared)
            response.raise_for_status()
            return response
        except:
            logger.warning(f"Не удалось установить соединение.")
            return None

    def _parse_json(self, response: requests.Response) -> dict:
        try:
            return response.json()
        except:
            logger.warning(f"Не удалось получить json.")
            return {}
