import json
import warnings

import numpy as np
import pandas as pd

from category_encoders import OrdinalEncoder
from sklearn import metrics
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.svm import SVC
from scipy.stats import uniform
from sklearn.metrics import f1_score, accuracy_score

import matplotlib.pyplot as plt



warnings.filterwarnings(action='ignore')


def read_jsonl_file(path):
    json_lines = []
    with open(path, 'r') as f:
        for line in f:
            json_lines.append(json.loads(line.strip()))
    return json_lines



def do_exp_1(method):
    
    X = []
    y = []
    for match in matches:

        list_att_home = []
        list_att_away = []
        

        for i in match['home_players']:
            
            # assign hometeam goalkeeper's attributes first.
            if merged_data[str(i)]['is_goalkeeper']==1:
                key_home_keeper = i
                
                for k, j in merged_data[str(i)]['premier_stats'].items():
                    list_att_home.append(j)

        
        for i in match['home_players']:
            
            # assign hometeam field players' attributes.
            if i != key_home_keeper:
                
                for k, j in merged_data[str(i)]['premier_stats'].items():
                    list_att_home.append(j)


                    
                    
        for i in match['away_players']:
            
            # assign awayteam goalkeeper's attributes first.
            if merged_data[str(i)]['is_goalkeeper']==1:
                key_away_keeper = i
                
                for k, j in merged_data[str(i)]['premier_stats'].items():
                    list_att_away.append(j)

        
        for i in match['away_players']:
            
            # assign awayteam field players' attributes.
            if i != key_away_keeper:
                
                for k, j in merged_data[str(i)]['premier_stats'].items():
                    list_att_away.append(j)

         
        x = np.array(list_att_away + list_att_home)    
        X.append(x)
        y.append(int(match['match_result']))

        
    X = np.asarray(X)
    y = np.asarray(y)

    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
   

    ######################### Block for SVM ############################################
    if method == 'svm':

        dists = {'C': [0.1, 1, 10, 100, 1000], 
                'gamma': [1, 0.1, 0.01, 0.001, 0.0001],
                'kernel': ['rbf']} 

        clf = SVC(random_state = 42, class_weight = 'balanced')
    ####################################################################################
    
    
    
    ######################### Block for Random Forest ##################################
    if method == 'randomforest':

        dists = { 'n_estimators' : [10, 100],
                'max_depth' : [6, 8, 10, 12],
                'min_samples_leaf' : [8, 12, 18],
                'min_samples_split' : [8, 16, 20]
                    }
    
        clf = RandomForestClassifier(random_state=42, class_weight='balanced')

    ####################################################################################

    clf1 = RandomizedSearchCV(
        clf,
        param_distributions=dists,
        n_iter = 500,
        cv = 5, 
        scoring = 'accuracy',
        verbose = 1,
        random_state = 42
    )
    
    clf1.fit(X_train, y_train)
    

    print('Best Hyperparameters: ', clf1.best_params_)
    y_test_pred = clf1.predict(X_test)
 

    pd.set_option('display.float_format',  '{:.2f}'.format)
    results = pd.DataFrame(metrics.classification_report(y_test, y_test_pred, output_dict=True)).to_latex()
    print(results)



def do_exp_2(method):
    
    X = []
    y = []
    for match in matches:

        list_att_home = []
        list_att_away = []
        

        for i in match['home_players']:
            
            # assign hometeam goalkeeper's attributes first.
            if merged_data[str(i)]['is_goalkeeper']==1:
                key_home_keeper = i
                
                for k, j in merged_data[str(i)]['fm_stats'].items():
                    list_att_home.append(j)

        
        for i in match['home_players']:
            
            # assign hometeam field players' attributes.
            if i != key_home_keeper:
                
                for k, j in merged_data[str(i)]['fm_stats'].items():
                    list_att_home.append(j)


                    
                    
        for i in match['away_players']:
            
            # assign awayteam goalkeeper's attributes first.
            if merged_data[str(i)]['is_goalkeeper']==1:
                key_away_keeper = i
                
                for k, j in merged_data[str(i)]['fm_stats'].items():
                    list_att_away.append(j)

        
        for i in match['away_players']:
            
            # assign awayteam field players' attributes.
            if i != key_away_keeper:
                
                for k, j in merged_data[str(i)]['fm_stats'].items():
                    list_att_away.append(j)


                    
        x = np.array(list_att_away + list_att_home)    
        X.append(x)
        y.append(int(match['match_result']))

        

    X = np.asarray(X)
    y = np.asarray(y)

    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    


    ######################### Block for SVM ############################################
    if method == 'svm':

        dists = {'C': [0.1, 1, 10, 100, 1000], 
                'gamma': [1, 0.1, 0.01, 0.001, 0.0001],
                'kernel': ['rbf']} 

        clf = SVC(random_state = 42, class_weight = 'balanced')
    ####################################################################################
    
    
    
    ######################### Block for Random Forest ##################################
    if method == 'randomforest':

        dists = { 'n_estimators' : [10, 100],
                'max_depth' : [6, 8, 10, 12],
                'min_samples_leaf' : [8, 12, 18],
                'min_samples_split' : [8, 16, 20]
                    }
    
        clf = RandomForestClassifier(random_state=42, class_weight='balanced')

    ####################################################################################

    clf1 = RandomizedSearchCV(
        clf,
        param_distributions=dists,
        n_iter = 500,
        cv = 5, 
        scoring = 'accuracy',
        verbose = 1,
        random_state = 42
    )
    
    clf1.fit(X_train, y_train)
    

    print('Best Hyperparameters: ', clf1.best_params_)
    y_test_pred = clf1.predict(X_test)
 

    pd.set_option('display.float_format',  '{:.2f}'.format)
    results = pd.DataFrame(metrics.classification_report(y_test, y_test_pred, output_dict=True)).to_latex()
    print(results)


    
    
    

def do_exp_3(method):
    

    
    X = []
    y = []
    for match in matches:

        list_att_home = []
        list_att_away = []

        for i in match['home_players']:
            
            # assign hometeam goalkeeper's attributes first.
            if merged_data[str(i)]['is_goalkeeper']==1:
                key_home_keeper = i
                
                for k, j in merged_data[str(i)]['premier_stats'].items():
                    list_att_home.append(j)

                for k, j in merged_data[str(i)]['fm_stats'].items():
                    list_att_home.append(j)
        
        for i in match['home_players']:
            
            # assign hometeam field players' attributes.
            if i != key_home_keeper:
                
                for k, j in merged_data[str(i)]['premier_stats'].items():
                    list_att_home.append(j)

                for k, j in merged_data[str(i)]['fm_stats'].items():
                    list_att_home.append(j)

                    
                    
        for i in match['away_players']:
            
            # assign awayteam goalkeeper's attributes first.
            if merged_data[str(i)]['is_goalkeeper']==1:
                key_away_keeper = i
                
                for k, j in merged_data[str(i)]['premier_stats'].items():
                    list_att_away.append(j)

                for k, j in merged_data[str(i)]['fm_stats'].items():
                    list_att_away.append(j)
        
        for i in match['away_players']:
            
            # assign awayteam field players' attributes.
            if i != key_away_keeper:
                
                for k, j in merged_data[str(i)]['premier_stats'].items():
                    list_att_away.append(j)

                for k, j in merged_data[str(i)]['fm_stats'].items():
                    list_att_away.append(j)

        
        
        x = np.array(list_att_away + list_att_home)    
        X.append(x)
        y.append(int(match['match_result']))

        

    X = np.asarray(X)
    y = np.asarray(y)

    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    

    
    
    ######################### Block for SVM ############################################
    if method == 'svm':

        dists = {'C': [0.1, 1, 10, 100, 1000], 
                'gamma': [1, 0.1, 0.01, 0.001, 0.0001],
                'kernel': ['rbf']} 

        clf = SVC(random_state = 42, class_weight = 'balanced')
    ####################################################################################
    
    
    
    ######################### Block for Random Forest ##################################
    if method == 'randomforest':

        dists = { 'n_estimators' : [10, 100],
                'max_depth' : [6, 8, 10, 12],
                'min_samples_leaf' : [8, 12, 18],
                'min_samples_split' : [8, 16, 20]
                    }
    
        clf = RandomForestClassifier(random_state=42, class_weight='balanced')

    ####################################################################################

    clf1 = RandomizedSearchCV(
        clf,
        param_distributions=dists,
        n_iter = 500,
        cv = 5, 
        scoring = 'accuracy',
        verbose = 1,
        random_state = 42
    )
    
    clf1.fit(X_train, y_train)
    

    print('Best Hyperparameters: ', clf1.best_params_)
    y_test_pred = clf1.predict(X_test)
 

    pd.set_option('display.float_format',  '{:.2f}'.format)
    results = pd.DataFrame(metrics.classification_report(y_test, y_test_pred, output_dict=True)).to_latex()
    print(results)




matches = read_jsonl_file('/Users/jooyong/github_locals/Premier_League_match_prediction/premier_official_data/team_ids_player_ids.jsonl')

with open('/Users/jooyong/github_locals/Premier_League_match_prediction/datasets/final_dataset_field_players.json') as f:
    final_dataset_field = json.load(f)

with open('/Users/jooyong/github_locals/Premier_League_match_prediction/datasets/final_dataset_goalkeepers.json') as f:
    final_dataset_goalkeer = json.load(f)


merged_data = {}
for key, value in final_dataset_field.items():
    merged_data[key] = value
for key, value in final_dataset_goalkeer.items():
    merged_data[key] = value

print('SVM with only official_stats')
do_exp_1('svm')
print('SVM with only fm_atts')
do_exp_2('svm')
print('SVM with official_stats + fm_atts')
do_exp_3('svm')
print('RandomForest with only official_stats')
do_exp_1('randomforest')
print('RandomForest with only fm_atts')
do_exp_2('randomforest')
print('RandomForest with official_stats + fm_atts')
do_exp_3('randomforest')