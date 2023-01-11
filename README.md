# Predicting Outcomes of the Premier League Matches Using Real World and Computer Game Data 


## Motivation
There has been a lot of interest in predicting match outcomes of football (or soccer) games as the sport is hugely popular with a large fan base and enjoys much media attention. Predictions of match outcomes may be useful for stakeholders within the sport, such as managers, journalists, analysts, bookmakers, etc., as such information can be utilized to make risk assessments and plan strategies.

## Goal
- Construct comprehensive dataset include official player statistics and in-game attributes for football prediction.
- Predict English Premier League match results using different models, such as Elo Rating System, Support Vector Machine(SVM), RandomForest(RF), and Heterogeneous Graph Convolutional Network (HGCN).

## Details of Folders
### fm_inside/fm_inside_scraper
This folder includes web scrapers to extract in-game attributes of players from the [FMinside](https://fminside.net/players)
- [list_links.py](fm_inside/fm_inside_scraper/list_links.py) will generate [list_links.txt](fm_inside/fm_inside_scraper/list_links.txt) includes each link of a player. Links will be used in [fm_inside_spider.py](fm_inside/fm_inside_scraper/fm_inside_scraper/spiders/fm_inside_spider.py) and this file will generate [fm_players.json](fm_inside/fm_inside_scraper/fm_inside_scraper/spiders/fm_players.json) includes fm attributes of each player.
## premier_official_data
This folder includes web scrapers to extract players' official statistics and official match details from the [Premier Leagure Official Website](https://www.premierleague.com/matchweek/7847/blog)
## Analysis

## datasets

## Experiments

