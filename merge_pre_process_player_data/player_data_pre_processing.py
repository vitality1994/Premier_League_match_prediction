# Two Steps of player data pre-processing
# 1. Decide how many attributes we will use to make player dataset. (How many features for player dataset?)
# 2. Impute missing values. (Not all players have fm_attributes & some players does not have all of selected official stats)
#   - Impute using mean value
#   - Impute using KNN algorithm


# Import packages
import json
import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer



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

    return ave_att_dict_field, ave_att_dict_keeper

    

pre_processed_data = pre_processing_1(merged_player_data)
ave_field, ave_keeper = ave_atts(pre_processed_data)



# ---------- with following codes below, we can check there are some players who does not have 
# ---------- 21 selected attributes fully all of those players include selected attributes at least 14. 
# ---------- Therefore, we can use KNN for also official_stats.

# keys_lack_stats = []

# count = 0
# count2 = 0
# keys = list(pre_processed_data.keys())
# for i in keys:
#     if len(pre_processed_data[i]['official_stats'])!=21:
#         count += 1
#         keys_lack_stats.append(i)

#     else:
#         count2 +=1

# print("total # players", len(list(pre_processed_data.keys())))
# print("total # lack player", count, len(keys_lack_stats))
# print("total # not empty", count2)



# for i in keys_lack_stats:
#     print(len(pre_processed_data[i]['official_stats'].keys()))

# --------------------------------------------------------------------------



list_keys_field = []
list_keys_keeper = []

for i in pre_processed_data.keys():

    if pre_processed_data[i]['is_keeper']==1:
        list_keys_keeper.append(i)

    else:
        list_keys_field.append(i)


fm_atts_field = pre_processed_data['4999']['fm_data'].keys()
fm_atts_keeper = pre_processed_data['4330']['fm_data'].keys()



fixed_data = {}

for i in pre_processed_data.keys():
    
    fixed_data[i] = {}

    for key, value in pre_processed_data[i]['official_stats'].items():
        fixed_data[i][key] = value
    

    if 'fm_data' in pre_processed_data[i].keys():

        for key, value in pre_processed_data[i]['fm_data'].items():
            fixed_data[i][key+'_fm'] = value

    fixed_data[i]['age'] = pre_processed_data[i]['age']
    fixed_data[i]['is_keeper'] = pre_processed_data[i]['is_keeper']



dict_field_att = {}
dict_field_age = {}
dict_field_fm = {}
dict_is_keeper_field = {}
dict_keys_field = {}


temp = []
for i in list_keys_field:
    temp.append(i)

dict_keys_field['key'] = temp


temp = []
for i in range(len(list_keys_field)):
    temp.append(0)
dict_is_keeper_field['is_keeper'] = temp

temp = []
for i in list_keys_field:
    temp.append(fixed_data[i]['age'])

dict_field_age['age'] = temp

for i in list_selected_atts_field:
    
    temp = []
    
    for k in list_keys_field:
        
        if i in fixed_data[k].keys():
            temp.append(fixed_data[k][i])
            
        else:
            
            temp.append(np.nan)
        
    dict_field_att[i] = temp

for i in fm_atts_field:
    
    temp = []
    
    for k in list_keys_field:
            
        if i+"_fm" in fixed_data[k].keys():

            temp.append(fixed_data[k][i+"_fm"])

        else:

            temp.append(np.nan)

        
    dict_field_fm[i+"_fm"]=temp

new_0 = pd.DataFrame.from_dict(dict_keys_field)
new_1 = pd.DataFrame.from_dict(dict_field_att)
new_2 = pd.DataFrame.from_dict(dict_field_age)
new_3 = pd.DataFrame.from_dict(dict_field_fm)
new_4 = pd.DataFrame.from_dict(dict_is_keeper_field)

dataframe_field = pd.concat([new_0, new_1, new_3, new_2, new_4], axis=1)


dict_keeper_att = {}
dict_keeper_age = {}
dict_keeper_fm = {}
dict_is_keeper_keeper = {}
dict_keys_keeper = {}


temp = []
for i in list_keys_keeper:
    temp.append(i)

dict_keys_keeper['key'] = temp


temp = []
for i in range(len(list_keys_keeper)):
    temp.append(1)
dict_is_keeper_keeper['is_keeper'] = temp

temp = []
for i in list_keys_keeper:
    temp.append(fixed_data[i]['age'])

dict_keeper_age['age'] = temp

for i in list_selected_atts_keeper:
    
    temp = []
    
    for k in list_keys_keeper:
        
        if i in fixed_data[k].keys():
            temp.append(fixed_data[k][i])
            
        else:
            
            temp.append(np.nan)
        
    dict_keeper_att[i] = temp

for i in fm_atts_keeper:
    
    temp = []
    
    for k in list_keys_keeper:
            
        if i+"_fm" in fixed_data[k].keys():

            temp.append(fixed_data[k][i+"_fm"])

        else:

            temp.append(np.nan)

        
    dict_keeper_fm[i+"_fm"]=temp



new_0 = pd.DataFrame.from_dict(dict_keys_keeper)
new_1 = pd.DataFrame.from_dict(dict_keeper_att)
new_2 = pd.DataFrame.from_dict(dict_keeper_age)
new_3 = pd.DataFrame.from_dict(dict_keeper_fm)
new_4 = pd.DataFrame.from_dict(dict_is_keeper_keeper)



dataframe_keeper = pd.concat([new_0, new_1, new_3, new_2, new_4], axis=1)



imputer=KNNImputer(n_neighbors=3)

filled_field=imputer.fit_transform(dataframe_field)

filled_field=pd.DataFrame(filled_field, columns=dataframe_field.columns)



imputer=KNNImputer(n_neighbors=3)

filled_keeper=imputer.fit_transform(dataframe_keeper)

filled_keeper=pd.DataFrame(filled_keeper, columns=dataframe_keeper.columns)



dict_field = filled_field.to_dict('records')

new_dict_field = {}

for i in range(len(dict_field)):
    temp = {}
    premier_stats = {}
    fm_stats = {}
    
    for n, m in dict_field[i].items():
        if n[-2:]!='fm'and n!='key' and n!='is_keeper':
            premier_stats[n] = m
        elif n[-2:]=='fm':
            fm_stats[n]=m
    
    temp['premier_stats'] = premier_stats
    temp['fm_stats'] = fm_stats
    temp['is_goalkeeper'] = 0
    
    new_dict_field[int(dict_field[i]['key'])] = temp


dict_keeper = filled_keeper.to_dict('records')

new_dict_keeper = {}

for i in range(len(dict_keeper)):
    temp = {}
    premier_stats = {}
    fm_stats = {}
    
    for n, m in dict_keeper[i].items():
        if n[-2:]!='fm'and n!='key' and n!='is_keeper':
            premier_stats[n] = m
        elif n[-2:]=='fm':
            fm_stats[n]=m
    
    temp['premier_stats'] = premier_stats
    temp['fm_stats'] = fm_stats
    temp['is_goalkeeper'] = 1
    
    new_dict_keeper[int(dict_keeper[i]['key'])] = temp



list_mins_field = []
for i in new_dict_field.keys():
    list_mins_field.append(new_dict_field[i]['premier_stats']['mins_played'])

list_mins_keeper = []
for i in new_dict_keeper.keys():
    list_mins_keeper.append(new_dict_keeper[i]['premier_stats']['mins_played'])


for i in new_dict_field.keys():
    mins_playtime = new_dict_field[i]['premier_stats']['mins_played']
        
    for m, n in new_dict_field[i]['premier_stats'].items():
        
        if m != 'age' and m != 'mins_played':
            new_dict_field[i]['premier_stats'][m] = n / mins_playtime
        
        elif m == 'mins_played':
            new_dict_field[i]['premier_stats'][m] = (n - 6) / (33374 - 6)


for i in new_dict_keeper.keys():
    mins_playtime = new_dict_keeper[i]['premier_stats']['mins_played']
    
    for m, n in new_dict_keeper[i]['premier_stats'].items():
        
        if m != 'age' and m != 'mins_played':
            new_dict_keeper[i]['premier_stats'][m] = n / mins_playtime
        
        elif m == 'mins_played':
            new_dict_keeper[i]['premier_stats'][m] = (n - 90) / (34959 - 90)


normalized_field = {}
normalized_keeper = {}

for k, v in new_dict_field.items():
    normalized_field[k] = v

for k, v in new_dict_keeper.items():
    normalized_keeper[k] = v

with open('final_dataset_field_players.json', 'w', encoding='utf-8') as make_file:
    json.dump(normalized_field, make_file, ensure_ascii=False, indent='\t')
        
with open('final_dataset_goalkeepers.json', 'w', encoding='utf-8') as make_file:
    json.dump(normalized_keeper, make_file, ensure_ascii=False, indent='\t')