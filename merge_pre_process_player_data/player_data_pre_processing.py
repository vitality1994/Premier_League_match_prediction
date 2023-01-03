# 2 Steps of player data pre-processing
# 1. Decide how many attributes we will use to make player dataset. (How many features for player dataset?)
# 2. Impute missing values. (Not all players have fm_attributes & some players does not have all of selected official stats)


# Import packages
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import copy

# Function for reading json file as a list
def read_jsonl_file(path):
    json_lines = []
    with open(path, 'r') as f:
        for line in f:
            json_lines.append(json.loads(line.strip()))
    return json_lines


# Import required players' id data and players' official/fm features
# *players who played from season 2012-13 ~ 2021-22
required_players_id = read_jsonl_file('/Users/jooyong/github_locals/CSCI5525_project/merge_pre_process_player_data/team_ids_player_ids.json')


list_all_keys_needed = []
for i in range(len(required_players_id)):
    temp = required_players_id[i]['home_players']+required_players_id[i]['away_players']
    for k in temp:
        list_all_keys_needed.append(str(k))
list_all_keys_needed = list(set(list_all_keys_needed))


with open('/Users/jooyong/github_locals/CSCI5525_project/merge_pre_process_player_data/merged_player_data.json') as f:
    merged_player_data = json.load(f)


# Make lists of selected attributes of a field player and a goalkeeper.
selected_atts_field = [('appearances', 9390),
                        ('losses', 9249),
                        ('wins', 9078),
                        ('draws', 9024),
                        ('clean_sheet', 8160),
                        ('yellow_card', 8133),
                        ('goal_assist', 7035),
                        ('goals', 6957),
                        ('mins_played', 6798),
                        ('attempts_conceded_ibox', 6753),
                        ('touches', 6693),
                        ('game_started', 6687),
                        ('total_pass', 6684),
                        ('accurate_pass', 6678),
                        ('total_fwd_zone_pass', 6663),
                        ('goals_conceded', 6657),
                        ('poss_lost_all', 6657),
                        ('poss_lost_ctrl', 6657),
                        ('total_final_third_passes', 6651),
                        ('accurate_fwd_zone_pass', 6648),
                        ('total_back_zone_pass', 6645)]

selected_atts_keeper = [('appearances', 804),
                        ('losses', 774),
                        ('draws', 741),
                        ('wins', 726),
                        ('clean_sheet', 720),
                        ('mins_played', 573),
                        ('attempts_conceded_ibox', 570),
                        ('game_started', 570),
                        ('accurate_back_zone_pass', 567),
                        ('accurate_pass', 567),
                        ('attempts_conceded_obox', 567),
                        ('poss_lost_all', 567),
                        ('poss_lost_ctrl', 567),
                        ('total_back_zone_pass', 567),
                        ('total_long_balls', 567),
                        ('total_pass', 567),
                        ('touches', 567),
                        ('long_pass_own_to_opp', 564),
                        ('total_fwd_zone_pass', 564),
                        ('accurate_long_balls', 561),
                        ('final_third_entries', 561)]


list_selected_atts_field = []
for i in selected_atts_field:
    list_selected_atts_field.append(i[0])

list_selected_atts_keeper = []
for i in selected_atts_keeper:
    list_selected_atts_keeper.append(i[0])



# Discard players who is not in list_all_keys_needed from merged_player_data
for i in list(merged_player_data.keys()):
    if i not in list_all_keys_needed:
        del(merged_player_data[i])
