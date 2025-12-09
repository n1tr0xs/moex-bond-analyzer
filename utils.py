import logging
import requests
import copy
from bs4 import BeautifulSoup
from schemas import Bond, SearchCriteria

logger = logging.getLogger("Utils")


def filter_bonds(bonds: list[Bond], criteria: SearchCriteria) -> list[Bond]:
    """
    Filters given bonds by specified criteria.

    :param bonds: List of bond to filter.
    :type bonds: list[Bond]
    :param criteria: Criterias for filtering.
    :type criteria: SearchCriteria
    :return: List of bonds filtered by specidifed criteria.
    :rtype: list[Bond]
    """
    filtered_bonds = []
    for bond in bonds:
        if not (criteria.min_days_to_maturity <= bond.days_to_maturity):
            logger.info(f"Облигация {bond.ISIN} не прошла проверку по сроку погашения.")
            continue
        if not (bond.days_to_maturity <= criteria.max_days_to_maturity):
            logger.info(f"Облигация {bond.ISIN} не прошла проверку по сроку погашения.")
            continue
        if not (criteria.min_bond_yield <= bond.approximate_yield):
            logger.info(f"Облигация {bond.ISIN} не прошла проверку по доходности.")
            continue
        if not (criteria.face_units is None or bond.face_unit in criteria.face_units):
            logger.info(f"Облигация {bond.ISIN} не прошла проверку по валюте.")
            continue

        logger.info(f"Облигация {bond.ISIN} прошла проверку критериев.")
        filtered_bonds.append(bond)
    return filtered_bonds


def with_credit_scores(bonds: list[Bond]) -> list[Bond]:
    """
    Adds credit scores to all bonds in the list.

    :param bonds: List of Bond objects.
    :type bonds: list[Bond]
    :return: New list of Bond objects with `credit_score` attribute added.
    :rtype: list[Bond]
    """
    new_bonds = copy.deepcopy(bonds)
    for bond in new_bonds:
        bond.credit_score = _get_credit_score_SMARTLAB(bond.ISIN)
    return new_bonds


def _get_credit_score_SMARTLAB(ISIN: str) -> str:
    """
    Fetches the credit score of a bond issuer from Smart-Lab by ISIN.

    :param ISIN: ISIN of the bond.
    :type ISIN: str
    :return: Credit score as string. Returns 'Неизвестно' if not found.
    :rtype: str
    """
    logger.info(f"Получение кредитного рейтинга эмитента облигации {ISIN}.")
    BASE_URL = "https://smart-lab.ru/q/bonds/{}"
    response = requests.get(BASE_URL.format(ISIN))
    soup = BeautifulSoup(response.text, "lxml")
    score = "Неизвестно"  # Default value
    try:
        div = soup.find("div", text="Кредитный рейтинг")
        score = div.find_next().text.strip()
        logger.info(f"Кредитный рейтинг эмитента облигации {ISIN} - {score}.")
    except AttributeError as e:
        logger.info(f"Кредитный рейтинг эмитента облигации {ISIN} не известен.")
        logger.exception(e)
    except Exception as e:
        logger.exception(e)
    return score
