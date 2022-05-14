#!/usr/bin/env python3

"""
Downloads maps from a GameFAQs profile

Might have to rerun if there are errors from too many requests
"""

import argparse
import sys
import time
from pathlib import Path

import filetype
import keyboard
import requests
from bs4 import BeautifulSoup
from latest_user_agents import get_random_user_agent


# command line arguments
parser = argparse.ArgumentParser(description='Supply a GameFAQs username to download all maps and charts')
parser.add_argument('gfuser', type=str, help='gamefaqs.gamespot.com username to get maps from (required)')
parser.add_argument('-s', '--savedir', type=str, help='save directory to download to (default: maps/<user>)')
parser.add_argument('-w', '--wait', type=int, default=30, help='wait time in seconds when script needs to pause (default: 30)')
parser.add_argument('-d', '--downloads', type=int, default=150, help='how many downloads before waiting (default: 150)')
parser.add_argument('--version', action='version', version='Release date 20220424')
args = parser.parse_args()

gfuser = requests.utils.quote(args.gfuser)
wait = args.wait
dl_loops = args.downloads

if not args.savedir:
    savedir = Path(f'maps/{gfuser}')
else:
    savedir = Path(args.savedir)

# some settings for headers and urls
base = 'https://gamefaqs.gamespot.com'
profile = f'{base}/community/{gfuser}/contributions'
profile_maps = f'{profile}/maps'
headers = {
    'User-Agent': get_random_user_agent(),
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': profile,  # initial referer
    'Dnt': '1'
}

# function to remove illegal and annoying filename characters
def sanitize(string) -> str:
    """ Remove bad filename characters from string """
    chars = '<>:"\'/\\|?*'
    for char in chars:
        string = string.replace(char, '')
    return string

# create a session to reuse
s = requests.Session()
s.headers.update(headers)
page = s.get(profile_maps)
if page.status_code != requests.codes.ok:
    print(f'Error {page.status_code}: Could not access maps contribution page at: {profile}')
    sys.exit()
soup = BeautifulSoup(page.text, 'html.parser')
results = soup.find_all('a', {'class': 'link_color'})
if len(results) == 0:
    print(f'{gfuser}\'s profile at {profile_maps} contained no maps')
    sys.exit()

# get list of dict with filename without extension (game - console - map name) and url to map
maps = []
for result in results:
    link = result['href']
    map = sanitize(result.text)
    game = sanitize(result.find_parent('div', {'class': 'content'}).find('a').text)
    console = sanitize(result.find_parent('div', {'class': 'pod'}).find('h3', {'class': 'title'}).text)
    maps.append({'filename': f'{game} - {console} - {map}', 'url': f'{base}{link}'})

# make save dir if doesn't exist
if not savedir.is_dir():
    savedir.mkdir(parents=True, exist_ok=True)
    print(f'Created and saving to dir: {savedir.resolve()}')
else:
    print(f'Saving to dir: {savedir.resolve()}')

# loop and save files. counters for report
print(f'{len(maps)} maps found in {gfuser}\'s profile')
print('Starting downloads. Press Q to end early. (might not work while waiting)')
i = 0
dl_num = 0
err_num = 0
skip_num = 0
for map in maps:
    filename = Path(savedir / map['filename'])
    url = map['url']

    # skip download if file already exists
    skip_to_next = False
    img_exts = ['', '.dwg', '.xcf', '.jpg', '.jpeg', '.jpx', '.png', '.apng', '.gif', '.webp', '.cr2', '.tif', '.tiff', '.bmp', '.jxr', '.psd', '.ico', '.heic']
    for ext in img_exts:
        if Path(f'{filename}{ext}').is_file():
            print(f'Skipped: {filename.name}{ext}')
            skip_num += 1
            skip_to_next = True
            continue
    if skip_to_next:  # skip to next download if matched a file ext
        skip_to_next = False
        continue

    # using split to figure out img url
    url_split1 = url.rsplit('/', 1)
    url_split2 = url_split1[1].split('-', 1)
    url_part1 = url_split1[0]
    url_part2 = url_split2[0]
    img = f'{url_part1}/{url_part2}?raw=1'

    # downloading image and writing as filename
    img_dl = s.get(img, stream=True, headers={'Referer': profile_maps})
    if img_dl.status_code != requests.codes.ok:
        print(f'Error {img_dl.status_code}: {img} (name: {filename.name})')
        err_num += 1
        print(f'Waiting: {wait} seconds')
        time.sleep(wait)
        continue
    with open(filename, 'wb') as f:
        for chunk in img_dl.iter_content(chunk_size=4096):
            f.write(chunk)
        dl_num += 1
    
    # renaming file based on guessed type
    kind = filetype.guess(filename)
    if kind is not None:
        filename = filename.rename(f'{filename}.{kind.extension}')
    print(f'Downloaded: {filename.name}')

    # counter for wait time
    i += 1
    if i % dl_loops == 0:
        print(f'Waiting: {wait} seconds')
        time.sleep(wait)
    if keyboard.is_pressed('q'):
        print('*** Q pressed! Stopping downloads early! ***')
        break

# end report
files_num = 0
for file in savedir.iterdir():
    if file.is_file():
        files_num += 1

maps_num = len(maps)

print(f'Files in folder: {files_num}')
print(f'Maps in profile: {maps_num}')
print(f'Downloaded: {dl_num}')
print(f'Skipped: {skip_num}')
print(f'Download errors: {err_num}')
print(f'Downloads left: {maps_num - dl_num - skip_num - err_num}')
