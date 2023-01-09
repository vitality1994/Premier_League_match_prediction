import time

import requests

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

headers = {
    'authority': 'footballapi.pulselive.com',
    'accept': '*/*',
    'accept-language': 'en,ko-KR;q=0.9,ko;q=0.8,fr;q=0.7',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'dnt': '1',
    'if-none-match': 'W/"091d852ff11e156a2ceff8371e93f5f67"',
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

base_url = 'https://footballapi.pulselive.com/football/fixtures?comps=1&compSeasons={}&page={}&pageSize=40&sort=desc&statuses=C&altIds=true'
for season_no in season_no_to_season_year.keys():
    print(f'{season_no_to_season_year[season_no]}..')
    match_results = []
    season_url = base_url.format(season_no, 0)
    response = requests.get(season_url, headers=headers).json()
    # "pageInfo": {
    #     "page": 0,
    #     "numPages": 14,
    #     "pageSize": 40,
    #     "numEntries": 555
    # },
    # "content": [..]

    zero_page_info = response['pageInfo']
    zero_page_content = response['content']
    assert isinstance(zero_page_content, list)
    match_results.extend(zero_page_content)

    for page_no in range(1, zero_page_info['numPages']):
        next_page_url = base_url.format(season_no, page_no)
        page_response = requests.get(next_page_url, headers=headers).json()
        page_content = page_response['content']
        assert isinstance(page_content, list)
        match_results.extend(page_content)
        time.sleep(0.5)

    season_year = season_no_to_season_year[season_no]
    with open(f'./matchesm/season_{season_year}.json', 'w') as f:
        for match in match_results:
            f.write(f'{match}\n')
