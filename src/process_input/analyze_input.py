import spacy
import pandas as pd
from src.process_input.get_duration import get_movie_duration, get_movie_duration_from_regex
from src.process_input.get_genres import get_movie_genres
from src.process_input.get_people import get_actor_or_director
from src.process_input.get_years import get_movie_years
from src.process_input.llm_analyze_input import llm_analyze_user_input


def load_data():
    sets = {}
    df = pd.read_csv('data/directors_set.csv', header=None)
    df.columns = ['Name']
    sets["directors"] = df['Name'].str.lower().tolist()

    df = pd.read_csv('data/actors_set.csv', header=None)
    df.columns = ['Name']
    sets["actors"] = df['Name'].str.lower().tolist()

    df = pd.read_csv('data/genres_set.csv', header=None)
    df.columns = ['Name']
    sets["genres"] = df['Name'].str.lower().tolist()

    return sets


def analyze_user_input(input, mode="standard"):
    nlp = spacy.load("en_core_web_sm")
    tokens = nlp(input)
    sets = load_data()
    data = {
        "actors": [],
        "directors": [],
        "genres": [],
        "years": (),
        "duration": ()
    }

    for ent in tokens.ents:
        if ent.label_ == "PERSON" or ent.label_ == "ORG":
            in_set, person_type = get_actor_or_director(ent.text.lower(), sets)

            if in_set is True:
                if person_type == "actors":
                    data["actors"].append(ent.text)

                elif person_type == "directors":
                    data["directors"].append(ent.text)

        if ent.label_ == "TIME" and data["duration"] == ():
            data["duration"] = get_movie_duration(ent.text, input)

    if data["duration"] == () or data["duration"] == 0:
        h, min = get_movie_duration_from_regex(input)
        data["duration"] = h*60 + min

    data["genres"] = get_movie_genres(tokens, sets)
    data["years"] = get_movie_years(input)

    if mode == "advanced":
            return llm_analyze_user_input(input, data)
        
    return data