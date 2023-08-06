import datetime
import json
import re

import pytz


snake_add_underscore_to_camel_pattern = re.compile(r"(?<!^)(?=[A-Z])")


def camel_to_snake(name):
    return snake_add_underscore_to_camel_pattern.sub("_", name).lower()


def snake_to_camel(word):
    import re

    return "".join(x.capitalize() or "_" for x in word.split("_"))


def string_to_dict(payload_as_string):
    payload_as_dict = json.loads(payload_as_string)
    return payload_as_dict


def log_style_utc_date_w_millis(timestamp):
    d = datetime.datetime.utcfromtimestamp(timestamp)
    d = pytz.UTC.localize(d)
    millis = round(d.microsecond / 1000)
    if millis == 1000:
        d += datetime.timedelta(seconds=1)
        millis = 0
    utc_date = d.strftime("%Y-%m-%d %H:%M:%S")
    if 0 <= millis < 10:
        millis_string = f".00{millis}"
    elif 10 <= millis < 100:
        millis_string = f".0{millis}"
    else:
        millis_string = f".{millis}"
    return utc_date + millis_string + d.strftime(" %Z")
