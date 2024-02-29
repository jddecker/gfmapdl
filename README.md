# GameFAQs Map Downlaod

gfmapdl.py is a simple map download for GameFAQs contributors.

## Installation

Download the Python script and put it into a directory of your choosing. Then install the requirements:

`pip install -r requirements.txt`

This script requires the following third party libraries:
* beautifulsoup4
* filetype
* httpx
* keyboard
* latest_user_agents

## Usage

A basic command example would look like:

`python gfmapdl.py StarFighters76`

(note: use python3 command on systems with both python versions 2 and 3 installed)

This would download all the maps found in StarFighters76's profile to the following folder:

`./maps/StarFighters76`

The script will also skip any maps with the same name that is in the download folder.

## Command Line Help

This is what the argment help look like from running the command:

`python .\gfmapdl.py -h`

```
usage: gfmapdl.py [-h] [-s SAVEDIR] [-w WAIT] [-d DOWNLOADS] [--logging] [--version] [gfuser]

Supply a GameFAQs username to download all maps and charts

positional arguments:
  gfuser                gamefaqs.gamespot.com username to get maps from (required)

options:
  -h, --help            show this help message and exit
  -s SAVEDIR, --savedir SAVEDIR
                        save directory to download to (default: maps/<user>)
  -w WAIT, --wait WAIT  wait time in seconds when script needs to pause (default: 30)
  -d DOWNLOADS, --downloads DOWNLOADS
                        how many downloads before waiting (default: 150)
  --logging             print request and download information to console
  --version             show program's version number and exit
```
