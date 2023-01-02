import requests
import json
from typing import List


def read_lines(file_path: str) -> List[str]:
    lines = []
    with open(file_path, 'r') as inf:
        for line in inf:
            lines.append(line.rstrip('\n'))
    return lines


season_no_to_season_year = {
    "418": "2021-22",
    "363": "2020-21",
    "274": "2019-20",
    "210": "2018-19",
    "79": "2017-18",
    "54": "2016-17",
    "42": "2015-16",
    "27": "2014-15",
    "22": "2013-14",
    "21": "2012-13",
    "20": "2011-12",
    "19": "2010-11",
    "18": "2009-10",
    "17": "2008-09",
    "16": "2007-08",
    "15": "2006-07",
    "14": "2005-06",
    "13": "2004-05",
    "12": "2003-04",
    "11": "2002-03",
    "10": "2001-02",
    "9": "2000-01",
    "8": "1999-00",
    "7": "1998-99",
    "6": "1997-98",
    "5": "1996-97",
    "4": "1995-96",
    "3": "1994-95",
    "2": "1993-94",
    "1": "1992-93",
}


def crawl_player(player_id):
    headers = {
        'authority': 'footballapi.pulselive.com',
        'accept': '*/*',
        'accept-language': 'en,ko-KR;q=0.9,ko;q=0.8,fr;q=0.7',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'dnt': '1',
        'origin': 'https://www.premierleague.com',
        'referer': 'https://www.premierleague.com/',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'sec-gpc': '1',
    }

    params = {
        'comps': '1',
        # 'compSeasons': '489',
    }

    response = requests.get(f'https://footballapi.pulselive.com/football/stats/player/{player_id}', params=params, headers=headers)

    if response.status_code == 404:
        print(response.status_code)
        return None
    try:
        response = response.json()
    except requests.exceptions.JSONDecodeError:
        return None

    results = {'all_season': response}

    # For every season
    for season_id, season_name in season_no_to_season_year.items():
        params = {
            'comps': '1',
            'compSeasons': season_id,
        }

        response = requests.get(f'https://footballapi.pulselive.com/football/stats/player/{player_id}', params=params, headers=headers)

        if response.status_code == 404:
            continue
        try:
            response = response.json()
        except requests.exceptions.JSONDecodeError:
            continue

        if 'stats' not in response or len(response['stats']) < 1:
            continue

        results[season_id] = response

    return results


if __name__ == '__main__':
    with open('./all_players.json', 'r') as f:
            players = json.load(f)
            players = [int(player) for player in players.keys()]
    with open('./keys_no_in_merged_data.txt', 'r') as f:
            players_missing = f.readline().split(',')
            for player in players_missing:
                players.append(int(player.strip()))
            
            #print(players)

    player_ids = sorted(players)[2002:2050]

        
    
    with open(f'all_players_official_stats_3.json', 'w') as f:
        for i, player_id in enumerate(player_ids, start=1):
            print(f'{i}/{len(player_ids)}\t{player_id}')
            result = crawl_player(player_id)
            if result is not None:
                res = {player_id: result}
                f.write(f'{json.dumps(res)}\n')

    # for line in read_lines('all_players_official_stats_old.json'):
    #     players_stats = json.loads(line)
    #     for k, v in players_stats.items():
    #         players_stats[k] = v['all_season']
    #     print(len(players_stats.keys()))

    # for line in read_lines('all_players_official_stats_missing.json'):
    #     dict_sample = json.loads(line)
    #     print(len(dict_sample.keys()))
    #     assert len(dict_sample.keys()) == 1
    #     for k, v in dict_sample.items():
    #         players_stats[k] = v['all_season']

    # print(len(players_stats.keys()))

    # with open('all_players_official_stats.json', 'w') as f:
    #     json.dump(players_stats, f)

# player_ids = [_id for _id in player_ids if _id not in lines.keys()]
# print(len(player_ids))

# with open('leftover_player_ids.json', 'r') as f:
#     player_ids = json.load(f)
