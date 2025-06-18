# movies/utils.py
import os
import subprocess
import requests

BASE_MEDIA_PATH = os.path.join("media", "movies")
MEDIA_MOVIE_PATH = BASE_MEDIA_PATH
THUMBNAIL_PATH = os.path.join(BASE_MEDIA_PATH, "thumbnails")

def ensure_dirs():
    os.makedirs(MEDIA_MOVIE_PATH, exist_ok=True)
    os.makedirs(THUMBNAIL_PATH, exist_ok=True)

def convert_to_mp4(input_path, output_path):
    try:
        subprocess.run([
            "ffmpeg", "-i", input_path, "-c:v", "libx264", "-c:a", "aac",
            "-strict", "experimental", output_path
        ], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def generate_thumbnail(video_path, thumbnail_path, time="00:00:10"):
    try:
        subprocess.run([
            "ffmpeg", "-ss", time, "-i", video_path, "-frames:v", "1",
            "-q:v", "2", thumbnail_path
        ], check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    
def download_movie_file(url, save_dir):
    ensure_dirs()
    os.makedirs(save_dir, exist_ok=True)
    filename = os.path.join(save_dir, url.split("/")[-1])
    response = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return filename
