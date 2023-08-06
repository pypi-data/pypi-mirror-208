import string
import struct
from datetime import datetime
from typing import Any
from typing import Callable

import pendulum
import pydantic
import pytz

from gwatn.data_classes import MarketType
from gwatn.data_classes.hack_price_method import PlatformPriceMethod
from gwatn.enums import RecognizedCurrencyUnit
from gwatn.enums import RecognizedTemperatureUnit
from gwatn.enums.hack_recognized_p_node_alias import RecognizedPNodeAlias
from gwatn.enums.hack_weather_method import WeatherMethod
from gwatn.enums.hack_weather_source import WeatherSource
from gwatn.enums.recognized_irradiance_type import RecognizedIrradianceType


def is_recognized_p_node_alias(candidate):
    c = ".".join(["w"] + candidate.split(".")[1:])
    try:
        RecognizedPNodeAlias(c)
    except ValueError:
        return False
    return True


def is_recognized_currency_unit(candidate):
    try:
        RecognizedCurrencyUnit(candidate)
    except ValueError:
        return False
    return True


def is_recognized_temperature_unit(candidate):
    try:
        RecognizedTemperatureUnit(candidate)
    except ValueError:
        return False
    return True


def is_recognized_irradiance_type(candidate):
    try:
        RecognizedIrradianceType(candidate)
    except ValueError:
        return False
    return True


def is_weather_source(candidate):
    try:
        WeatherSource(candidate)
    except ValueError:
        return False
    return True


def is_weather_method(candidate):
    try:
        WeatherMethod(candidate)
    except ValueError:
        return False
    return True


def is_non_negative_int64(candidate):
    if not isinstance(candidate, int):
        return False
    if candidate < 0:
        return False
    return True


def is_log_style_utc_date_w_millis(candidate):
    """Example: '2020-11-17 14:57:00.525 UTC'"""
    try:
        x = candidate.split(" ")
    except AttributeError:
        return False
    if x[2] != "UTC":
        return False
    t_w_millis = x[1].split(".")
    if len(t_w_millis[1]) != 3:
        return False
    try:
        int(t_w_millis[1])
    except ValueError:
        return False
    hh, mm, ss = t_w_millis[0].split(":")
    try:
        hh = int(hh)
        mm = int(mm)
        ss = int(ss)
    except ValueError:
        return False
    if hh < 0 or hh > 23:
        return False
    if mm < 0 or mm > 59:
        return False
    if ss < 0 or ss > 59:
        return False
    yyyy, MM, dd = x[0].split("-")
    if len(yyyy) != 4:
        return False
    try:
        yyyy = int(yyyy)
        MM = int(MM)
        dd = int(dd)
    except ValueError:
        return False
    if MM < 1 or MM > 12:
        return False
    if dd < 1 or dd > 31:
        return False
    return True


def is_recognized_market_type(candidate):
    if candidate in MarketType.by_id.keys():
        return True
    return False


def is_recognized_price_method(candidate):
    if candidate not in PlatformPriceMethod.keys():
        return False
    return True


def is_recognized_timezone_string(candidate):
    try:
        pytz.timezone(candidate)
    except:
        return False
    return True


def predicate_validator(
    field_name: str, predicate: Callable[[Any], bool], error_format: str = ""
) -> classmethod:  # type: ignore
    def _validator(v: Any) -> Any:
        if not predicate(v):
            if error_format:
                err_str = error_format.format(value=v)
            else:
                err_str = f"{field_name}: {predicate} fails for [{v}]"
            raise ValueError(err_str)
        return v

    return pydantic.validator(field_name, allow_reuse=True)(_validator)


def is_iso_format(candidate: str) -> bool:
    try:
        datetime.fromisoformat(candidate.replace("Z", "+00:00"))
    except:
        return False
    return True


def is_64_bit_hex(candidate: str) -> bool:
    if len(candidate) != 8:
        return False
    if not all(c in string.hexdigits for c in candidate):
        return False
    return True


def check_is_64_bit_hex(candidate: str) -> None:
    if len(candidate) != 8:
        raise ValueError(f" {candidate} Must be length 8, not {len(candidate)}")
    if not all(c in string.hexdigits for c in candidate):
        raise ValueError("Must be hex digits")


def is_bit(candidate: int) -> bool:
    if candidate not in {0, 1}:
        return False
    return True


def check_is_bit(candidate: int) -> None:
    if candidate not in {0, 1}:
        raise ValueError(f"{candidate} must be either 0 or 1")


def is_lrd_alias_format(candidate: str) -> bool:
    """Lowercase AlphanumericStrings separated by dots (i.e. periods), with most
    significant word to the left.  I.e. `dw1.ne` is the child of `dw1`.
    Checking the format cannot verify the significance of words. All
    words must be alphanumeric. Most significant word must start with
    an alphabet charecter

    Args:
        candidate (str): candidate

    Returns:
        bool: True if is_lrod_alias_format
    """
    try:
        x = candidate.split(".")
    except:
        return False
    first_word = x[0]
    first_char = first_word[0]
    if not first_char.isalpha():
        return False
    for word in x:
        if not word.isalnum():
            return False
    if not candidate.islower():
        return False
    return True


def check_is_lrd_alias_format(candidate: str) -> None:
    """Lowercase AlphanumericStrings separated by dots (i.e. periods), with most
    significant word to the left.  I.e. `dw1.ne` is the child of `dw1`.
    Checking the format cannot verify the significance of words. All
    words must be alphanumeric. Most significant word must start with
    an alphabet charecter


    Raises:
        ValueError: if candidate is not of lrd format (e.g. dw1.iso.me.apple)
    """
    try:
        x = candidate.split(".")
    except:
        raise ValueError("Failed to seperate into words with split'.'")
    first_word: str = x[0]
    first_char = first_word[0]
    if not first_char.isalpha():
        raise ValueError(
            f"Most significant word must start with alphabet char. Got '{first_word}'"
        )
    for word in x:
        w: str = str(word)
        if not w.isalnum():
            raise ValueError(f"words seperated by dots must be alphanumeric. Got '{w}'")
    if not candidate.islower():
        raise ValueError(f"alias must be lowercase. Got '{candidate}'")


def is_lru_alias_format(candidate: str) -> bool:
    """AlphanumericStrings separated by underscores, with most
    significant word to the left.  I.e. `dw1.ne` is the child of `dw1`.
    Checking the format cannot verify the significance of words. All
    words must be alphanumeric. Most significant word must start with
    an alphabet charecter"""
    try:
        x = candidate.split("_")
    except:
        return False
    first_word = x[0]
    first_char = first_word[0]
    if not first_char.isalpha():
        return False
    for word in x:
        if not word.isalnum():
            return False
    if not candidate.islower():
        return False
    return True


def is_lrh_alias_format(candidate: str) -> bool:
    """AlphanumericStrings separated by hyphens, with most
    significant word to the left.  I.e. `dw1.ne` is the child of `dw1`.
    Checking the format cannot verify the significance of words. All
    words must be alphanumeric. Most significant word must start with
    an alphabet charecter"""
    try:
        x = candidate.split("-")
    except:
        return False
    first_word = x[0]
    first_char = first_word[0]
    if not first_char.isalpha():
        return False
    for word in x:
        if not word.isalnum():
            return False
    if not candidate.islower():
        return False
    return True


def is_positive_integer(candidate: Any) -> bool:
    if not isinstance(candidate, int):
        return False
    if candidate <= 0:
        return False
    return True


def check_is_positive_integer(candidate: int) -> None:
    if not isinstance(candidate, int):
        raise ValueError("Must be an integer")
    if candidate <= 0:
        raise ValueError("Must be positive integer")


def is_world_instance_alias_format(candidate: str) -> bool:
    """AlphanumericString + '__' + Integer"""
    x = candidate.split("__")
    if len(x) != 2:
        return False
    world_root_alias = x[0]
    idx = x[1]
    if not world_root_alias.isalnum():
        return False
    idx_as_float = float(idx)
    if idx_as_float != int(idx_as_float):
        return False
    return True


def is_recognized_p_node_alias(candidate):
    c = ".".join(["w"] + candidate.split(".")[1:])
    try:
        RecognizedPNodeAlias(c)
    except ValueError:
        return False
    return True


def is_reasonable_unix_time_ms(candidate: int) -> bool:
    if pendulum.parse("2000-01-01T00:00:00Z").int_timestamp * 1000 > candidate:
        return False
    if pendulum.parse("3000-01-01T00:00:00Z").int_timestamp * 1000 < candidate:
        return False
    return True


def check_is_reasonable_unix_time_ms(candidate: int) -> None:
    if pendulum.parse("2000-01-01T00:00:00Z").int_timestamp * 1000 > candidate:
        raise ValueError("ReasonableUnixTimeMs must be after 2000 AD")
    if pendulum.parse("3000-01-01T00:00:00Z").int_timestamp * 1000 < candidate:
        raise ValueError("ReasonableUnixTimeMs must be before 3000 AD")


def is_reasonable_unix_time_s(candidate: int) -> bool:
    if pendulum.parse("2000-01-01T00:00:00Z").int_timestamp > candidate:
        return False
    if pendulum.parse("3000-01-01T00:00:00Z").int_timestamp < candidate:
        return False
    return True


def check_is_reasonable_unix_time_s(candidate: int) -> None:
    if pendulum.parse("2000-01-01T00:00:00Z").int_timestamp > candidate:
        raise ValueError("ReasonableUnixTimeS must be after 2000 AD")
    if pendulum.parse("3000-01-01T00:00:00Z").int_timestamp < candidate:
        raise ValueError("ReasonableUnixTimeS must be before 3000 AD")


def is_unsigned_short(candidate: int) -> bool:
    try:
        struct.pack("H", candidate)
    except:
        return False
    return True


def check_is_unsigned_short(candidate: int) -> None:
    try:
        struct.pack("H", candidate)
    except:
        raise ValueError("requires 0 <= number <= 65535")


def is_short_integer(candidate: int) -> bool:
    try:
        struct.pack("h", candidate)
    except:
        return False
    return True


def check_is_short_integer(candidate: int) -> None:
    try:
        struct.pack("h", candidate)
    except:
        raise ValueError("short format requires (-32767 -1) <= number <= 32767")


def is_uuid_canonical_textual(candidate: str) -> bool:
    try:
        x = candidate.split("-")
    except AttributeError:
        return False
    if len(x) != 5:
        return False
    for hex_word in x:
        try:
            int(hex_word, 16)
        except ValueError:
            return False
    if len(x[0]) != 8:
        return False
    if len(x[1]) != 4:
        return False
    if len(x[2]) != 4:
        return False
    if len(x[3]) != 4:
        return False
    if len(x[4]) != 12:
        return False
    return True


def check_is_uuid_canonical_textual(candidate: str) -> None:
    try:
        x = candidate.split("-")
    except AttributeError as e:
        raise ValueError(f"Failed to split on -: {e}")
    if len(x) != 5:
        raise ValueError(f"Did not have 5 words")
    for hex_word in x:
        try:
            int(hex_word, 16)
        except ValueError:
            raise ValueError("Words are not all hex")
    if len(x[0]) != 8:
        raise ValueError("Word 0  not of length 8")
    if len(x[1]) != 4:
        raise ValueError("Word 1 not of length 4")
    if len(x[2]) != 4:
        raise ValueError("Word 2 not of length 4")
    if len(x[3]) != 4:
        raise ValueError("Word 3 not of length 4")
    if len(x[4]) != 12:
        raise ValueError("Word 4 not of length 12")


def is_market_alias_lrd_format(candidate: str) -> bool:
    try:
        x = candidate.split(".")
    except AttributeError:
        return False
    try:
        MarketType(x[0])
    except ValueError:
        return False
    g_node_alias = ".".join(x[1:])
    return is_lrd_alias_format(g_node_alias)


def is_market_slot_name_lrd_format(candidate: str) -> bool:
    try:
        x = candidate.split(".")
    except AttributeError:
        return False
    slot_start = x[-1]
    if len(slot_start) != 10:
        return False
    try:
        slot_start = int(slot_start)
    except ValueError:
        return False
    if slot_start % 300 != 0:
        return False

    market_alias_lrd = ".".join(x[:-1])
    if not is_market_alias_lrd_format(market_alias_lrd):
        return False

    market_type = MarketType(market_alias_lrd.split(".")[0])
    if not slot_start % (market_type.duration_minutes * 60) == 0:
        print(
            f"market_slot_start_s mod {(market_type.duration_minutes * 60)} must be 0"
        )
        return False

    return True


def check_world_alias_matches_universe(g_node_alias: str, universe: str) -> None:
    """
    Raises:
        ValueError: if g_node_alias is not LRD format or if first word does not match universe
    """
    check_is_lrd_alias_format(g_node_alias)
    world_alias = g_node_alias.split(".")[0]
    if universe == "dev":
        if world_alias[0] != "d":
            raise ValueError(
                f"World alias for dev universe must start with d. Got {world_alias}"
            )


def is_recognized_iso8601_utc(candidate):
    try:
        pendulum.parse(candidate)
    except:
        return False
    try:
        date, time_w_utc = candidate.split("T")
    except:
        return False
    try:
        year, month, day = date.split("-")
    except:
        return False
    if len(year) != 4:
        return False
    try:
        int(year)
    except:
        return False
    if time_w_utc[-1] != "Z":
        return False
    time = time_w_utc[:-1]
    hour, minute, second = time.split(":")
    two_digit_int_strings = [month, day, hour, minute, second]
    for s in two_digit_int_strings:
        if len(s) != 2:
            return False
        try:
            int(s)
        except:
            return False
    return True


def is_valid_month_hour_int_array(candidate):
    if type(candidate) != list:
        return False
    if len(candidate) != 12:
        return False
    for i in range(len(candidate)):
        month_list = candidate[i]
        if type(month_list) != list:
            return False
        if len(month_list) != 24:
            return False
        for j in range(len(month_list)):
            hour_value = month_list[j]
            if type(hour_value) != int:
                return False
