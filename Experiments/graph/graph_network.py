import random

import dgl
import dgl.function as fn
import dgl.nn as dglnn
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from graph_dataset import FootballDataset

torch.manual_seed(42)
np.random.seed(42)
random.seed(42)


class RGCN(nn.Module):
    """a Heterograph Conv model"""
    def __init__(self, in_feats, hid_feats, out_feats, rel_names):
        super().__init__()

        self.conv1 = dglnn.HeteroGraphConv({
            rel: dglnn.GraphConv(in_feats, hid_feats)
            for rel in rel_names}, aggregate='sum')
        self.conv2 = dglnn.HeteroGraphConv({
            rel: dglnn.GraphConv(hid_feats, out_feats)
            for rel in rel_names}, aggregate='sum')

    def forward(self, graph, inputs):
        # inputs are features of nodes
        h = self.conv1(graph, inputs)
        h = {k: F.relu(v) for k, v in h.items()}
        h = self.conv2(graph, h)
        return h


class HeteroMLPPredictor(nn.Module):
    def __init__(self, in_dims, n_classes):
        super().__init__()
        self.W = nn.Linear(in_dims * 2, n_classes)

    def apply_edges(self, edges):
        x = torch.cat([edges.src["h"], edges.dst["h"]], 1)
        y = self.W(x)
        return {'score': y}

    def forward(self, graph, h):
        # h contains the node representations for each edge type computed from
        # the GNN for heterogeneous graphs defined in the node classification
        # section (Section 5.1).
        with graph.local_scope():
            graph.ndata["h"] = h["team"]   # assigns 'h' of all node types in one shot
            graph.apply_edges(func=self.apply_edges)
            return graph.edata["score"]


class Octopus(nn.Module):
    def __init__(self, in_features, hidden_features, out_features, rel_names):
        super().__init__()
        self.sage = RGCN(in_features, hidden_features, out_features, rel_names)
        self.pred = HeteroMLPPredictor(out_features, len(rel_names))
    def forward(self, g, x, dec_graph):
        h = self.sage(g, x)
        return self.pred(dec_graph, h)


if __name__ == "__main__":
    from sklearn.metrics import accuracy_score, f1_score

    # Premier: 22, FM: 42
    # 2: draw, 3: lose, 6: win
    dataset = FootballDataset(dataset_path="/Users/zaemyung/Development/aml_5525/dataset/processed")

    all_pred = []
    all_true = []
    for season_year, hetero_graph in dataset.graphs_by_season.items():
        print(season_year)

        dec_graph = hetero_graph["team", :, "team"]
        edge_label = dec_graph.edata[dgl.ETYPE]

        # model = Octopus(22, 16, 10, hetero_graph.etypes)
        model = Octopus(42 + 22, 100, 20, hetero_graph.etypes)

        team_feats = hetero_graph.nodes["team"].data["feature"]
        # TODO: FM and Premier + FM
        keeper_feats_pr = hetero_graph.nodes["keeper"].data["premier"]
        kicker_feats_pr = hetero_graph.nodes["kicker"].data["premier"]
        keeper_feats_fm = hetero_graph.nodes["keeper"].data["fm"]
        kicker_feats_fm = hetero_graph.nodes["kicker"].data["fm"]
        keeper_feats = torch.concat((keeper_feats_pr, keeper_feats_fm), dim=1)
        kicker_feats = torch.concat((kicker_feats_pr, kicker_feats_fm), dim=1)
        node_features = {"team": team_feats, "keeper": keeper_feats, "kicker": kicker_feats}

        opt = torch.optim.Adam(model.parameters())
        for epoch in range(40):
            logits = model(hetero_graph, node_features, dec_graph)
            loss = F.cross_entropy(logits, edge_label)
            opt.zero_grad()
            loss.backward()
            opt.step()
            # print(loss.item())

        pred = torch.max(logits, 1).indices
        true = edge_label

        all_pred.extend(pred)
        all_true.extend(edge_label)

        print(accuracy_score(y_true=true, y_pred=pred))
        print(f1_score(y_true=true, y_pred=pred, average="macro"))
    print(accuracy_score(y_true=all_true, y_pred=all_pred))
    print(f1_score(y_true=all_true, y_pred=all_pred, average="macro"))