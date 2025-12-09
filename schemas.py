from dataclasses import dataclass
import datetime


@dataclass
class SearchCriteria:
    """
    Search criterias dataclass.

    Args:
        min_bond_yield (float): Minimum bond approximate yield.
        min_days_to_maturity (float): Minimum days to bond maturity.
        max_days_to_maturity (float): Maximum days to bond maturity.
        face_units (list[str]): Allowed face units for bond. Defaults to "SUR". Use None if you don't care about face units.
    """

    min_bond_yield: float = 0
    min_days_to_maturity: float = 1
    max_days_to_maturity: float = float("inf")
    face_units: list[str] | None = ("SUR",)  # Use None if don't care about face unit


class Bond:
    """
    Bond class.
    """

    BROKER_FEE = 0.25 / 100

    def __init__(
        self,
        ISIN: str,
        name: str,
        face_value: float,
        coupon_value: float,
        coupon_period: int,
        maturity_date: datetime.date,
        price: float,
        ACI: float,
        face_unit: str,
        credit_score: str | None = None,
    ):
        """
        Initialize Bond.

        :param ISIN: Bond ISIN.
        :type ISIN: str
        :param name: Bond name.
        :type name: str
        :param face_value: Bond face value. Defaults to 0.
        :type face_value: float
        :param coupon_value: Bond coupons face value. Defaults to 0.
        :type coupon_value: float
        :param coupon_period: Bond coupons period. Defaults to +infinity.
        :type coupon_period: int
        :param maturity_date: Bond maturity date.
        :type maturity_date: datetime.date
        :param price: Bond current price in percents. Defaults to +intfinity.
        :type price: float
        :param ACI: Bond accumalated coupond income for now.
        :type ACI: float
        :param face_unit: Bond face unit.
        :type face_unit: str
        :param credit_score: Bond credit score.
        :type credit_score: str | None
        """
        self.ISIN: str = ISIN
        self.bond_name: str = name
        self.face_value: float = face_value or 0
        self.coupon_value: float = coupon_value or 0
        self.coupon_period: int = coupon_period or float("inf")
        self.maturity_date: datetime.date = maturity_date
        self.bond_price: float = price or float("inf")
        self.ACI: float = ACI
        self.face_unit: str = face_unit
        self.credit_score: str = credit_score

    @classmethod
    def from_list(cls, data: list):
        return cls(
            ISIN=data[0],
            name=data[1],
            face_value=float(data[2]),
            coupon_value=float(data[3]),
            coupon_period=float(data[4]),
            maturity_date=datetime.datetime.strptime(data[5], "%Y-%m-%d").date(),
            price=float(data[6]),
            ACI=float(data[7]),
            face_unit=data[8],
        )

    @classmethod
    def headers(cls):
        return [
            "Наименование",
            "Кредитный рейтинг эмитента",
            "ISIN",
            "Номинал",
            "Цена на бирже",
            "Номинал купона",
            "Дней до погашения",
            "Доходность к погашению",
            "Валюта",
        ]

    @property
    def as_list(self) -> list:
        return [
            self.bond_name,
            self.credit_score or "Неизвестно",
            self.ISIN,
            self.face_value,
            self.broker_price,
            self.coupon_value,
            self.days_to_maturity,
            self.approximate_yield,
            self.face_unit,
        ]

    @property
    def broker_price(self) -> float:
        """
        Calculates bond price on broker.
        Formula: (face_value * bond_price / 100 + ACI) * (1 + BROKER_FEE)

        :return: Bond price on broker.
        :rtype: float
        """
        price = self.face_value * self.bond_price / 100  # no ACI
        price = price + self.ACI  # current market price
        price *= 1 + self.BROKER_FEE  # including broker fee
        return price

    @property
    def coupons_amount(self) -> int:
        """
        Calculates amount of coupons left in bond.

        :return: Amount of coupons left in bond.
        :rtype: int
        """
        if not self.coupon_period:
            return 0

        full_coupons, part_coupon = divmod(self.days_to_maturity, self.coupon_period)
        coupons = full_coupons + bool(part_coupon)
        return coupons

    @property
    def days_to_maturity(self) -> int:
        """
        Calculates days to bond maturity date from today.

        :return: Days to bond maturity date from today.
        :rtype: int
        """
        return (self.maturity_date - datetime.date.today()).days

    @property
    def approximate_yield(self) -> float:
        """
        Calculates approximate bond yield from today to maturity date in percents.

        :return: Approximate bond yield from today to maturity date in percents.
        :rtype: float
        """
        if self.days_to_maturity <= 0:
            return 0

        coupons_income = self.coupons_amount * self.coupon_value

        total_income = self.face_value + coupons_income
        rate = (
            (total_income / self.broker_price - 1) * 100 * 365 / self.days_to_maturity
        )

        return round(rate, 2)
