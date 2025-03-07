import ast
import csv
import pandas as pd
import re


def get_genres_with_regex(genres):
    genres_list = re.findall(r"'(.*?)'?(?='[,\]])'", genres)

    return genres_list


def prepare_set_with_regex(data_path, save_path=None):
    genres_set = []
    print("Loading data...")

    df = pd.read_csv(data_path)

    print("Preprocessing data...")

    for index, row in df.iterrows():
        genres = row['genres']
        genres = get_genres_with_regex(genres)

        for genre in genres:
            if genre not in genres_set:
                genres_set.append(genre)

    if save_path is not None:
        with open(save_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            for genre in genres_set:
                writer.writerow([genre])

    return


def prepare_set_from_list(data_path, save_path=None):
    df = pd.read_csv(data_path, converters={
        'genres': ast.literal_eval,
    })

    genres_set = []
    for genres in df['genres']:
        for genre in genres:
            if genre not in genres_set:
                genres_set.append(genre)

    if save_path is not None:
        with open(save_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            for genre in genres_set:
                writer.writerow([genre])

    return


data_path = "data/movies_data.csv" 
save_path = "data/genres_set.csv"

prepare_set_with_regex(data_path, save_path)
# prepare_set_from_list(data_path, save_path)