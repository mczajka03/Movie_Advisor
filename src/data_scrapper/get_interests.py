import requests
from bs4 import BeautifulSoup
import config
import json

# Black list for unwanted genres that
# are not actually genres but appear 
# in search by naive scrapping
black_list = [
    "Popular interests",
    "Advanced search",
    "About this page",
    "Recently viewed",
]


"""
QUICK INFO:

RETURNS DICT
KEY-MAIN GENRE
VALUE-LIST OF LISTS => FOR SUBGENRE IN SUBGENRES subgenre[0]-name, subgenre[1]-url

save=False - if True save to file interests.json

Get all interests from imdb https://www.imdb.com/interest/all/
interest are all types of genres,subgenres.
Return dict with genres as keys and list of lists as values:
[
[subgenre_name,subgenre_url],
[subgenre_name,subgenre_url],...
]
"""
def get_interests(save=False):
    result = {}
    url = "https://www.imdb.com/interest/all/"
    site = requests.get(url, headers=config.headers)
    soup = BeautifulSoup(site.text, 'html.parser')
    
    # Find all sections with main interests
    interest_sections = soup.find_all('section',
                                      class_='ipc-page-section ipc-page-section--baseAlt')
    
    for section in interest_sections:
        # Find genre title (header of the section)
        genre_header = section.find('h3', class_='ipc-title__text')
        if genre_header:
            genre = genre_header.text.strip()
            if genre not in black_list:
                sub_genres=[]
                # cards from row under genre title
                cards = section.find_all(
                    'a', 
                    class_='ipc-slate-card__title ipc-slate-card__title--clickable sc-c5922af5-2 fhgilD'
                )
                for card in cards:
                    # get name of subgenre
                    sub_genre_name=card.text.strip()
                    # not necessary but better to check
                    if sub_genre_name not in black_list:
                        sub_genre_link="https://www.imdb.com"+card['href']
                        sub_genres.append([sub_genre_name, sub_genre_link])
                result[genre] = sub_genres
    
    if save:
        with open(config.data_save_location+"interest.json", 'w') as f:
            json.dump(result, f,indent=4)
    else:
        return result
