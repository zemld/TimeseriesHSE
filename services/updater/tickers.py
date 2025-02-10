from enum import Enum


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


def get_all_action_tickers():
    return [ticker.value for ticker in ActionTickers]
