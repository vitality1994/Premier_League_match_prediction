import ast
import json
import os
import time
from glob import glob
from typing import Dict, List

import requests
from lxml import etree, html

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
    # "20": "2011-12",
    # "19": "2010-11",
    # "18": "2009-10",
    # "17": "2008-09",
    # "16": "2007-08",
    # "15": "2006-07",
    # "14": "2005-06",
    # "13": "2004-05",
    # "12": "2003-04",
    # "11": "2002-03",
    # "10": "2001-02",
    # "9": "2000-01",
    # "8": "1999-00",
    # "7": "1998-99",
    # "6": "1997-98",
    # "5": "1996-97",
    # "4": "1995-96",
    # "3": "1994-95",
    # "2": "1993-94",
    # "1": "1992-93",
}

def read_lines(file_path: str) -> List[str]:
    lines = []
    with open(file_path, 'r') as inf:
        for line in inf:
            lines.append(line.rstrip('\n'))
    return lines



def crawl_club_details(club_id: int) -> Dict:
    headers = {
        'authority': 'footballapi.pulselive.com',
        'accept': '*/*',
        'accept-language': 'en,ko-KR;q=0.9,ko;q=0.8,fr;q=0.7',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'dnt': '1',
        'if-none-match': 'W/"0624614605ee8d632ff3a8f391162a356"',
        'origin': 'https://www.premierleague.com',
        'referer': 'https://www.premierleague.com/',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    }

    params = {
        'comps': '1',
        # 'compSeasons':
    }

    # For all seasons combined
    club_details = requests.get(f'https://footballapi.pulselive.com/football/stats/team/{club_id}', params=params, headers=headers)

    if club_details.status_code == 404:
        print(club_details.status_code)
        return None
    try:
        club_details = club_details.json()
    except requests.exceptions.JSONDecodeError:
        return None

    results = {'all_season': club_details}

    # For every season
    for season_id, season_name in season_no_to_season_year.items():
        params = {
            'comps': '1',
            'compSeasons': season_id,
        }

        club_details = requests.get(f'https://footballapi.pulselive.com/football/stats/team/{club_id}', params=params, headers=headers)

        if club_details.status_code == 404:
            continue
        try:
            club_details = club_details.json()
        except requests.exceptions.JSONDecodeError:
            continue

        results[season_id] = club_details

    return results


# seasons = glob(os.path.join('./matches', 'season_*.json'))
# # get all ids for clubs
# club_ids = {}
# for season in seasons:
#     print(season)
#     matches = read_lines(season)
#     matches = set(matches)
#     for match in matches:
#         match = ast.literal_eval(match)
#         team_1_id = int(match['teams'][0]['team']['id'])
#         team_1_name = match['teams'][0]['team']['name']
#         team_2_id = int(match['teams'][1]['team']['id'])
#         team_2_name = match['teams'][1]['team']['name']
#         club_ids[team_1_id] = team_1_name
#         club_ids[team_2_id] = team_2_name

# print(club_ids)
# print(len(club_ids))

# with open('all_clubs.json', 'w') as f:
#     json.dump(club_ids, f, indent=2)

with open('all_clubs.json', 'r') as f:
    club_ids = json.load(f)
    print(club_ids)

with open('all_club_details.json', 'w') as f:
    for _id, name in club_ids.items():
        print(_id, name)
        details = crawl_club_details(_id)
        f.write(f'{details}\n')
        f.flush()