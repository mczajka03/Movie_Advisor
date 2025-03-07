import requests
from bs4 import BeautifulSoup
import config
import json
import re
import pandas as pd
import html
"""
QUICK INFO
returns DataFrame with columns from config.movie_columns
or return None if movie (part of movie data) not found

url - url of movie
main_genre - main genre of movie
save=False - if True save to file movie_data.json
iter - number of done tries to get data

MAXIMUM NUMBER OF TRIES = 3
Gets data for one movie from imdb
Return DataFrame with columns from config.movie_columns
"""


def get_movie_data(url, save=False):
    result=pd.DataFrame(columns=config.movie_columns)
    not_found_flag=False
    # Version using requests
    try:
        site = requests.get(url, headers=config.headers)
    except requests.exceptions.ConnectionError:
        print("Connection error. Trying again")
        return "CONNECTION_ERROR"
    soup=BeautifulSoup(site.text, 'html.parser')
    
    """# Version using selenium
    try:
        chrome_options = Options()
        #chrome_options.add_argument("--headless")  # Tryb bez interfejsu graficznego
        chrome_options.add_argument("--window-size=1920,1080")  # Ustaw wymiary okna
        
        driver = webdriver.Chrome(options=chrome_options)
        
        driver.get(url)
        site=driver.page_source
        soup=BeautifulSoup(site, 'html.parser')
    except:
        print("Connection error. Trying again")
        return "CONNECTION_ERROR"
    """
    
    # Title
    title=soup.find(
        "h1",{"data-testid":"hero__pageTitle"}
    )
    if title:
        title=title.text.strip()
        result.loc[0, "title"]=title
    else:
        not_found_flag=True
    # Release date and duration
    details_row=soup.find(
        "ul",{"role":"presentation", "class":"ipc-inline-list ipc-inline-list--show-dividers sc-ec65ba05-2 joVhBE baseAlt"}
    )
    if details_row:
        details=details_row.find_all("li")
        for detail in details:
            text=detail.text.strip()
            if re.match(r"^[0-9]{4}$", text):
                result.loc[0, "release_date"]=text
            if re.match(r"^[0-9]*h [0-9]*m", text):
                result.loc[0, "duration"]=text
    else:
        not_found_flag=True
    
    # Find genres
    genres_row=soup.find("div",
                         {"data-testid":"interests"}
    )
    if genres_row:
        genres=genres_row.find_all("a",
                                {"class":"ipc-chip ipc-chip--on-baseAlt"})
        found_genres=[]
        for genre in genres:
            genre_text=genre.text.strip()
            found_genres.append(genre_text)
        found_genres.sort()
        result.loc[0, "genres"]=found_genres
    else:
        not_found_flag=True
        
    # Find rating
    rating=soup.find("span",
                     {"class":"sc-d541859f-1 imUuxf"}
    )
    if rating:
        rating=float(rating.text.strip())
        result.loc[0, "rating"]=rating
    else:
        not_found_flag=True

    # Find description
    # Description is sometimes cut due to it's length.
    # Easiest way to get it all is to look for 
    # script that renders it in desired length 
    # and get it all from variable which stores description.
    
    try:
        found_script=soup.find("script", {"type":"application/ld+json"})
        script=json.loads(found_script.text.strip())
        description=script.get("description")
        description=html.unescape(description)
    except:
        print("Error getting description")
        description=""
    if(description!=""):
        result.loc[0, "description"]=description
    else:
        not_found_flag=True
        
    
    # Find directors
    directors=[]
    stars=[]
    # There are 3 rows on IMDB page in order: directors,writers,stars
    cast_rows=soup.find_all("div",
                            "ipc-metadata-list-item__content-container")
    if cast_rows:
        directors_links=cast_rows[0].find_all("a")
        for director in directors_links:
            directors.append(director.text.strip())
        result.loc[0, "directors"]=directors
        stars_links=cast_rows[2].find_all("a")
        for star in stars_links:
            stars.append(star.text.strip())
        result.loc[0, "stars"]=stars
    else:
        not_found_flag=True
        
    # Find storyline
    
    # Due to the fact that movie page has lazy loading
    # we need to go to the page that contains plotsummary
    
    plot_summary_url=url+"plotsummary/"
    plot_summary_site=requests.get(plot_summary_url, headers=config.headers)
    plot_summary_soup=BeautifulSoup(plot_summary_site.text, 'html.parser')
    summaries=plot_summary_soup.find_all(
        "li",
        {"class":"ipc-metadata-list__item"}
    )
    if summaries:
        text_summaries=[]
        for summary in summaries:
            if summary!=None:
                try:
                    plot_summary=summary.find("div",
                                            {"class":"ipc-html-content-inner-div"}).text.strip()
                except AttributeError:
                    continue
                if plot_summary:
                    text_summaries.append(plot_summary)
        # Pick 2nd longest summary (if only one, pick it, if none, pick empty string)
        if len(text_summaries) > 1:
            longest_summary = sorted(text_summaries, key=len)[-2]
        else:
            longest_summary = text_summaries[0] if text_summaries else ""
        # Remove author of the summary
        if "—" in longest_summary:
            longest_summary = longest_summary.split("—")[0].strip()
        result.loc[0, "storyline"] = longest_summary
    else:
        not_found_flag=True
        
    
    # Find keywords
    # also different url than main movie page
    keywords=[]
    keywords_url=url+"keywords/"
    keywords_site=requests.get(keywords_url, headers=config.headers)
    keywords_soup=BeautifulSoup(keywords_site.text, 'html.parser')
    all_keywords=keywords_soup.find_all("a",
                                        {"class":"ipc-metadata-list-summary-item__t"})
    if all_keywords:
        for keyword in all_keywords:
            if(keyword):
                try:
                    keyword_text=keyword.text.strip()
                    if keyword_text:
                        keywords.append(keyword_text) if len(keywords)<5 else None
                except AttributeError:
                    continue
        if(len(keywords)==0):
            keywords=[""]
        result.loc[0, "keywords"]=keywords
    else:
        not_found_flag=True
    
    # Set url
    result.loc[0, "url"]=url
    
    if not_found_flag:
        print("One (many) of the movie data not found")
        return None
    else:
        if save:    
            result.to_csv(config.data_save_location+"movie_data.csv", index=False)
        else:
            return result