import ast
import csv
import pandas as pd
import re


def get_genres_with_regex(actors):
    regex = r"( '|\[| (?!\'))(.*?)(\]|,)"
    matches = re.finditer(regex, actors, re.MULTILINE)
    actors_list = [match.group()[1:-1] for matchNum, match in enumerate(matches, start=1)]

    return actors_list


def prepare_set_with_regex(data_path, save_path=None):
    actors_set = []
    print("Loading data...")

    df = pd.read_csv(data_path)

    print("Preprocessing data...")

    for index, row in df.iterrows():
        actors = row['stars']
        actors = get_genres_with_regex(actors)

        for actor in actors:
            actor = actor.replace("\"", "\'")[1:-1]
            if actor not in actors_set and "See production info" not in actor and actor != "":
                actors_set.append(actor)

    if save_path is not None:
        with open(save_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            for actor in actors_set:
                writer.writerow([actor])

    return



def prepare_set_from_list(data_path, save_path=None):
    df = pd.read_csv(data_path, converters={
        'stars': ast.literal_eval,
    })

    actors_set = []
    for actors in df['stars']:
        for actor in actors:
            if actor not in actors_set and actor != '' and "See production info" not in actor:
                actors_set.append(actor)

    if save_path is not None:
        with open(save_path, "w", newline="") as file:
            writer = csv.writer(file)
            for actor in actors_set:
                writer.writerow([actor])

    return


data_path = "data/movies_data.csv"
save_path = "data/actors_set.csv"

prepare_set_with_regex(data_path, save_path)
# prepare_set_from_list(data_path, save_path)

