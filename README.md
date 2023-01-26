# Predicting Outcomes of the Premier League Matches Using Real World and Computer Game Data 


## Motivation
There has been a lot of interest in predicting match outcomes of football (or soccer) games as the sport is hugely popular with a large fan base and enjoys much media attention. Predictions of match outcomes may be useful for stakeholders within the sport, such as managers, journalists, analysts, bookmakers, etc., as such information can be utilized to make risk assessments and plan strategies.

<br/>

## Goal
- Construct comprehensive dataset include official player statistics and in-game attributes for football prediction.
- Predict English Premier League match results using different models, such as Elo Rating System, Support Vector Machine(SVM), RandomForest(RF), and Heterogeneous Graph Convolutional Network (HGCN).

<br/>

## Details of Folders

<br/>

### fm_inside/fm_inside_scraper
This folder includes web scrapers to extract in-game attributes of players from the [FMinside](https://fminside.net/players)
- [list_links.py](./fm_inside/fm_inside_scraper/list_links.py) generates [list_links.txt](./fm_inside/fm_inside_scraper/list_links.txt) includes each link of a player. Links will be used in [fm_inside_spider.py](./fm_inside/fm_inside_scraper/fm_inside_scraper/spiders/fm_inside_spider.py) and this file generates [fm_players.json](./fm_inside/fm_inside_scraper/fm_inside_scraper/spiders/fm_players.json) includes fm attributes of each player.

<br/>

### premier_official_data
This folder includes web scrapers to extract players' official statistics and official match details from the [Premier Leagure Official Website](https://www.premierleague.com/matchweek/7847/blog)
- club_match_official:
    - [crawl_matches.py](./premier_official_data/club_match_official/crawl_matches.py) generates brief information of each match from [season 2012-13](./premier_official_data/club_match_official/matches/season_2012-13.json) to [season 2021-22](./premier_official_data/club_match_official/matches/season_2021-22.json)
    - [crawl_match_details.py](./premier_official_data/club_match_official/crawl_match_details.py) generates **details** of each match from [season 2012-13 (details)](./premier_official_data/club_match_official/matches/season_2012-13.details.json) to [season 2021-22 (details)](./premier_official_data/club_match_official/matches/season_2021-22.details.json) using json files generated by *crawl_matches.py*.
    
### analysis
We observed that not every player has the same diversity of all-season official statistics. Therefore, selecting some from all statistics was necessary to ensure each player had the same features. For the selection, we sorted official statistics in descending order in terms of how many times each statistic is observed in the player data and calculated the percentage of players who contains the top’ n’ statistics. We decided to use the top 21 statistics and sampled approximately 41% of players who included all of those statistics. The significant common characteristic of most players not included in the sample is that the last season those players played was before season 2012-13. Therefore, we decided to discard players who never had a match from season 2012-13 to 2021-22. This [Jupyter Notebook](./Analysis/Selecting_official_attributes.ipynb) shows the codes and process for discarding some statistics of a player and some players.


### datasets
Each of [files final_data_field_players.json](datasets/final_dataset_field_players.json) and [final_dataset_goalkeepers.json](datasets/final_dataset_goalkeepers.json) includes 1499 field players and 128 goal-keepers respectively. Each player’s data includes 2 attributes: players’ all season official statistics and in-game attributes. For all season official statistics, a field player contains 22 attributes, such as touches, successful_final_third_passes, poss_lost_all, and accurate_pass, and a goalkeeper contains 22 attributes as goal_kicks, saves, ball_recovery, and saves. For in-game data, a field player contains 42 attributes, such as corners, crossing, and dribbling, and a goalkeeper contains 44 attributes, such as aerial reach, punching, rushing out, one-and-one, and kicking.


### experiments
Three different mathods are used for expriments (training the model and predicting match outcomes). 

- [Elo rating system](experiments/EloUpdated.ipynb): It was created by Arpad Elo, is an effective method to calculate the relative strengths of players or teams with respect to their opponents. After fitting the system to learn each team’s relative strengths, we can predict the probability of the outcome of the match.

- We conducted [6 baseline experiments with Support Vector Machin (SVM) and Random Forest Machine Learning models](experiments/SVM_RandomForest.py) to predict match results when:
    1. all_season_official_statistics are given to each player.
    2. in_game_attributes are given to each player.
    3. all_season_official_statistics and in_game_attributes are given to each player.
    4. Selected all_season_official_statistics (field player: 17, goalkeeper: 16) are given to each player. 5. Selected in_game_attributes (field player: 3, goalkeeper: 4) are given to each player.
    6. Selected all_season_official_statistics and in_game_attributes are given to each player.

<br/>

- We created a [large HGCN network](experiments/graph) for each season and evaluated the network at per season level. The task here is to classify the type of edges between team-team nodes.

- [Feature_importances](experiments/Feature_importances.ipynb): To better understand the models we trained, We observed the importance of each feature using the function RandomForestClassi- fier.feature_importances_. There are features that have high importance commonly in terms of player role between field player and goalkeeper.


