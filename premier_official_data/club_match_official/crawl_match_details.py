import ast
import json
import os
import time
from glob import glob
from typing import Dict, List

import requests
from lxml import etree, html


def read_lines(file_path: str) -> List[str]:
    lines = []
    with open(file_path, 'r') as inf:
        for line in inf:
            lines.append(line.rstrip('\n'))
    return lines


def crawl_match_details(match_id: int) -> Dict:
    # ## OVERRIDE
    # match_id = 66712
    match_url = f'https://www.premierleague.com/match/{match_id}'
    print(match_url)
    page = requests.get(match_url)
    content = html.fromstring(page.content)

    details = content.xpath('//div[@class="mcTabsContainer"]')[0]
    details = details.get('data-fixture')
    details = json.loads(details)
    return details


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
}
for season_no, season_year in season_no_to_season_year.items():
    season = os.path.join('./matches', f'season_{season_year}.json')
    with open(f'{season[:-5]}.details.json', 'w') as f:
        print(season_year)
        season_name = os.path.basename(season)[7:-5]
        print(season_name)
        matches = read_lines(season)
        #matches = set(matches)
        for match in matches:
            match = ast.literal_eval(match)
            match['id'] = int(match['id'])
            details = crawl_match_details(match['id'])
            f.write(f'{details}\n')
