# GameFAQs Map Download

gfmapdl is a simple map downloader for GameFAQs contributors.

## Installation

Releases come in two versions

| File                                                                                    | Description                                           |
| --------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| [gfmapdl](https://github.com/jddecker/gfmapdl/releases/latest/download/gfmapdl)         | Platform-independent zipapp file. Needs Python to run |
| [gfmapdl.exe](https://github.com/jddecker/gfmapdl/releases/latest/download/gfmapdl.exe) | Windows x64 binary                                    |

### Running From Source

Download the repository and then install the requirements:

`pip install -r requirements.txt`

This script requires the following third party libraries and their dependencies:
* beautifulsoup4
* filetype
* httpx
* latest_user_agents
* rich

## Usage

Platform-independent zipapp file basic usage looks like:

`./gfmapdl StarFighters76`

Or Windows x64 binary:

`.\gfmapdl.exe StarFighters76`

This would download all the maps found in StarFighters76's profile to the following folder:

`./maps/StarFighters76`

The script will also skip any maps with the same name that is in the download folder.

## Command Line Help

```
usage: gfmapdl.exe [-h] [-s SAVEDIR] [-w WAIT] [-d DOWNLOADS] [--overwrite] [--logging] [--version] [gfuser]

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
  --overwrite           overwrites existing files (useful if existing maps have been updated)
  --logging             print request and download information to console
  --version             show program's version number and exit
```

## Building

### Zipapp platform-independent file

1. Download repository
2. Create directories in the downloaded files called zipapp and dist
3. Copy gfmapdl.py to the zipapp directory
4. Rename gfmapdl.py in the zipapp directory to __main__.py
5. Install dependencies to the zipapp directory with the following command `python -m pip install -t zipapp -r requirements.txt --no-binary ":all:"`
6. Build zipapp with the command `python -m zipapp -p "/usr/bin/env python3" -c -o dist/gfmapdl zipapp`

### Binary for your platform using pyinstaller

1. Install pyinstaller with the command `python -m pip install pyinstaller`
2. Build the binary with the command `pyinstaller gfmapdl.py --onefile`
3. Finished binary is located in the dist folder
