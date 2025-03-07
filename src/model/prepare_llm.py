import os
import requests
from tqdm import tqdm

def prepare_mistral(model_name = "mistral-7b-instruct-v0.1.Q4_0.gguf"):
    model_url = f"https://gpt4all.io/models/{model_name}"
    model_dir = os.path.expanduser("~/.gpt4all/")
    model_path = os.path.join(model_dir, model_name)

    os.makedirs(model_dir, exist_ok=True)

    if not os.path.exists(model_path):
        print("Model not found. Downloading...")
        response = requests.get(model_url, stream=True)
        total_size = int(response.headers.get('content-length', 0))

        with open(model_path, 'wb') as file, tqdm(
                desc="Downloading model",
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                file.write(data)
                bar.update(len(data))

        print(f"Model downloaded and saved at: {model_path}")

    else:
        print(f"Model already exists: {model_path}")
        

