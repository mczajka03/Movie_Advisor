import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
import pandas as pd
import pickle
from transformers import BertTokenizer, BertModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from src.process_input.analyze_input import analyze_user_input
import numpy as np

def load_embeddings(embeddings_path):
    with open(embeddings_path, 'rb') as f:
        embeddings = pickle.load(f)
    return embeddings


def enhance_user_input(user_input,analyzed_data,negative_analyzed_data):
    parts = []

    if analyzed_data['actors']:
        parts.append(f"featuring {' and '.join(analyzed_data['actors'])}")
    if analyzed_data['directors']:
        parts.append(f"directed by {' and '.join(analyzed_data['directors'])}")
    if analyzed_data['genres']:
        parts.append(f"in the genre of {' and '.join(analyzed_data['genres'])}")
    if analyzed_data['years']:
        start, end = analyzed_data['years']
        parts.append(f"released between {start} and {end}")
    if analyzed_data['duration']:
        parts.append(f"with a runtime under {analyzed_data['duration']} minutes")

    print(f"Enhanced Input: {user_input} -> {', '.join(parts)}")

    return " ".join(parts) or user_input


def generate_user_embedding(user_input, model_type, model,analyzed_data,negative_analyzed_data, tokenizer=None):
    # enhanced_input = enhance_user_input(user_input,analyzed_data,negative_analyzed_data)
    enhanced_input = user_input
    print(f"Enhanced Input for Embedding: {enhanced_input}")

    if model_type == 'bert':
        if tokenizer is None:
            raise ValueError("Tokenizer is required for BERT model.")
        inputs = tokenizer(enhanced_input, return_tensors='pt', max_length=512, truncation=True, padding='max_length')
        outputs = model(**inputs)
        return outputs.last_hidden_state[:, 0, :].squeeze(0).detach().numpy()
    elif model_type in ['sentence-transformer', 'sentence-bert', 'alibaba']:
        return model.encode(enhanced_input, convert_to_tensor=False)
    else:
        raise ValueError("Invalid model type. Choose 'bert', 'sentence-transformer', or 'sentence-bert'.")



def recommend_movies(user_input, df, embeddings, model_type, model, tokenizer=None, performance_choice="standard", similarity_metric="cosine"):
    if performance_choice == "advanced":
        analyzed_data, negative_analyzed_data = analyze_user_input(user_input, performance_choice)
    else:
        analyzed_data = analyze_user_input(user_input, performance_choice)
        negative_analyzed_data = {}

    print(f"Analyzed Data: {analyzed_data}")
    print(f"Negative Analyzed Data: {negative_analyzed_data if performance_choice == 'advanced' else 'N/A'}")

    user_embedding = generate_user_embedding(
        user_input, model_type, model, analyzed_data, negative_analyzed_data, tokenizer
    )

    raw_cosine_similarities = cosine_similarity([user_embedding], embeddings).flatten()
    raw_euclidean_distances = np.linalg.norm(embeddings - user_embedding, axis=1)

    # Scale to [0, 1]
    scaled_cosine_similarities = (raw_cosine_similarities + 1) / 2

    # Scale to [0, 1]
    scaled_euclidean_distances = 1 / (1 + raw_euclidean_distances)

    if similarity_metric == "cosine":
        scores = scaled_cosine_similarities
    elif similarity_metric == "euclidean":
        scores = scaled_euclidean_distances
    else:
        raise ValueError("Invalid similarity metric. Choose 'cosine' or 'euclidean'.")

    weights = pd.Series(1.0, index=df.index)

    WEIGHT_FACTORS = {
        "actors": 0.7,
        "directors": 0.2,
        "genres": 0.2,
        "years": 0.125,
        "duration": 0.125
    }
    PENALTY_FACTOR = 1.5

    if analyzed_data.get('actors'):
        for actor in analyzed_data['actors']:
            weights += df['stars'].str.contains(actor, case=False, na=False) * WEIGHT_FACTORS['actors']

    if analyzed_data.get('directors'):
        for director in analyzed_data['directors']:
            weights += df['directors'].str.contains(director, case=False, na=False) * WEIGHT_FACTORS['directors']

    if analyzed_data.get('genres'):
        for genre in analyzed_data['genres']:
            weights += df['genres'].str.contains(genre, case=False, na=False) * WEIGHT_FACTORS['genres']

    if analyzed_data.get('years'):
        start_year, end_year = map(int, analyzed_data['years'])
        df_years = pd.to_numeric(df['release_date'], errors='coerce').fillna(0).astype(int)
        weights += ((df_years >= start_year) & (df_years <= end_year)) * WEIGHT_FACTORS['years']

    if analyzed_data.get('duration'):
        weights += ((df['duration_minutes'] >= analyzed_data['duration'] - 20) &
                    (df['duration_minutes'] <= analyzed_data['duration'] + 20)) * WEIGHT_FACTORS['duration']

    if performance_choice == "advanced":
        if negative_analyzed_data.get('actors'):
            for actor in negative_analyzed_data['actors']:
                weights -= df['stars'].str.contains(actor, case=False, na=False) * (WEIGHT_FACTORS['actors'] * PENALTY_FACTOR)

        if negative_analyzed_data.get('directors'):
            for director in negative_analyzed_data['directors']:
                weights -= df['directors'].str.contains(director, case=False, na=False) * (WEIGHT_FACTORS['directors'] * PENALTY_FACTOR)

        if negative_analyzed_data.get('genres'):
            for genre in negative_analyzed_data['genres']:
                weights -= df['genres'].str.contains(genre, case=False, na=False) * (WEIGHT_FACTORS['genres'] * PENALTY_FACTOR)

        if negative_analyzed_data.get('years'):
            start_year, end_year = map(int, negative_analyzed_data['years'])
            df_years = pd.to_numeric(df['release_date'], errors='coerce').fillna(0).astype(int)
            weights -= ((df_years >= start_year) & (df_years <= end_year)) * (WEIGHT_FACTORS['years'] * PENALTY_FACTOR)

        if negative_analyzed_data.get('duration'):
            weights -= ((df['duration_minutes'] < analyzed_data['duration'] - 20) |
                        (df['duration_minutes'] > analyzed_data['duration'] + 20)) * (WEIGHT_FACTORS['duration'] * PENALTY_FACTOR)

    df["similarity"] = 0.8 * scores + 0.05 * weights
    df['cosine_similarity'] = scaled_cosine_similarities
    df['euclidean_distance'] = scaled_euclidean_distances
    df['scores'] = scores
    df['weights'] = weights

    sorted_df = df.sort_values(by="similarity", ascending=False)

    print("Final Scores, Scores, Weights, Cosine Similarities, and Euclidean Distances:")
    print(sorted_df[["title", "similarity", "scores", "weights", "cosine_similarity", "euclidean_distance"]]
          .head(10)
          .to_string(index=False, float_format="%.6f"))


    recommendations = sorted_df.head(10).copy()

    recommendations['genres'] = recommendations['genres'].apply(
        lambda x: ", ".join(eval(x)) if isinstance(x, str) and x.startswith("[") else x
    )
    recommendations['directors'] = recommendations['directors'].apply(
        lambda x: ", ".join(eval(x)) if isinstance(x, str) and x.startswith("[") else x
    )
    recommendations['stars'] = recommendations['stars'].apply(
        lambda x: ", ".join(eval(x)) if isinstance(x, str) and x.startswith("[") else x
    )

    return recommendations[
        ["title", "rating", "genres", "release_date", "directors", "description", "duration_minutes", "stars", "url", "similarity", "cosine_similarity", "euclidean_distance", "img_path"]
    ]
