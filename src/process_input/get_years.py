import re
from datetime import datetime

def get_movie_years_from_word(input):
    regex = r"\b((latest|newest|new|current|recent|modern|old|old-fashioned|retro|vintage)\b[\sa-z]{0,20})?\b(movie|film|classic|show|art|adventure|story|crime|drama|thriller|comedy|tale)\b(\s+from last)?\b"

    release_dates = re.findall(regex, input, re.IGNORECASE)

    for rd in release_dates:
        if rd[0] != "":
            if rd[0].lower() in ["latest ", "new ", "newest ", "current ", "recent ", "modern "]:
                years = (str(datetime.now().year - 5), str(datetime.now().year))
            else:
                years = ("1900", "1985")

            return years

        elif rd[2] != "" and rd[3] != "":
            years = (str(datetime.now().year - 10), str(datetime.now().year))
            return years

    return ()


def get_movie_years_from_digit(input):
    regex = r"\b(\d{4}|\d{2})(s?)\s+(movie|film|classic|show|art|adventure|story|crime|drama|thriller|comedy|tale)\b"
    release_dates = re.findall(regex, input, re.IGNORECASE)

    for rd in release_dates:
        if len(rd[0]) == 2:
            rd = ("19" + rd[0], rd[1], rd[2])

        year = ()

        if rd[1] == '':
            year = (rd[0], rd[0])
        elif rd[1] == 's':
            year = (rd[0][0:3] + '0', rd[0][0:3] + '9')

        if year != ():
            return year

    return ()


def get_movie_years_from_basic(input):
    regex = r"\b(movie|film|classic|show|art|adventure|story|crime|drama|thriller|comedy|tale).{0,50}\s+(released|from|before|after|made|produced|in|during|early|late|middle|since)[a-z\s]{0,20}(\d{4}|\d{2})(s?)\b"
    release_dates = re.findall(regex, input, re.IGNORECASE)

    for rd in release_dates:
        if len(rd[2]) == 2:
            rd = (rd[0], rd[1], "19" + rd[2], rd[3])

        year = ()

        match rd[1].lower():
            case "in":
                if rd[3] == '':
                    year = (rd[2], rd[2])
                elif rd[3] == 's':
                    year = (rd[2][0:3] + '0', rd[2][0:3] + '9')

            case "during":
                if rd[3] == '':
                    year = (rd[2], rd[2])
                elif rd[3] == 's':
                    year = (rd[2][0:3] + '0', rd[2][0:3] + '9')

            case "from":
                if rd[3] == '':
                    year = (rd[2], rd[2])
                elif rd[3] == 's':
                    year = (rd[2][0:3] + '0', rd[2][0:3] + '9')

            case "before":
                year = ("1900", rd[2])

            case "after":
                if rd[3] == '':
                    year = (rd[2], str(datetime.now().year))
                elif rd[3] == 's':
                    year = (rd[2][0:3] + "0", str(datetime.now().year))

            case "since":
                if rd[3] == '':
                    year = (rd[2], str(datetime.now().year))
                elif rd[3] == 's':
                    year = (rd[2][0:3] + "0", str(datetime.now().year))

            case "early":
                if rd[3] == '':
                    year = (rd[2], rd[2])
                elif rd[3] == 's':
                    year = (rd[2], rd[2][0:3] + '4')

            case "late":
                if rd[3] == '':
                    year = (rd[2], rd[2])
                elif rd[3] == 's':
                    year = (rd[2][0:2] + '5', rd[2][0:3] + '9')

            case "middle":
                if rd[3] == '':
                    year = (rd[2], rd[2])
                elif rd[3] == 's':
                    year = (rd[2][0:3] + '3', rd[2][0:3] + '7')

            case _:
                year = ()

        if year != ():
            return year

    return ()


def get_movie_years_from_last(input):
    regex = r"((\b(movie|film|classic|show|art|adventure|story|crime|drama|thriller|comedy|tale).{0,50}last (\d{0,3})\s*(years|year|decades|decade)('s)?.{0,50}(movie|film|classic|show|art|adventure|story|crime|drama|thriller|comedy|tale)?\b)|(\b(movie|film|classic|show|art|adventure|story|crime|drama|thriller|comedy|tale)?.{0,50}last (\d{0,3})\s*(years|year|decades|decade)('s)?.{0,50}(movie|film|classic|show|art|adventure|story|crime|drama|thriller|comedy|tale)\b))"
    release_dates = re.findall(regex, input, re.IGNORECASE)

    if len(release_dates) != 0:
        if release_dates[0][4] != '':
            rd = release_dates[0][4]
            number = release_dates[0][3]

        else:
            rd = release_dates[0][10]
            number = release_dates[0][9]

        match rd:
            case "year":
                if number != '':
                    years = (str(datetime.now().year - int(number)), str(datetime.now().year))
                else:
                    years = (str(datetime.now().year - 1), str(datetime.now().year))

                return years

            case "years":
                if number != '':
                    years = (str(datetime.now().year - int(number)), str(datetime.now().year))
                    return years

    return ()


def get_movie_years_from_range(input):
    regex = r"((\b(movie|film|classic|show|art|adventure|story|crime|drama|thriller|comedy|tale).{0,50}(between|from|range|within|in)?\s+(\d{4}s?|\d{2}s?)\s*(-|to|and)\s*(\d{4}s?|\d{2}s?)(?!\d).{0,50}(movie|film|classic|show|art|adventure|story|crime|drama|thriller|comedy|tale)?\b)|(\b(movie|film|classic|show|art|adventure|story|crime|drama|thriller|comedy|tale)?.{0,50}(between|from|range|within)?\s+(\d{4}s?|\d{2}s?)\s*(-|to|and)\s*(\d{4}s?|\d{2}s?)(?!\d).{0,50}(movie|film|classic|show|art|adventure|story|crime|drama|thriller|comedy|tale)\b))"
    release_dates = re.findall(regex, input, re.IGNORECASE)

    if len(release_dates) != 0:

        if release_dates[0][4] != '':
            first_date = release_dates[0][4]
            second_date = release_dates[0][6]
        else:
            first_date = release_dates[0][11]
            second_date = release_dates[0][13]

        if len(first_date) == 2:
            first_date = "19" + first_date
        elif len(second_date) == 2:
            second_date = "19" + second_date

        return tuple(sorted((first_date, second_date)))

    return ()


def get_movie_years(input):
    steps = [get_movie_years_from_range, get_movie_years_from_last, get_movie_years_from_basic, get_movie_years_from_digit, get_movie_years_from_word]
    years = ()

    for step in steps:
        years = step(input)

        if years != ():
            return years

    return years