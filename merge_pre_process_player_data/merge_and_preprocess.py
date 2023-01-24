# import necessary packages
import re
import json
import numpy as np
from difflib import SequenceMatcher
import ast

# function for pre processing
def fm_player_pre_processing(data):   
        
    fm_inside_total = {}

    for j in range(len(data)):

        fm_inside = {}    
        dict_test_att = {}

        # pre process attributes
        for i in range(len(data[j]['attribute'])):
            dict_test_att[data[j]['attribute'][i]]=float(data[j]['level'][i])/20

        dict_test_player_other_info = {}

        # pre process player information
        for i in range(len(data[j]['player_other_info_keys'])):
            dict_test_player_other_info[data[j]['player_other_info_keys'][i]] \
            =data[j]['player_other_info_values'][i]


        dict_test_main_role_suit = {}

        # pre process player main roles level
        for i in range(len(data[j]['player_main_roles_keys(suitable)'])):
            dict_test_main_role_suit[data[j]['player_main_roles_keys(suitable)'][i]] \
            =round(float(data[j]['player_main_roles_values(suitable)'][i])/100, 3)


        fm_inside['attributes']=dict_test_att

        for key, value in dict_test_player_other_info.items():

            if key == 'Length' or key == 'Weight' or key == 'Sell value' or key == 'Wages':
                value = value.replace(',','')
                fm_inside[key] = float(re.findall(r'\d+', value)[0])


            else:
                fm_inside[key] = value

        fm_inside['main roles']=dict_test_main_role_suit
        fm_inside['ability']=float(data[j]['ability'])/100

        if data[j]['potential']!=None:
            fm_inside['potential']=float(data[j]['potential'])/100

        else:
            fm_inside['potential']=data[j]['potential'] # which is none

        fm_inside['club_team']=data[j]['club_team']
        fm_inside['nationality']=data[j]['nationality']
        fm_inside['age']=float(data[j]['age'])
        fm_inside['positions']=data[j]['positions']
        fm_inside.pop('Caps / Goals')
        fm_inside.pop('Unique ID')

        fm_inside_total[data[j]['name']]=fm_inside
    

    Length_list = []

    for k in fm_inside_total:
        Length_list.append(fm_inside_total[k]['Length'])


    Length_max = np.max(Length_list)
    Length_min = np.min(Length_list)

    Weight_list = []

    for k in fm_inside_total:
        Weight_list.append(fm_inside_total[k]['Weight'])

    Weight_max = np.max(Weight_list)
    Weight_min = np.min(Weight_list)


    Sell_value_list = []

    for k in fm_inside_total:
        if 'Sell value' in fm_inside_total[k].keys():
            Sell_value_list.append(fm_inside_total[k]['Sell value'])
        else:
            fm_inside_total[k]['Sell value'] = 0

    Sell_value_max = np.max(Sell_value_list)
    Sell_value_min = np.min(Sell_value_list)

    Wages_list = []

    for k in fm_inside_total:
        if 'Wages' in fm_inside_total[k].keys():
            Wages_list.append(fm_inside_total[k]['Wages'])
        else:
            fm_inside_total[k]['Wages'] = 0
    Wages_max = np.max(Wages_list)
    Wages_min = np.min(Wages_list)    

    
    for k in fm_inside_total:
        
        fm_inside_total[k]['Length'] = round((fm_inside_total[k]['Length']-Length_min) / (Length_max-Length_min), 3)
        fm_inside_total[k]['Weight'] = round((fm_inside_total[k]['Weight']-Weight_min) / (Weight_max-Weight_min), 3)
        
        if fm_inside_total[k]['Sell value']!=0:
            fm_inside_total[k]['Sell value'] = round((fm_inside_total[k]['Sell value']-Sell_value_min) / (Sell_value_max-Sell_value_min), 3)
    
        if fm_inside_total[k]['Wages']!=0:
            fm_inside_total[k]['Wages'] = round((fm_inside_total[k]['Wages']-Wages_min) / (Wages_max-Wages_min), 3)



    team_list = ['Arsenal', 'Manchester City', 'Newcastle', 'Tottenham Hotspur', 'Manchester United', \
            'Brighton', 'Chelsea', 'Liverpool', 'Fulham', 'Crystal Palace', 'Brentford', 'Leeds Utd', \
            'Aston Villa', 'Leicester City', 'West Ham', 'Everton', 'Bournemouth', 'Southampton', \
            'Wolves', 'Nottingham Forest']

    fm_player_premier = {}

    for key, value in fm_inside_total.items():
        
        if value['club_team'] in team_list:
            
            fm_player_premier[key] = value

    official_data = {}
    with open('/Users/jooyong/github_locals/CSCI5525_project/premier_official_data/player_official_stats/all_players_official_stats.json') as f:
        for line in f:
            temp = ast.literal_eval(line.strip().replace("false", "False").replace("true", "True"))
            for key, value in temp.items():
                official_data[key] = value


    official_names_dict = {}
    for i in range(len(list(official_data))):
        official_names_dict[official_data[list(official_data)[i]]['all_season']['entity']['name']['display']]= \
                            list(official_data.keys())[i]

    official_names = []
    for i in range(len(list(official_data))):
        official_names.append(official_data[list(official_data)[i]]['all_season']['entity']['name']['display'])


    fm_player_premier_names = list(fm_player_premier.keys())
    fm_player_premier_names_for_remove = fm_player_premier_names[:]

    merged_data_list = []
    count = 0

    for i in fm_player_premier_names:
        
        distance_word = []
        
        for k in official_names:
            
            ratio = SequenceMatcher(None, ''.join(sorted(k.lower())), ''.join(sorted(i.lower()))).ratio()
            distance_word.append(ratio)
        
        
        merged_data = sorted(distance_word, reverse=True)    
        min_distance = np.max(distance_word)
        
        top_similar_names = []
        
        for j in range(3):
            top_similar_names.append(official_names[distance_word.index(merged_data[j])])
        
        if count < 20:
            print('-------------------------------------------')
            print('player name in fm_data:', i)
            print()
            print('list of top three similar names:')
            print(top_similar_names[0], ",",\
                top_similar_names[1], ",",\
                top_similar_names[2])


        if min_distance >= 0.85:
            count+=1
            if count<=20:
                print()
                print('matched name:', official_names[distance_word.index(min_distance)])
                print('counting the number of matched names:', count)
            
            fm_player_premier_names_for_remove.remove(i)

            matched_id = official_names_dict[official_names[distance_word.index(min_distance)]]
            official_data[matched_id]['fm_data'] = fm_player_premier[i]

    print('\n\n')
    print("results above are only first 20 players matched")


    for k in official_data.keys():
        seasons = []
        for j in list(official_data[k].keys()):
            
            if j!='fm_data' and j!='all_season':
                
                seasons.append(j)
                del(official_data[k][j])


                dict_att = {}
                for i in official_data[k]['all_season']['stats']:
                    dict_att[list(i.values())[0]] = float(list(i.values())[1])
    
        official_data[k]['entity']=official_data[k]['all_season']['entity']
        

        official_data[k]['official_stats'] = dict_att
        del(official_data[k]['all_season']['stats'])

        del(official_data[k]['all_season'])

        official_data[k]['seasons']=seasons


    
    return official_data



with open('/Users/jooyong/github_locals/CSCI5525_project/fm_inside/fm_inside_scraper/fm_inside_scraper/spiders/fm_players.json') as f:
    fm_raw_data = json.load(f) 

merged_data = fm_player_pre_processing(fm_raw_data)

count = 1
for i in merged_data.keys():
    if 'fm_data' in list(merged_data[i].keys()):
        count+=1

print("total number of matched players:", count)


with open('./merged_player_data.json', 'w', encoding='utf-8') as make_file:
    json.dump(merged_data, make_file, ensure_ascii=False, indent='\t')