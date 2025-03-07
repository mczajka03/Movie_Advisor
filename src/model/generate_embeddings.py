import pandas as pd
import torch
import numpy as np
from transformers import BertTokenizer, BertModel
import pickle
from sentence_transformers import SentenceTransformer


def generate_and_save_embeddings(data_path, embeddings_path, model_name='bert-base-uncased'):

    print("Loading preprocessed data...")
    df = pd.read_csv(data_path)

    print(f"Loading BERT model and tokenizer ({model_name})...")
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertModel.from_pretrained(model_name)

    print("Generating embeddings...")
    embeddings = []
    for text in df['combined_text']:
        inputs = tokenizer(text, return_tensors='pt', max_length=512, truncation=True, padding='max_length')
        outputs = model(**inputs)

        cls_embedding = outputs.last_hidden_state[:, 0, :].squeeze(0).detach().numpy()
        embeddings.append(cls_embedding)

    embeddings_array = np.array(embeddings)

    print(f"Saving embeddings to {embeddings_path}...")
    with open(embeddings_path, 'wb') as f:
        pickle.dump(embeddings_array, f)

    print("Embedding generation complete.")


def lightweight_generate_and_save_embeddings(data_path, embeddings_path, model_name='all-MiniLM-L6-v2'):
    print("Loading preprocessed data...")
    df = pd.read_csv(data_path)

    print(f"Loading Sentence-BERT model ({model_name})...")
    model = SentenceTransformer(model_name)

    print("Generating embeddings...")
    embeddings = model.encode(df['combined_text'].tolist(), convert_to_tensor=True)

    print(f"Saving embeddings to {embeddings_path}...")
    with open(embeddings_path, 'wb') as f:
        pickle.dump(embeddings, f)

    print("Embedding generation complete.")

def generate_and_save_embeddings_with_trust_remote_code(data_path, embeddings_path, model_name='Alibaba-NLP/gte-large-en-v1.5'):
    print("Loading preprocessed data...")
    df = pd.read_csv(data_path)

    print(f"Loading ({model_name})...")
    model = SentenceTransformer(model_name,trust_remote_code=True)

    print("Generating embeddings...")
    embeddings = model.encode(df['combined_text'].tolist(), convert_to_tensor=True)

    print(f"Saving embeddings to {embeddings_path}...")
    with open(embeddings_path, 'wb') as f:
        pickle.dump(embeddings, f)

    print("Embedding generation complete.")


data_path = "../../data/preprocessed_data.csv"
bert_embeddings_path = "../../data/bert_embeddings.pkl"
sentence_transformer_embeddings_path = "../../data/sentence_transformer_embeddings.pkl"
sentence_bert_embeddings_path = "../../data/sentence_bert_embeddings.pkl"
alibaba_embeddings_path = "../../data/alibaba_embeddings.pkl"

print("Generating embeddings with lightweight model all-MiniLM-L6-v2 ...")
lightweight_generate_and_save_embeddings(data_path, sentence_transformer_embeddings_path, model_name='all-MiniLM-L6-v2')

print("Generating embeddings with BERT...")
generate_and_save_embeddings(data_path, bert_embeddings_path, model_name='bert-base-uncased')

print("Generating embeddings with Sentence BERT...")
lightweight_generate_and_save_embeddings(data_path, sentence_bert_embeddings_path, model_name='paraphrase-mpnet-base-v2')

print("Generating embeddings with Alibaba model...")
generate_and_save_embeddings_with_trust_remote_code(data_path, alibaba_embeddings_path, model_name='Alibaba-NLP/gte-large-en-v1.5')