import spacy
import pandas as pd
from get_duration import get_movie_duration, get_movie_duration_from_regex
from get_genres import get_movie_genres
from get_people import get_actor_or_director
from get_years import get_movie_years
from llm_analyze_input import llm_analyze_user_input

"""
The same as in the file src/process_input/analyze_input.py
This file is used to check performance of different LLM's
"""

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


def analyze_user_input(input,model_name):
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
        if ent.label_ == "PERSON":
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

    return llm_analyze_user_input(input, data,model_name=model_name)
    #return data
    
inputs=[
    "I want to watch action movie about fighting with the past. I really like Aaron Paul. It should be directed by Vince Gilligan. Movie can't be longer than 3 hours, and released in the last 10 years.",
    "I want to watch a thriller, but not with Harrison Ford. I love Tom Holland. Preferably something directed by Jon Watts, about 2.5 hours long, and released in the last 8 years.",
    "I want to watch a comedy. I love movies with Jim Carrey. It can't be directed by Peter Weir. I want it to be about 2 hours long, and released in the last 50 years."
]

models=[
    "mistral-7b-instruct-v0.1.Q4_0.gguf",
    "mistral-7b-openorca.Q4_0.gguf",
    "Meta-Llama-3-8B-Instruct.Q4_0.gguf",
    "Llama-3.2-3B-Instruct-Q4_0.gguf"
]

for input in inputs:
    print(f"Input: {input}")
    with open("src/process_input/llms_analyze_test_results.txt", "a") as f:
        f.write(f"Input: {input}\n")
        for model in models:
            print(model)
            output = analyze_user_input(input, model_name=model)
            print(output)
            f.write(f"{model}\nResult: {output}\n-------------------------------------------------\n")
            print("-------------------------------------------------")
        f.close()
   