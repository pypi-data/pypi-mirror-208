#!python3
from eyes_soatra import eyes
import jellyfish
import urllib 
from urllib.request import urlopen
import requests
import pandas
import random


a = eyes.view_page(
    url='https://www.hokkaido-esashi.jp/modules/lifeinfo/content0937.html',
    show_highlight=True,
    show_header=True,
    allow_redirects=True,
)

print(a)