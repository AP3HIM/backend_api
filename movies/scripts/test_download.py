from movies.utils import download_movie_file

def run():
    test_url = "https://archive.org/download/SevenKeysToBaldpate1917/SEVENKEYSTOBALDPATE.mp4"
    save_directory = "media/movies"
    download_movie_file(test_url, save_directory)
