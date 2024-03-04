"""
Downloads maps from a GameFAQs profile
"""

import argparse
import signal
import sys
import time
from pathlib import Path

import filetype
import httpx
import progressbar
from bs4 import BeautifulSoup
from latest_user_agents import get_random_user_agent

# command line arguments
parser = argparse.ArgumentParser(description="Supply a GameFAQs username to download all maps and charts")
parser.add_argument("gfuser", type=str, nargs="?", help="gamefaqs.gamespot.com username to get maps from (required)")
parser.add_argument("-s", "--savedir", type=str, help="save directory to download to (default: maps/<user>)")
parser.add_argument(
    "-w", "--wait", type=int, default=30, help="wait time in seconds when script needs to pause (default: 30)"
)
parser.add_argument("-d", "--downloads", type=int, default=150, help="how many downloads before waiting (default: 150)")
parser.add_argument(
    "--overwrite",
    default=False,
    action="store_true",
    help="overwrites existing files (useful if existing maps have been updated)",
)
parser.add_argument(
    "--logging", default=False, action="store_true", help="print request and download information to console"
)
parser.add_argument("--version", action="version", version="Release date 2024-03-03")
args = parser.parse_args()

# if no gamefaqs user specified prompt for it
if not args.gfuser:
    gfuser = input("User to download maps from: ")
else:
    gfuser = args.gfuser

# set variables from argparse
wait = args.wait
dl_loops = args.downloads
logging = args.logging
overwrite = args.overwrite

if not args.savedir:
    savedir = Path(f"maps/{gfuser}")
else:
    savedir = Path(args.savedir)


def signal_handler(sig, frame):
    end_early()


def sanitize(string) -> str:
    """Remove bad filename characters from string"""
    chars = "<>:\"'/\\|?*"
    for char in chars:
        string = string.replace(char, "")
    return string


def print_report():
    """Print ending report"""
    files_count = 0
    for file in savedir.iterdir():
        if file.is_file():
            files_count += 1
    print(f"Files in folder: {files_count}")
    print(f"Maps in profile: {maps_count}")


def end_early():
    """Stop early and exit"""
    print("*** Ctrl+C pressed! Stopping downloads early! ***")
    bar.finish(dirty=True)
    print_report()
    sys.exit()


def wait_check(response):
    """Check and wait after number of responses"""
    global req_num
    try:
        req_num += 1
    except NameError:
        req_num = 1
    global wait
    global dl_loops

    if req_num % dl_loops == 0:
        if logging:
            print(f"=== Wait {wait} seconds on request number {req_num} ===")
        time.sleep(wait)
    return


def log_request(request):
    """Print request"""
    if logging:
        print(f"{request.method} {request.url} - waiting", end="")
    return


def log_response(response):
    """Print response code"""
    if logging:
        print(f" - status {response.status_code}")
    return


# some settings for headers and urls
base = "https://gamefaqs.gamespot.com"
profile = f"{base}/community/{gfuser}/contributions"
profile_maps = f"{profile}/maps"
headers = {
    "User-Agent": get_random_user_agent(),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": profile,  # initial referer
    "Dnt": "1",
}

# create a session to reuse
s = httpx.Client(
    base_url=base,
    follow_redirects=True,
    timeout=60.0,
    headers=headers,
    event_hooks={"request": [wait_check, log_request], "response": [log_response]},
)

page = s.get(profile_maps)
if page.status_code != httpx.codes.ok:
    print(f"Error {page.status_code}: Could not access maps contribution page at: {profile}")
    sys.exit()
soup = BeautifulSoup(page.text, "html.parser")
results = soup.select("a.link_color")
if len(results) == 0:
    print(f"{gfuser}'s profile at {profile_maps} contained no maps")
    sys.exit()

# get list of dict with filename without extension (game - console - map name) and url to map
maps = []
for result in results:
    link = result["href"]
    map = sanitize(result.text)
    game = sanitize(result.find_parent("div", {"class": "content"}).find("a").text)
    console = sanitize(result.find_parent("div", {"class": "pod"}).find("h3", {"class": "title"}).text)
    maps.append({"filename": f"{game} - {console} - {map}", "url": f"{base}{link}"})
maps_count = len(maps)

# make save dir if doesn't exist
if not savedir.is_dir():
    savedir.mkdir(parents=True, exist_ok=True)
    print(f"Created and saving to dir: {savedir.resolve()}")
else:
    print(f"Saving to dir: {savedir.resolve()}")

signal.signal(signal.SIGINT, signal_handler)

widgets = [
    progressbar.Percentage(),
    " ",
    progressbar.SimpleProgress("(%(value_s)s of %(max_value_s)s)"),
    " ",
    progressbar.Bar(),
    " ",
    progressbar.Timer()
]

# loop and save files. counters for report. set new referer. progressbar
print(f"{maps_count} maps found in {gfuser}'s profile")
print(f"Will wait {wait} seconds every {dl_loops} requests")
print("Starting downloads (press ctrl+c to end early)")
i = 0
s.headers["Referer"] = profile_maps
with progressbar.ProgressBar(prefix="Downloading", widgets=widgets, min_value=i, max_value=maps_count, redirect_stdout=True) as bar:
    for map in maps:
        filename = Path(savedir / map["filename"])
        url = map["url"]

        # skip download if file already exists unless overwrite set
        skip_to_next = False
        if not overwrite:
            img_exts = [
                "",
                ".dwg",
                ".xcf",
                ".jpg",
                ".jpeg",
                ".jpx",
                ".png",
                ".apng",
                ".gif",
                ".webp",
                ".cr2",
                ".tif",
                ".tiff",
                ".bmp",
                ".jxr",
                ".psd",
                ".ico",
                ".heic",
            ]
            for ext in img_exts:
                filename_ext = Path(filename.with_suffix(ext))
                if filename_ext.is_file():
                    if filename_ext.stat().st_size == 0:  # check for blank file
                        continue
                    else:
                        if logging:
                            print(f"Skipped: {filename_ext.name}")
                        skip_to_next = True
                        continue
        if skip_to_next:  # skip to next download if matched a file ext
            skip_to_next = False
            i += 1
            bar.update(i)
            continue

        # using split to figure out img url
        url_split1 = url.rsplit("/", 1)
        url_split2 = url_split1[1].split("-", 1)
        url_part1 = url_split1[0]
        url_part2 = url_split2[0]
        img = f"{url_part1}/{url_part2}?raw=1"

        # downloading image and writing as filename.tmp
        filename_temp = Path(filename.with_suffix(".tmp"))
        with open(filename_temp, "wb") as f:
            with s.stream("GET", img) as r:
                for chunk in r.iter_bytes():
                    f.write(chunk)

        # renaming file based on guessed type
        file_type = filetype.guess(filename_temp)
        new_ext = f".{file_type.extension}"
        if file_type is not None:
            if overwrite:
                filename_new = filename_temp.replace(filename.with_suffix(new_ext))
            else:
                filename_new = filename_temp.rename(filename.with_suffix(new_ext))

        if logging:
            print(f"Downloaded: {filename_new.name}")

        # progressbar update
        i += 1
        bar.update(i)

print("\n*** DONE ***")
print_report()
