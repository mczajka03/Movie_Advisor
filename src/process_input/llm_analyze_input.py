from gpt4all import GPT4All

def llm_analyze_user_input(user_input, data, model_name = "mistral-7b-instruct-v0.1.Q4_0.gguf"):
    model = GPT4All(model_name)

    prompt = f"""Analyze the provided movie preferences based on the following structured data and user description.
    For each category and item, specify whether it is 'positive' (the user wants it), 'neutral' (it doesn't matter) or 'negative' (the user doesn't want it).
    If a category or list is empty, ignore it and do not include it in the output.

    ### EXAMPLE:

    User description:
    "I want to watch a thriller or drama, but not with Brad Pitt. I love films with Bruce Willis or Jackie Chan. Preferably something not directed by Quentin Tarantino, about 2.5 hours long, and released in the last 8 years."

    Data:
    actors: ["Brad Pitt", "Tom Cruise", "Bruce Willis", "Jackie Chan"]
    directors: ["Quentin Tarantino", "James Cameron"]
    genres: ["thriller", "drama"]
    years: (2015, 2023)
    duration (minutes): 150

    Output Format:

    Actors:
    - Brad Pitt - negative
    - Tom Cruise - neutral
    - Bruce Willis - positive
    - Jackie Chan - positive

    Directors:
    - Quentin Tarantino - negative
    - James Cameron - neutral

    Genres:
    - Thriller - positive
    - Drama - positive

    Years:
    - 2015–2023 - positive

    Duration:
    - 150 minutes - positive

    ### NOW ANALYZE THE FOLLOWING DATA:

    User description:
    "{user_input}"

    Data:
    actors: {data['actors']},
    directors: {data['directors']},
    genres: {data['genres']},
    years: {data['years']},
    duration (minutes): {data['duration']}
    """

    print("Analyzing...")
    output = model.generate(prompt)

    positive = {'actors': [], 'directors': [], 'genres': [], 'years': (), 'duration': 0}
    negative = {'actors': [], 'directors': [], 'genres': [], 'years': (), 'duration': 0}

    lines = output.splitlines()
    current_category = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("Actors:"):
            current_category = 'actors'
        elif line.startswith("Directors:"):
            current_category = 'directors'
        elif line.startswith("Genres:"):
            current_category = 'genres'
        elif line.startswith("Years:"):
            current_category = 'years'
        elif line.startswith("Duration:"):
            current_category = 'duration'
        elif current_category:
            try:
                item, status = line.split(" - ")
                item = item[2:]
            except:
                continue

            if current_category in ['actors', 'directors', 'genres']:
                if 'positive' in status:
                    positive[current_category].append(item)
                elif 'negative' in status:
                    negative[current_category].append(item)
            elif current_category == 'years':
                if 'positive' in status:
                    positive['years'] = data['years']
                elif 'negative' in status:
                    negative['years'] = data['years']
            elif current_category == 'duration':
                if 'positive' in status:
                    positive['duration'] = data['duration']
                elif 'negative' in status:
                    negative['duration'] = data['duration']
            
    return positive, negative