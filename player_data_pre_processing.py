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



required_players_id = read_jsonl_file('/Users/jooyong/github_locals/CSCI5525_project/team_ids_player_ids.json')
print(required_players_id[0])
 