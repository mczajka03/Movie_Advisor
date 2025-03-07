import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from flask import Flask, render_template, request
import pandas as pd
from transformers import BertTokenizer, BertModel
from sentence_transformers import SentenceTransformer
from src.model.recommend_movies import recommend_movies, load_embeddings

app = Flask(__name__,static_folder="assets")

data_path = "data/preprocessed_data.csv"
bert_embeddings_path = "data/bert_embeddings.pkl"
sentence_transformer_embeddings_path = "data/sentence_transformer_embeddings.pkl"
sentence_bert_embeddings_path = "data/sentence_bert_embeddings.pkl"
alibaba_embeddings_path = "data/alibaba_embeddings.pkl"

df = pd.read_csv(data_path)

bert_tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
bert_model = BertModel.from_pretrained("bert-base-uncased")
sentence_transformer_model = SentenceTransformer("all-MiniLM-L6-v2")
sentence_bert_model = SentenceTransformer("paraphrase-mpnet-base-v2")
alibaba_model= SentenceTransformer("Alibaba-NLP/gte-large-en-v1.5",trust_remote_code=True)

bert_embeddings = load_embeddings(bert_embeddings_path)
sentence_transformer_embeddings = load_embeddings(sentence_transformer_embeddings_path)
sentence_bert_embeddings = load_embeddings(sentence_bert_embeddings_path)
alibaba_embeddings=load_embeddings(alibaba_embeddings_path)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form.get("description", "").strip() 
        if not user_input:
            return render_template(
                "index.html",
                error="Please provide a description to get movie recommendations."
            )

        model_type = request.form.get("model_type", "")
        performance_choice = request.form.get("preference_choice", "")
        similarity_metric = request.form.get("similarity_metric", "")
        
        if model_type == "bert":
            model = bert_model
            tokenizer = bert_tokenizer
            embeddings = bert_embeddings
        elif model_type == "sentence-transformer":
            model = sentence_transformer_model
            tokenizer = None
            embeddings = sentence_transformer_embeddings
        elif model_type == "sentence-bert":
            model = sentence_bert_model
            tokenizer = None
            embeddings = sentence_bert_embeddings
        elif model_type == "alibaba":
            model=alibaba_model
            tokenizer=None
            embeddings=alibaba_embeddings
        else:
            return "Invalid model type selected.", 400
        
        recommendations = recommend_movies(
            user_input, 
            df, 
            embeddings, 
            model_type, 
            model, 
            tokenizer, 
            performance_choice, 
            similarity_metric
        )

        return render_template(
            "results.html",
            recommendations=recommendations.to_dict(orient="records"),
            user_prompt=user_input,
            performance_choice=performance_choice,
            similarity_metric=similarity_metric 
        )

    return render_template("index.html")



if __name__ == "__main__":
    app.run(debug=True)
