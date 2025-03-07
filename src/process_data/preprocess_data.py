import pandas as pd

def convert_duration_to_minutes(duration):
    if not isinstance(duration, str):
        return None
    try:
        parts = duration.split()
        hours = int(parts[0][:-1]) if 'h' in parts[0] else 0
        minutes = int(parts[1][:-1]) if len(parts) > 1 and 'm' in parts[1] else 0
        return hours * 60 + minutes
    except (ValueError, IndexError):
        return None


def format_field(field):
    if isinstance(field, list):
        return ", ".join(field)
    if isinstance(field, str) and field.startswith('['):
        return ", ".join(eval(field))
    return field


def load_and_preprocess(data_path, save_path=None):
    print("Loading data...")
    df = pd.read_csv(data_path)

    print("Preprocessing data...")

    df['duration_minutes'] = df['duration'].apply(convert_duration_to_minutes)

    df = df[df['duration_minutes'].notnull() & (df['duration_minutes'] >= 60)]

    columns_to_parse = ['genres', 'directors', 'stars', 'keywords']
    for column in columns_to_parse:
        df[column] = df[column].apply(eval).apply(format_field)

    df['description'] = df['description'].fillna('').astype(str)
    df['storyline'] = df['storyline'].fillna('').astype(str)

    df['combined_text'] = (
        df['description'] + " " +
        df['storyline'] + " " +
        df['keywords'] + " " +
        "featuring " + df['stars'] + " " +
        "directed by " + df['directors'] + " " +
        "in the genre of " + df['genres'] + " " +
        "released in " + df['release_date'].astype(str) + " " +
        "with a runtime of " + df['duration_minutes'].astype(str) + " minutes"
    )

    df = df.drop(columns=['storyline', 'keywords', 'duration'])

    print("Preprocessing complete.")

    if save_path:
        df.to_csv(save_path, index=False)
        print(f"Processed data saved to {save_path}")

    return df


data_path = "data/movies_data.csv"
save_path = "data/preprocessed_data.csv"

df = load_and_preprocess(data_path, save_path)

# Uncomment to preview the preprocessed data
# print("\nPreprocessed Data Preview:")
# print(df.head())
