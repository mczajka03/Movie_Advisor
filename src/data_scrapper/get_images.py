import pandas as pd
import time
import requests
import re
import config

# Function to get image (poster for movie) from the url

def get_image(url,id):
    time.sleep(5)
    headers = config.headers
    default_img_path="assets/static/default.jpg"
    try:
        # Get main page
        response=requests.get(url,headers=headers)
        if(response.status_code!=200):
            return default_img_path
        match=re.findall(r'https://m\.media-amazon\.com/images/[^\s"<>]+\.jpg',response.text)
        # Perfect resolution image for our use case is always the 8th link 
        small_img_url=match[7]
        response=requests.get(small_img_url,headers=headers)
        if(response.status_code!=200):
            return default_img_path
        # Save image
        with open(f"src/app/assets/static/{id}.jpg", 'wb') as f:
            f.write(response.content)
        print("Image saved")
        return f"assets/static/{id}.jpg"
    except Exception as e:
        print(e)
        return default_img_path

data_path = "data/movies_data.csv"

# Edit movies_data.csv to include image path

def get_images(data):
    data["img_path"] = data.apply(lambda row: get_image(row['url'], row.name), axis=1)
    data.to_csv(data_path, index=False)

# Uncomment the below line to get images

get_images(pd.read_csv(data_path))
    
