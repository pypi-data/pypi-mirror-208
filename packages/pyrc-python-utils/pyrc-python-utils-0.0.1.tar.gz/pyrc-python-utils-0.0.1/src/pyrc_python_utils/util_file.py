import os


def get_next_available_filename(path):
    base, ext = os.path.splitext(path)
    counter = 1

    while os.path.exists(path):
        path = f"{base}_{counter}{ext}"
        counter += 1

    return path
