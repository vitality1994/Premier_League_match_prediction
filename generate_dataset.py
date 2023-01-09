import ast
import pandas as pd
import json
import os
from collections import Counter
from glob import glob
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from sklearn import metrics, preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC


def read_lines(file_path: str) -> List[str]:
    lines = []
    with open(file_path, 'r') as inf:
        for line in inf:
            lines.append(line.rstrip('\n'))
    return lines


def create_features_for_single_sample(match):
    match = ast.literal_eval(match)
    home_id = match['teamLists'][0]['teamId']
    away_id = match['teamLists'][1]['teamId']
    assert match['teams'][0]['team']['id'] == home_id
    assert match['teams'][1]['team']['id'] == away_id
    home_score = int(match['teams'][0]['score'])
    away_score = int(match['teams'][1]['score'])
    if home_score > away_score:
        match_result = 2
    elif home_score == away_score:
        match_result = 1
    else:
        match_result = 0
    home_players = []
    away_players = []
    for player in match['teamLists'][0]['lineup']:
        player_id = player['id']
        home_players.append(player_id)
    for player in match['teamLists'][1]['lineup']:
        player_id = player['id']
        away_players.append(player_id)
    if len(home_players) != 11 or len(away_players) != 11:
        print(home_players)
        print(away_players)
        return None
    return {'home_id': home_id, 'away_id': away_id, 'match_result': match_result, 'home_players': home_players, 'away_players': away_players}


def generate_dataset(season_samples, season_keys):
    if season_keys == 'all':
        season_keys = list(season_samples.keys())
    elif isinstance(season_keys, list):
        assert all(k in season_samples.keys() for k in season_keys)
    elif isinstance(season_keys, str):
        assert season_keys in season_samples.keys()
        season_keys = list(season_keys)
    D = []
    all_players = set()
    for key in season_keys:
        for sample in season_samples[key]:
            # x = [sample['home_id'], sample['away_id'], *sample['home_players'], *sample['away_players'], sample['match_result']]
            x = [*sample['home_players'], *sample['away_players'], sample['match_result']]
            # print(x)
            # input('next')
            # x = [sample['home_id'], sample['away_id'], sample['match_result']]
            all_players.update(sample['home_players'])
            all_players.update(sample['away_players'])
            D.append(x)
    print(all_players)
    print(len(all_players))
    # cats = [
    #     list(all_clubs.keys()),
    #     list(all_clubs.keys()),
    #     11 * list(players.keys()),
    #     11 * list(players.keys()),
    #     ['win', 'draw', 'lose']
    # ]
    # one_hot_enc = preprocessing.OneHotEncoder(categories=cats)
    one_hot_enc = preprocessing.OneHotEncoder().fit(D)
    print('cat len', len(one_hot_enc.categories_))
    # print(D)
    D_emb = one_hot_enc.transform(D).toarray()
    X = D_emb[:, :-3]
    y = D_emb[:, -3:]

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    print(x_train.shape, y_train.shape)
    print(x_test.shape, y_test.shape)

    return X_train, X_test, y_train, y_test


if __name__ == '__main__':
    # one-hot encode clubs
    with open('/Users/jooyong/github_locals/CSCI5525_project/premier_official_data/club_match_official/all_clubs.json', 'r') as f:
        all_clubs = json.load(f)

    with open('/Users/jooyong/github_locals/CSCI5525_project/premier_official_data/player_official_stats/all_players_keys.json', 'r') as f:
        players = json.load(f)

    print(len(all_clubs), len(players))

    season_matches = glob(os.path.join('/Users/jooyong/github_locals/CSCI5525_project/premier_official_data/club_match_official/matches', '/Users/jooyong/github_locals/CSCI5525_project/premier_official_data/club_match_official/matches', 'season_*.details.json'))
    season_samples = {}
    print(season_matches)
    all_samples = []
    for season_match in season_matches:
        # if '2012-13' in season_match:
        #     continue
        matches = read_lines(season_match)
        season_name = os.path.basename(season_match)
        season_name = season_name.replace('season_', '').replace('.details.json', '')
        print(season_name)
        season_samples[season_name] = []
        for match in matches:
            sample = create_features_for_single_sample(match)
            if sample is not None:
                season_samples[season_name].append(sample)
                sample['season'] = season_name
                all_samples.append(sample)
        print(len(season_samples[season_name]))
        print(len(all_samples))

    with open(f'./team_ids_player_ids.jsonl', 'w') as f:
        for sample in all_samples:
            f.write(f'{json.dumps(sample)}\n')

    # X_train, X_test, y_train, y_test = generate_dataset(season_samples, season_keys='all')
    # # X_train, X_test, y_train, y_test = generate_dataset(season_samples, ['2021-22', '2020-21', '2019-20', '2018-19'])

    # y_train = np.argwhere(y_train == 1)[:, 1]
    # y_test = np.argwhere(y_test == 1)[:, 1]
    # clf = RandomForestClassifier(max_depth=None, random_state=42)
    # # clf = SVC()
    # clf.fit(X_train, y_train)
    # y_preds = clf.predict(X_test)

    # pd.set_option('display.float_format',  '{:.2f}'.format)
    # results = pd.DataFrame(metrics.classification_report(y_test, y_preds, output_dict=True)).to_latex()
    # print(results)


    # # y_train_counter = Counter(y_train)
    # # y_test_counter = Counter(y_test)
    # # y_train_dist = {k: float(v) / len(y_train) for k, v in y_train_counter.items()}
    # # y_test_dist = {k: float(v) / len(y_test) for k, v in y_test_counter.items()}
    # # print(y_train_dist)
    # # print(y_test_dist)