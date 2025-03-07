import requests
from bs4 import BeautifulSoup
import config
import json
import re

"""
QUICK INFO
url - url of interest
save=False - if True save to file movies_links.json
Return list of urls

Get 25 movies links for ONE interest from imdb
link format: imdb.com/title/ttXXXXXXX/
"""



def get_movies_links_for_interest(url, save=False):
    site = requests.get(url, headers=config.headers)
    soup=BeautifulSoup(site.text, 'html.parser')
    # Find button to get only movies
    button = soup.find('a', {
    'class': 'ipc-chip ipc-chip--on-baseAlt',
    'data-testid': 'chip-see-all-movies'
})
    if button:
        results=[]
        # add sort by number of votes descending to get only popular movies
        movies_url="https://www.imdb.com"+button['href']+"&sort=num_votes,desc"
        site = requests.get(movies_url, headers=config.headers)
        soup=BeautifulSoup(site.text, 'html.parser')
        urls=soup.find_all(
            'a'
        )
        for url in urls:
            if url['href'].startswith("/title/tt"):
                base_url=re.match(r'/title/tt[0-9]+/', url['href'])
                complete_url="https://www.imdb.com"+base_url.group()
                if complete_url not in results:
                    results.append(complete_url)
    else:
        return "NO_BUTTON"
    if save:    
        with open(config.data_save_location+'movies_links.json', 'w') as f:
            json.dump(results, f, indent=4)
    else:
        return list(set(results))