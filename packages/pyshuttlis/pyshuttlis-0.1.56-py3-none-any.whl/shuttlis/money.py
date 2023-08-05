from dataclasses import dataclass


# Deprecated, soon will be removed
def paisa_to_inr(amount_in_paisa: int):
    return round(amount_in_paisa / 100, ndigits=2)


# Deprecated, soon will be removed
def inr_to_paisa(amount_in_inr: int):
    return int(amount_in_inr * 100)


def to_base_denomination(amount: int):
    return int(amount * 100)


def from_base_denomination(amount: int):
    return round(amount / 100, ndigits=2)


@dataclass(frozen=True)
class Money:
    amount: float
    currency: str
