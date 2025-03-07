import config

def error_links_saver(error_link):
    with open(config.data_save_location+"error_links.txt", 'a') as f:
        f.write(error_link+"\n")
        
def error_data_saver(e, movie_data, movie_link):
    with open("error_data.txt", "a") as f:
                        f.write(f"Error: {e}\n")
                        f.write(f"Movie data: {movie_data}\n")
                        f.write(f"Movie link: {movie_link}\n")
                        f.write("\n\n")