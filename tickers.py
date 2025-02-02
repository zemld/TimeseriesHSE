from enum import Enum

# Выяснилось, что нормально работают только акции. Облигации вообще странно, потому что у них есть срок годности.
# А с валютами просто какая-то хрень. Их не удается нормально получать
class ActionTickers(Enum):
    Sber = "SBER"
    Gazprom = "GAZP"
    Lukhoil = "LUKH"
    Rosneft = "ROSN"
    Yandex = "YNDX"
    Aeroflot = "AFTL"
    Mts = "MTSS"
    Nlmk = "NLMK"
    Polus = "PLZL"
    Tatneft = "TATN"
    Nornikel = "GMKN"
    Magnit = "MGNT"


class BondTickers(Enum):
    Sber = "RU000A0ZZZ01"
    Gazprom = "RU000A101AM1"
    Lukhoil = "RU000A0ZZZ99"
    Rosneft = "RU000A1008V9"
    Novatek = "RU000A0ZZZ77"


class CurrencyTickers(Enum):
    Dollar = "USDRUB"
    Euro = "EUR_RUB"
    Yuan = "CNY_RUB"
    Franc = "CHF_RUB"
    Pound = "GPB_RUB"
    Yen = "JPYRUB"
    BRub = "BYN_RUB"
    Lira = "TRY_RUB"
    Tenge = "KZT_RUB"


def action_value_to_enum(action: str):
    action = action.lower()
    if action == "сбер":
        return ActionTickers.Sber
    if action == "газпром":
        return ActionTickers.Gazprom
    if action == "лукойл":
        return ActionTickers.Lukhoil
    if action == "роснефть":
        return ActionTickers.Rosneft
    if action == "яндекс":
        return ActionTickers.Yandex
    if action == "аэрофлот":
        return ActionTickers.Aeroflot
    if action == "мтс":
        return ActionTickers.Mts
    if action == "нлмк":
        return ActionTickers.Nlmk
    if action == "полюс":
        return ActionTickers.Polus
    if action == "татнефть":
        return ActionTickers.Tatneft
    if action == "норникель":
        return ActionTickers.Nornikel
    if action == "магнит":
        return ActionTickers.Magnit

    raise ValueError(f"Unknown action: {action}")


def bond_value_to_enum(bond: str):
    bond = bond.lower()
    if bond == "сбер":
        return BondTickers.Sber
    if bond == "газпром":
        return BondTickers.Gazprom
    if bond == "лукойл":
        return BondTickers.Lukhoil
    if bond == "роснефть":
        return BondTickers.Rosneft
    if bond == "новатэк":
        return BondTickers.Novatek

    raise ValueError(f"Unknown bond: {bond}")


def currency_value_to_enum(currency: str):
    currency = currency.lower()
    if currency == "доллар":
        return CurrencyTickers.Dollar
    if currency == "евро":
        return CurrencyTickers.Euro
    if currency == "юань":
        return CurrencyTickers.Yuan
    if currency == "швейцарский франк":
        return CurrencyTickers.Franc
    if currency == "фунт":
        return CurrencyTickers.Pound
    if currency == "йена":
        return CurrencyTickers.Yen
    if currency == "беларусский рубль":
        return CurrencyTickers.BRub
    if currency == "турецкая лира":
        return CurrencyTickers.Lira
    if currency == "тенге":
        return CurrencyTickers.Tenge

    raise ValueError(f"Unknown currency: {currency}")


def get_all_action_tickers():
    return [ticker.value for ticker in ActionTickers]