import ast
import csv
import pandas as pd

def prepare_set_from_list(data_path, save_path=None):
    df = pd.read_csv(data_path, converters={
        'directors': ast.literal_eval,
        })

    directors_set = []
    for directors in df['directors']:
        for director in directors:
            if director not in directors_set and director != '':
                directors_set.append(director)

    if save_path is not None:
        with open(save_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            for director in directors_set:
                writer.writerow([director])


data_path = "data/movies_data.csv"
save_path = "data/directors_set.csv"

prepare_set_from_list(data_path, save_path)