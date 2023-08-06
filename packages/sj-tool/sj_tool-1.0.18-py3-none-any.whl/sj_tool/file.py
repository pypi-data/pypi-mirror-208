import os
import shutil


def makedir(path, delete_old=False):
    if delete_old:
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)
