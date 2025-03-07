import get_interests
import get_movies_links_for_interest
import get_movie_data
import error_saver as error_saver
import pandas as pd
import config
import json
import time
from tqdm import tqdm

def imdb_scrapper(default_sleep_time=5):
    # Try to load already scrapped data
    try:
        with open(config.data_save_location+"interests_movie_links.json", 'r') as f:
            interests_movie_links = json.load(f)
        print("Loaded already scrapper movie links...")
    except:
        print("Getting movie links..")
        interests=get_interests.get_interests()
        interests_movie_links={}
        number_of_genres=len(interests.keys())
        i=0
        time.sleep(default_sleep_time)
        for genre in interests.keys():
            print(f"Genre {i+1}/{number_of_genres}")
            interests_movie_links[genre]=[]
            for subgenre in interests[genre]:
                time.sleep(default_sleep_time)
                try:
                    links=get_movies_links_for_interest.get_movies_links_for_interest(subgenre[1])
                    if(links=="NO_BUTTON"):
                        continue
                    interests_movie_links[genre].extend(links)
                except TypeError:
                    print(f"Error in genre: {genre}, subgenre {subgenre}. Possible rate limit. Waiting 60s")
                    time.sleep(60)
                    links=get_movies_links_for_interest.get_movies_links_for_interest(subgenre[1])
                    interests_movie_links[genre].extend(links)
                    if(links==None):
                        print(f"Error in genre: {genre}, subgenre {subgenre}. Possible rate limit. Saving already scrapped data and continuing")
                        with open(config.data_save_location+"interests_movie_links.json", 'w') as f:
                            json.dump(interests_movie_links, f, indent=4)
                        continue
            i+=1
        with open(config.data_save_location+"interests_movie_links.json", 'w') as f:
            json.dump(interests_movie_links, f, indent=4)
    
    # Now get data for each movie
    print("Getting movie data...")
    movies=pd.DataFrame(columns=config.movie_columns)
    number_of_genres=len(interests_movie_links.keys())
    i=0
    for genre in interests_movie_links.keys():
        print(f"Genre {i+1}/{number_of_genres}")
        # Wait 60s after each genre to avoid rate limit
        if(i>0):
            time.sleep(60)
        movies_count=len(interests_movie_links[genre])
        j=0
        for movie_link in tqdm(interests_movie_links[genre], desc=f"Processing {genre}", unit="movie"):
            # Wait 5s after each movie to avoid rate limit
            time.sleep(default_sleep_time)
            movie_data=get_movie_data.get_movie_data(movie_link)
            tries=0
            flag=False
            while(type(movie_data)==str):
                if(tries>=3):
                    print(f"Problem with movie {movie_link}. Skipping")
                    error_saver.error_links_saver(movie_link)
                    flag=True
                    break
                print(f"TRY: {tries+1}Possible rate limit. Waiting 60s")
                time.sleep(60)
                movie_data=get_movie_data.get_movie_data(movie_link)
                tries+=1
            if flag:
                continue
            if movie_data is None:
                print("Possible rate limit/some of data is missing. Waiting 120s")
                time.sleep(120)
                movie_data=get_movie_data.get_movie_data(movie_link)
                if movie_data is None:
                    print("Still cannot get data for movie. Skipping")
                    error_saver.error_links_saver(movie_link)
                    continue
            if not movie_data.empty:
                try:
                    if movies['title'].str.contains(movie_data['title'][0]).any():
                        print(f"Movie {movie_data['title'][0]} already in database")
                        continue
                    movies=pd.concat([movies,movie_data], ignore_index=True)
                except Exception as e:
                    print(f"Error: {e}")
                    print(f"Movie data: {movie_data}")
                    error_saver.error_data_saver(e, movie_data, movie_link)
                    continue
            movies.to_csv(config.data_save_location+"movies_data.csv", index=False)
            j+=1
        i+=1
    movies.to_csv(config.data_save_location+"movies_data.csv", index=False)
    
    
    
imdb_scrapper()