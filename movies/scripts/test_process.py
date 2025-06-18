from movies.utils import ensure_dirs, MEDIA_MOVIE_PATH, THUMBNAIL_PATH, generate_thumbnail
import os

def run():
    ensure_dirs()

    # This is the movie file you downloaded earlier
    filename = "SEVENKEYSTOBALDPATE.mp4"
    input_path = os.path.join(MEDIA_MOVIE_PATH, filename)

    # Convert to mp4 if needed (skip here since it's already .mp4)
    mp4_output = input_path  # same file

    # Generate thumbnail
    thumbnail_filename = filename.replace(".mp4", ".jpg")
    thumbnail_path = os.path.join(THUMBNAIL_PATH, thumbnail_filename)

    success = generate_thumbnail(mp4_output, thumbnail_path)
    if success:
        print("Thumbnail created at:", thumbnail_path)
    else:
        print("Thumbnail generation failed.")
