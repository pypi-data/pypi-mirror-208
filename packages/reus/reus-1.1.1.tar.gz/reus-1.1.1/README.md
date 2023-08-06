[![PyPI version fury.io](https://badge.fury.io/py/reus.svg)](https://pypi.org/project/reus/) [![Lifecycle:
experimental](https://img.shields.io/badge/lifecycle-experimental-orange.svg)](https://www.tidyverse.org/lifecycle/#experimental) [![Twitter
Follow](https://img.shields.io/twitter/follow/ishep123?style=social)](https://twitter.com/ishep123) [![Twitter
Follow](https://img.shields.io/twitter/follow/theFirmAISports?style=social)](https://twitter.com/theFirmAISports)


## Soccer/Football Team Information

This package is designed to extract match statistics and league information from fbref in addition to player and team information from transfermarkt. Specific shoutout to [worldfootballR](https://github.com/JaseZiv/worldfootballR) and their associated [dataset](https://github.com/JaseZiv/worldfootballR_data) that provided the inspiration to build the python version.

## Installation

You can install reus from [PyPi](https://pypi.org/project/reus/) with:

``` python
pip install reus
```

Then to import the package:

``` python
import reus
```

Please scrape responsibly. Do not make calls faster than 1 per 3 seconds. If you are iterating over multiple pages, please use a sleep time of at least 3 seconds.

```python
time.sleep(4)
```

It is a minor inconvenience to you but lets us all keep accessing the data.

Additional documentation is provided [here](https://ian-shepherd.github.io/reus/)

## Roadmap
  - add fotmob league table and statistics functionality
  - translation function for players and teams
  - change outputs of fbref functions from lists and tuples to dictionaries
  - fbref player scouting reports
  - transfermarkt team staff
  - transfermarkt staff history
  - understat data


## Resources
  - [FBref](https://fbref.com/)
  - [Fotmob](https://www.fotmob.com/)
  - [Transfermarkt](http://transfermarkt.com/)
  - [FC Python](https://fcpython.com/)
  - [538](https://fivethirtyeight.com/)