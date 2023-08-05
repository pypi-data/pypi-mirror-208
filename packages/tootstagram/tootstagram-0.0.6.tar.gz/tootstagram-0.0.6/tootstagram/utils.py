"""
Copyright (c) 2023, Koen Martens <kmartens@sonologic.se>

Licensed under a hippocratic license. License terms can be found in
LICENSE.md or online:

https://firstdonoharm.dev/version/3/0/bds-cl-eco-extr-ffd-media-my-soc-sv-tal-xuar.md

"""
import shutil

import requests


def download_file(url: str, local_filename: str) -> None:
    with requests.get(url, stream=True) as src, open(local_filename, 'wb') as dst:
        shutil.copyfileobj(src.raw, dst)
