import pathlib
def is_img(file_path):
    return  pathlib.Path(file_path).suffix in (".jpg", ".png", ".bmp")

def is_video(file_path):
    return pathlib.Path(file_path).suffix in (".mp4", ".avi", ".mkv")