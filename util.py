from typing import Type
from model.UnitEnum import UnitEnum
import re
import logging
import unicodedata

UNIT_MAPPING = {
    "l": UnitEnum.l,
    "liter": UnitEnum.l,
    "ml": UnitEnum.ml,
    "stk": UnitEnum.stk,
    "pck": UnitEnum.stk,
    "pck.": UnitEnum.stk,
    "würfel": UnitEnum.stk,
    "scheibe/n": UnitEnum.stk,
    "körner": UnitEnum.stk,
    "große": UnitEnum.stk,
    "großes": UnitEnum.stk,
    "kleine": UnitEnum.stk,
    "packung": UnitEnum.packung,
    "kg": UnitEnum.kg,
    "g": UnitEnum.g,
    "mg": UnitEnum.mg,
    "tl": UnitEnum.tl,
    "el": UnitEnum.el,
    "msp": UnitEnum.msp,
    "msp.": UnitEnum.msp,
    "becher": UnitEnum.becher,
    "glas": UnitEnum.becher,
    "tasse": UnitEnum.becher,
    "prise": UnitEnum.prise,
    "prise(n)": UnitEnum.prise,
    "prisen": UnitEnum.prise,
    "etwas": UnitEnum.etwas,
    "spritzer": UnitEnum.etwas,
    "bund": UnitEnum.bund
}

EXCLUDE = ["gestr.", "kl", "gr"]

DEFAULT_UNIT = UNIT_MAPPING["stk"]
DEFAULT_QUANTITY = 1



def stripify(text: str) -> str:
    return re.sub(' +', ' ', text).strip()


def is_float(number: str) -> bool:
    try:
        float(number)
        return True
    except ValueError:
        pass
    # check if is unicode fraction like '⅕'
    try:
        number = unicodedata.numeric(number)
    except TypeError:
        return False

    return True


def to_float(number: str | float | int) -> float:
    try:
        return float(number)
    except ValueError:
        # is unicode fraction like '⅕'
        return unicodedata.numeric(number)


def parse_amount(amount: str, ingredient_name: str) -> tuple[str, str]:
    splits = amount.split(" ")

    if len(splits) == 1:
        # if unit is 'etwas' add quantity 1
        if splits[0] == "etwas":
            splits.insert(0, "1")
        # if no unit is provied use 'stk' as default unit
        else:
            splits += ["stk"]
    splits = [x for x in splits if x not in EXCLUDE]

    if len(splits) > 2:
        # catch fractions
        if len(splits) == 3:
            try:
                value = unicodedata.numeric(splits[1])
                splits[0] = str((float(splits[0]) + value))
                del splits[1]
            except TypeError as e:
                logger.warn(
                    f"Amount has more than 2 splits: '{splits}'. Removing {splits[1:-1]}")
                del splits[1:-1]

    assert len(splits) == 2

    quantity, unit = splits
    unit = unit.lower()

    if not is_float(quantity):
        logger.warn(
            f"No numeric quantity provided, set to '{DEFAULT_QUANTITY}'. (ing: '{ingredient_name}' - quantity: '{quantity}')")
        quantity = DEFAULT_QUANTITY

    if (sanitized_unit := UNIT_MAPPING.get(unit)) is None:
        logger.warn(
            f"Unit unknown, set to default '{DEFAULT_UNIT}'. (ing: '{ingredient_name}' - unit: '{unit}')")
        sanitized_unit = DEFAULT_UNIT

    quantity = to_float(quantity)

    return float(quantity), sanitized_unit



class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = '%(asctime)s - %(levelname)s | %(name)s: %(message)s'

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger("util")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)