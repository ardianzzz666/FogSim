import random
from random import randrange
import networkx as nx
from networkx.readwrite import json_graph
import argparse
from pathlib import Path
#import json
import simplejson as json

import operator
import copy
import time
import numpy as np
import pandas as pd

from random import randrange

# Configurasi path sediri bois
import sys
sys.path.append('D:\\Michael\\FogSim\\')

from yafs.core import Sim
from yafs.application import Application,Message

from yafs.topology import Topology

from simpleSelection import MinimunPath
from yafs.placement import *
from yafs.stats import Stats
from yafs.distribution import exponential_distribution, exponentialDistribution
from JSONpop import JSONPopulation
from yafs.placement import JSONPlacement

from yafs.application import fractional_selectivity


def create_json_topology(jumlah_node):

    t = Topology()
    t.G=nx.barabasi_albert_graph(jumlah_node, 3)

    ls = list(t.G.nodes)
    li = {x: int(x) for x in ls}
    nx.relabel_nodes(t.G, li, False)


    # Setting value IPT, RAM, Storage, BW, IPT
    min_ram = 10
    max_ram = 25

    min_ipt = 20
    max_ipt = 60

    min_storage = 10
    max_storage = 25

    propagasi = 5
    bandwith = 75000

    # Random node mana yg pakek IPT berapa dll
    penentuanBW = {x :bandwith for x in t.G.edges()}
    penentuanPR = {x :propagasi for x in t.G.edges()}
    penentuanIPT = {x :randrange(min_ipt, max_ipt) for x in t.G.nodes()}
    penentuanRAM = {x :randrange(min_ram, max_ram) for x in t.G.nodes()}
    penentuanStorage = {x :randrange(min_storage, max_storage) for x in t.G.nodes()}

    nx.set_node_attributes(t.G,values=penentuanIPT, name="IPT")
    nx.set_node_attributes(t.G,values=penentuanRAM, name="RAM")
    nx.set_node_attributes(t.G,values=penentuanStorage, name="Storage")
    nx.set_edge_attributes(t.G, name='BW', values=penentuanBW)
    nx.set_edge_attributes(t.G, name='PR', values=penentuanPR)


    dc = nx.degree_centrality(t.G)
    #print json_graph.dumps(t)
    save_json(t.G,"Test_topo_save.json")
    return t, dc

def save_json(G, fname):
	json.dump(dict(nodes=[[n, G.node[n]] for n in G.nodes()],
		edges=[[u, v, G.edge[u][v]] for u,v in G.edges()]),
		open(fname, 'w'), indent=2)


jumlah_node = 100
t, dc = create_json_topology(jumlah_node)