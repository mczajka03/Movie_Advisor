import re

def get_movie_duration_from_regex(input):
    reg_hours = 0
    reg_minutes = 0

    h_regex = r"\b(\d+|\d+[\.,]\d+)\s*(h|hour|hours)\b"
    h_time = re.findall(h_regex, input, re.IGNORECASE)
    min_regex = r"\b(\d+|\d+[\.,]\d+)\s*(min|minute)s?\b"
    min_time = re.findall(min_regex, input, re.IGNORECASE)

    try:
        reg_hours = float(h_time[0][0].replace(',', '.'))
    except:
        pass

    try:
        reg_minutes = float(min_time[0][0].replace(',', '.'))
    except:
        pass

    return reg_hours, reg_minutes


def get_movie_duration(time, input):
    time_list = time.split()
    time_list = [x.lower() for x in time_list]

    hours = 0
    minutes = 0

    hour_tags = ["hours", "hour"]
    for h in hour_tags:
        if h in time_list:
            try:
                hours = float(time_list[time_list.index(h) - 1].replace(',', '.'))
            except:
                pass

    minute_tags = ["minutes", "minute"]
    for m in minute_tags:
        if m in time_list:
            try:
                minutes = float(time_list[time_list.index(m) - 1].replace(',', '.'))
            except:
                pass

    if hours == 0 or minutes == 0:
        reg_hours, reg_minutes = get_movie_duration_from_regex(input)
        if hours == 0 and reg_hours != 0:
            hours = reg_hours

        if minutes == 0 and reg_minutes != 0:
            minutes = reg_minutes

    return hours*60 + minutes