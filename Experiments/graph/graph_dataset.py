import json
import os
import random

random.seed(42)
from typing import Dict, List, Tuple

import dgl
import torch
from dgl.data import DGLDataset


def read_jsonl_file(path):
    json_lines = []
    with open(path, 'r') as f:
        for line in f:
            json_lines.append(json.loads(line.strip()))
    return json_lines


def read_lines(file_path: str) -> List[str]:
    lines = []
    with open(file_path, 'r') as inf:
        for line in inf:
            lines.append(line.rstrip('\n'))
    return lines


def save_train_test_splits_by_season(dataset_path: str, filename: str = "team_ids_player_ids.json"):
    matches = read_jsonl_file(os.path.join("/Users/zaemyung/Development/aml_5525/dataset/processed", filename))
    club_ids = [23, 4, 3, 40, 1, 7, 25, 27, 12, 31, 21, 33, 11, 39, 13, 2, 34, 37, 18, 10, 29, 26, 5, 19, 22, 28, 15, 9, 20, 42, 127, 45, 36, 6, 14, 17, 8, 35, 16, 24, 38, 43, 131, 32, 159, 46, 41, 130, 44, 30]
    season_match = {'2012-13':[],'2013-14':[],'2014-15':[],'2015-16':[],'2016-17':[],'2017-18':[],'2018-19':[],'2019-20':[],'2020-21':[],'2021-22':[]}
    season_no = ['2012-13','2013-14','2014-15','2015-16','2016-17','2017-18','2018-19','2019-20','2020-21','2021-22']

    combined_test_set = {}
    combined_training_set = {}

    for i in range(len(matches)):
        one_match = matches[i]
        season = one_match['season']
        season_match[season].append(one_match)

    for j in season_no:
        test_set = []
        training_set = []
        combined = season_match[j]
        random.shuffle(combined)
        for i in range(len(club_ids)):
            club_id = club_ids[i]
            matched = 1
            for match in combined:
                home_id = match['home_id']
                if club_id == home_id and matched < 5:
                    test_set.append(match)
                    matched = matched + 1
                elif club_id == home_id and matched > 4:
                    training_set.append(match)
        print(j,'season','length of test set is',len(test_set))
        print(j,'season','length of training set is',len(training_set))
        combined_test_set[j] = test_set
        combined_training_set[j] = training_set

    with open(os.path.join("/Users/zaemyung/Development/aml_5525/dataset/processed", "team_ids_player_ids_train_test_split.json"), "w") as f:
        for _, matches in combined_training_set.items():
            for match in matches:
                match["is_testset"] = 0
                f.write(f"{json.dumps(match)}\n")
        for _, matches in combined_test_set.items():
            for match in matches:
                match["is_testset"] = 1
                f.write(f"{json.dumps(match)}\n")


class FootballDataset(DGLDataset):
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        super().__init__(name="football")

    def read_matches_by_season(self, filename: str = "team_ids_player_ids_train_test_split.json") -> Dict[str, List[Dict]]:
        """
        Returns in a format:
            {"season_year": ["home_id": 4, "away_id": 6, "match_result": 0, "home_players": [..], "away_players": [..]], ..}
        """
        file_path = os.path.join(self.dataset_path, filename)
        matches = read_lines(file_path)
        matches_by_season = {}
        for match in matches:
            match = json.loads(match)
            season_year = match["season"]

            if season_year not in matches_by_season:
                matches_by_season[season_year] = []

            del match["season"]
            matches_by_season[season_year].append(match)
        return matches_by_season

    def extract_entity_ids_from_matches(self) -> Tuple[List[int], List[int], List[int]]:
        def _get_keeper_and_kicker_ids(player_entity_ids: List[int]) -> Tuple[int, List[int]]:
            goalkeeper_entity_id = None
            for player_entity_id in player_entity_ids:
                if self.player_attributes[player_entity_id]["is_goalkeeper"]:
                    goalkeeper_entity_id = player_entity_id
                    break
            assert goalkeeper_entity_id is not None
            player_entity_ids.remove(goalkeeper_entity_id)
            return goalkeeper_entity_id, player_entity_ids

        team_ids, keeper_ids, kicker_ids = set(), set(), set()
        for season_year, matches in self.matches_by_season.items():
            for i, match in enumerate(matches):
                home_keeper_id, home_kicker_ids = _get_keeper_and_kicker_ids(match["home_players"])
                away_keeper_id, away_kicker_ids = _get_keeper_and_kicker_ids(match["away_players"])
                assert len(home_kicker_ids) == len(away_kicker_ids) == 10
                # add keeper and kicker ids to matches
                self.matches_by_season[season_year][i]["home_keeper_id"] = home_keeper_id
                self.matches_by_season[season_year][i]["away_keeper_id"] = away_keeper_id
                self.matches_by_season[season_year][i]["home_kicker_ids"] = home_kicker_ids
                self.matches_by_season[season_year][i]["away_kicker_ids"] = away_kicker_ids
                # aggregate all ids by type
                team_ids.update([match["home_id"], match["away_id"]])
                keeper_ids.update([home_keeper_id, away_keeper_id])
                kicker_ids.update(home_kicker_ids + away_kicker_ids)
        return sorted(list(team_ids)), sorted(list(keeper_ids)), sorted(list(kicker_ids))

    def read_player_attributes(self, filename: str = "final_players(normalized_official).json"):
        file_path = os.path.join(self.dataset_path, filename)
        with open(file_path, "r") as f:
            player_attributes = json.load(f)

        _player_attributes = {}
        for player_id, attributes in player_attributes.items():
            player_id = int(player_id)
            if attributes["is_goalkeeper"]:
                del attributes["fm_stats"]["Flair"]
                del attributes["fm_stats"]["Bravery"]
            _player_attributes[player_id] = attributes
        return _player_attributes

    def _create_single_graph(self, matches):

        graph_data = {
            ("keeper", "playFor", "team"): ([], []),
            ("kicker", "playFor", "team"): ([], []),
            ("team", "use", "keeper"): ([], []),
            ("team", "use", "kicker"): ([], []),
            ("team", "win", "team"): ([], []),
            ("team", "lose", "team"): ([], []),
            ("team", "draw", "team"): ([], [])
        }

        team_ids = set()
        keeper_ids = set()
        kicker_ids = set()
        for match in matches:
            home_team_id, away_team_id = match["home_id"], match["away_id"]
            home_keeper_id, away_keeper_id = match["home_keeper_id"], match["away_keeper_id"]
            home_kicker_ids, away_kicker_ids = match["home_kicker_ids"], match["away_kicker_ids"]

            team_ids.update([home_team_id, away_team_id])
            keeper_ids.update([home_keeper_id, away_keeper_id])
            kicker_ids.update(home_kicker_ids + away_kicker_ids)

            # player -> team
            graph_data[("keeper", "playFor", "team")][0].extend([home_keeper_id, away_keeper_id])
            graph_data[("keeper", "playFor", "team")][1].extend([home_team_id, away_team_id])
            graph_data[("kicker", "playFor", "team")][0].extend(home_kicker_ids + away_kicker_ids)
            graph_data[("kicker", "playFor", "team")][1].extend([home_team_id] * len(home_kicker_ids) +
                                                                [away_team_id] * len(away_kicker_ids))
            # team -> player
            graph_data[("team", "use", "keeper")][0].extend([home_team_id, away_team_id])
            graph_data[("team", "use", "keeper")][1].extend([home_keeper_id, away_keeper_id])
            graph_data[("team", "use", "kicker")][0].extend([home_team_id] * len(home_kicker_ids) +
                                                            [away_team_id] * len(away_kicker_ids))
            graph_data[("team", "use", "kicker")][1].extend(home_kicker_ids + away_kicker_ids)

            if match["match_result"] == 2:
                graph_data[("team", "win", "team")][0].extend([home_team_id])
                graph_data[("team", "win", "team")][1].extend([away_team_id])
                graph_data[("team", "lose", "team")][0].extend([away_team_id])
                graph_data[("team", "lose", "team")][1].extend([home_team_id])
            elif match["match_result"] == 0:
                graph_data[("team", "win", "team")][0].extend([away_team_id])
                graph_data[("team", "win", "team")][1].extend([home_team_id])
                graph_data[("team", "lose", "team")][0].extend([home_team_id])
                graph_data[("team", "lose", "team")][1].extend([away_team_id])
            else:
                graph_data[("team", "draw", "team")][0].extend([home_team_id])
                graph_data[("team", "draw", "team")][1].extend([away_team_id])
                graph_data[("team", "draw", "team")][0].extend([away_team_id])
                graph_data[("team", "draw", "team")][1].extend([home_team_id])

        id_mappings = {
            "team_id_to_node_id": {entity_id: node_id for node_id, entity_id in enumerate(team_ids)},
            "node_id_to_team_id": {node_id: entity_id for node_id, entity_id in enumerate(team_ids)},
            "keeper_id_to_node_id": {entity_id: node_id for node_id, entity_id in enumerate(keeper_ids)},
            "node_id_to_keeper_id": {node_id: entity_id for node_id, entity_id in enumerate(keeper_ids)},
            "kicker_id_to_node_id": {entity_id: node_id for node_id, entity_id in enumerate(kicker_ids)},
            "node_id_to_kicker_id": {node_id: entity_id for node_id, entity_id in enumerate(kicker_ids)},
        }

        def _convert_entity_ids_to_node_ids(entity_type: str, entity_ids: List[int]) -> List[int]:
            if entity_type == "team":
                node_ids = [id_mappings["team_id_to_node_id"][_id] for _id in entity_ids]
            elif entity_type == "keeper":
                node_ids = [id_mappings["keeper_id_to_node_id"][_id] for _id in entity_ids]
            elif entity_type == "kicker":
                node_ids = [id_mappings["kicker_id_to_node_id"][_id] for _id in entity_ids]
            else:
                raise AttributeError(f"Unknown attribute: {entity_type}")
            return node_ids

        for (e1, v, e2), (e1_vals, e2_vals) in graph_data.items():
            e1_vals = _convert_entity_ids_to_node_ids(e1, e1_vals)
            e2_vals = _convert_entity_ids_to_node_ids(e2, e2_vals)
            graph_data[(e1, v, e2)] = (torch.tensor(e1_vals), torch.tensor(e2_vals))

        g = dgl.heterograph(graph_data)

        g.nodes["keeper"].data["premier"] = torch.zeros(g.num_nodes("keeper"), self.premier_attributes_size, dtype=torch.float)
        g.nodes["kicker"].data["premier"] = torch.zeros(g.num_nodes("kicker"), self.premier_attributes_size, dtype=torch.float)
        g.nodes["keeper"].data["fm"] = torch.zeros(g.num_nodes("keeper"), self.fm_attributes_size, dtype=torch.float)
        g.nodes["kicker"].data["fm"] = torch.zeros(g.num_nodes("kicker"), self.fm_attributes_size, dtype=torch.float)

        # g.nodes["team"].data["feature"] = torch.randn(g.num_nodes("team"), self.premier_attributes_size)
        # g.nodes["team"].data["feature"] = torch.randn(g.num_nodes("team"), self.fm_attributes_size)
        g.nodes["team"].data["feature"] = torch.randn(g.num_nodes("team"), self.premier_attributes_size + self.fm_attributes_size)

        # fill feature vectors with attributes
        for keeper_node_id in range(g.num_nodes("keeper")):
            keeper_id = id_mappings["node_id_to_keeper_id"][keeper_node_id]
            g.nodes["keeper"].data["premier"][keeper_node_id] = torch.tensor(list(self.player_attributes[keeper_id]["premier_stats"].values()), dtype=torch.float)
            g.nodes["keeper"].data["fm"][keeper_node_id] = torch.tensor(list(self.player_attributes[keeper_id]["fm_stats"].values()), dtype=torch.float)
        for kicker_node_id in range(g.num_nodes("kicker")):
            kicker_id = id_mappings["node_id_to_kicker_id"][kicker_node_id]
            g.nodes["kicker"].data["premier"][kicker_node_id] = torch.tensor(list(self.player_attributes[kicker_id]["premier_stats"].values()), dtype=torch.float)
            g.nodes["kicker"].data["fm"][kicker_node_id] = torch.tensor(list(self.player_attributes[kicker_id]["fm_stats"].values()), dtype=torch.float)

        g.edata[("team", "win", "team")]["train_mask"] = torch.zeros(g.num_edges(("team", "win", "team")), dtype=torch.bool).bernoulli(0.6)
        g.edata[("team", "lose", "team")]["train_mask"] = torch.zeros(g.num_edges(("team", "lose", "team")), dtype=torch.bool).bernoulli(0.6)
        g.edata[("team", "draw", "team")]["train_mask"] = torch.zeros(g.num_edges(("team", "draw", "team")), dtype=torch.bool).bernoulli(0.6)
        return g

    def create_graphs_by_season(self):
        graphs_by_season = {}
        for season_year, matches in self.matches_by_season.items():
            graphs_by_season[season_year] = self._create_single_graph(matches)
        return graphs_by_season

    def process(self):
        self.matches_by_season = self.read_matches_by_season()
        self.player_attributes = self.read_player_attributes()
        self.team_ids, self.keeper_ids, self.kicker_ids = self.extract_entity_ids_from_matches()
        # check that we have player_attributes for all players
        assert len(self.player_attributes) == len(self.keeper_ids) + len(self.kicker_ids)
        keeper_premier_attributes_size = len(self.player_attributes[3169]["premier_stats"])
        keeper_fm_attributes_size = len(self.player_attributes[3169]["fm_stats"])
        kicker_premier_attributes_size = len(self.player_attributes[3116]["premier_stats"])
        kicker_fm_attributes_size = len(self.player_attributes[3116]["fm_stats"])

        assert keeper_premier_attributes_size == kicker_premier_attributes_size
        assert keeper_fm_attributes_size == kicker_fm_attributes_size

        self.premier_attributes_size = keeper_premier_attributes_size
        self.fm_attributes_size = keeper_fm_attributes_size

        self.graphs_by_season = self.create_graphs_by_season()
        self.graphs = list(self.graphs_by_season.values())

    def __getitem__(self, i):
        return self.graphs[i]

    def __len__(self):
        return len(self.graphs)


if __name__ == "__main__":
    # save_train_test_splits_by_season(dataset_path="/Users/zaemyung/Development/aml_5525/dataset/processed")
    dataset = FootballDataset(dataset_path="/Users/zaemyung/Development/aml_5525/dataset/processed")
    # print(len(dataset))
    graph = dataset[0]
    print(graph)