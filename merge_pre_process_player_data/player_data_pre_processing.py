# Two Steps of player data pre-processing
# 1. Decide how many attributes we will use to make player dataset. (How many features for player dataset?)
# 2. Impute missing values. (Not all players have fm_attributes & some players does not have all of selected official stats)
#   - Impute using mean value
#   - Impute using KNN algorithm


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


# Delete feature "season" because we don't need anymore
for i in merged_player_data.keys():
    del(merged_player_data[i]['seasons'])



def pre_processing_1(given_data):
    
    pre_processed_merged_player_data ={}

    data = given_data
    keys = list(merged_player_data.keys())
        
    for i in keys:

        official_dict = {}
        dict_pre_prcoessed_player = {}


        official_dict['official_stats'] = data[i]['official_stats']


        dict_pre_prcoessed_player[i] = official_dict
        dict_pre_prcoessed_player[i]['age'] = int(data[i]['entity']['age'][:2])/35

        
        if 'fm_data' in data[i].keys():
            dict_pre_prcoessed_player[i]['fm_data'] = data[i]['fm_data']['attributes']
            dict_pre_prcoessed_player[i]['fm_data']['Length'] = data[i]['fm_data']['Length']
            dict_pre_prcoessed_player[i]['fm_data']['Weight'] = data[i]['fm_data']['Weight']
            dict_pre_prcoessed_player[i]['fm_data']['Sell value'] = data[i]['fm_data']['Sell value']
            dict_pre_prcoessed_player[i]['fm_data']['Wages'] = data[i]['fm_data']['Wages']
            dict_pre_prcoessed_player[i]['fm_data']['ability'] = data[i]['fm_data']['ability']
            dict_pre_prcoessed_player[i]['fm_data']['potential'] = data[i]['fm_data']['potential']

        if  data[i]['entity']['info']['position']!='G':
            dict_pre_prcoessed_player[i]['is_keeper'] = 0 

        if  data[i]['entity']['info']['position']=='G':
            dict_pre_prcoessed_player[i]['is_keeper'] = 1 


        all_atts = list(dict_pre_prcoessed_player[i]['official_stats'].keys())

        for k in all_atts:
            
            if  data[i]['entity']['info']['position']!='G':

                if k not in list_selected_atts_field:
                    del(dict_pre_prcoessed_player[i]['official_stats'][k])
                
                    
            if  data[i]['entity']['info']['position']=='G':   

                if k not in list_selected_atts_keeper:
                    del(dict_pre_prcoessed_player[i]['official_stats'][k])


        pre_processed_merged_player_data[i] = dict_pre_prcoessed_player[i]

    return pre_processed_merged_player_data
    



def ave_atts(data):

    ave_att_dict_keeper = {}
    ave_att_dict_field = {}
    num_keeper = 0
    num_field = 0

    for i in data.keys():

        count = 0 

        if data[i]['is_keeper']==1:

            for k in data[i]['official_stats']:

                if k in list_selected_atts_keeper:
                    count+=1

            if count==21:
                num_keeper += 1

                for a in list_selected_atts_keeper:

                    if a not in ave_att_dict_keeper.keys():
                        ave_att_dict_keeper[a] = data[i]['official_stats'][a]

                    else:
                        ave_att_dict_keeper[a] += data[i]['official_stats'][a]
        


        elif data[i]['is_keeper']==0:

            for k in data[i]['official_stats']:

                if k in list_selected_atts_field:
                    count+=1


            if count==21:
                num_field += 1

                for a in list_selected_atts_field:

                    if a not in ave_att_dict_field.keys():
                        ave_att_dict_field[a] = data[i]['official_stats'][a]

                    else:
                        ave_att_dict_field[a] += data[i]['official_stats'][a]


    for i in ave_att_dict_keeper.keys():
            ave_att_dict_keeper[i] /= num_keeper

    for i in ave_att_dict_field.keys():
        ave_att_dict_field[i] /= num_field            

    print(num_field)
    print(num_keeper)

    return ave_att_dict_field, ave_att_dict_keeper

    




pre_processed_data = pre_processing_1(merged_player_data)

print(ave_atts(pre_processed_data))