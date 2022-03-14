import random
from random import randrange
import networkx as nx
import argparse
from pathlib import Path
import json

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

    return t, dc

def create_population(node_id, name_app, name_module, app_jumlah, name_message, lamb, no):
    JSONfile2={"sources" : []}
    popul=[]

    for idx,node in enumerate(node_id):
        in_rg=randrange(app_jumlah)
        string2={
            "id_resource": random.choice(node_id),
            "app": str(name_app[in_rg]),
            "message": str(name_message[in_rg]),
            "lambda": random.choice(lamb)
        }
        popul.append(string2)

    JSONfile2["sources"] += popul

    json_object2 = json.dumps(JSONfile2, indent = 2)

    with open("JSON/Experiment_population/"+str(app_jumlah+1)+"_aplikasi_topology"+str(no)+".json", "w") as outfile:
        outfile.write(json_object2)
    return True

def create_applications_from_json(data):
    applications = {}
    name_app = []
    name_module = []
    name_message = []
    for app in data:
        a = Application(name=app["name"])
        modules = [{"None":{"Type":Application.TYPE_SOURCE}}]
        for module in app["module"]:
            modules.append({module["name"]: {"RAM": module["RAM"], "Type": Application.TYPE_MODULE}})
        name_module.append(module["name"])
        name_app.append(app["name"])
        a.set_modules(modules)

        ms = {}
        for message in app["message"]:
            name_message.append(message["name"])
            ms[message["name"]] = Message(message["name"],message["s"],message["d"],instructions=message["instructions"],bytes=message["bytes"])
            if message["s"] == "None":
                a.add_source_messages(ms[message["name"]])

        for idx, message in enumerate(app["transmission"]):
            if "message_out" in message.keys():
                a.add_service_module(message["module"],ms[message["message_in"]], ms[message["message_out"]], fractional_selectivity, threshold=1.0)
            else:
                a.add_service_module(message["module"], ms[message["message_in"]])

        applications[app["name"]]=a

    return applications, name_app, name_module, name_message


no = 10
jumlah_aplikasi = 30

# Panggil fungsi create aplikasi dari json
dataApp = json.load(open('JSON/Experiment_aplikasi/'+str(jumlah_aplikasi)+'_aplikasi.json'))
apps, name_app, name_module, name_message = create_applications_from_json(dataApp)

# Jumlah aplikasi -1
app_jumlah = jumlah_aplikasi - 1

jumlah_node = 100
t, dc = create_json_topology(jumlah_node)

# Cari centrality besar atau kecil
data_frame = pd.DataFrame.from_dict({'node': list(dc.keys()),'centrality': list(dc.values())})
new_value = data_frame.sort_values('centrality', ascending=False)
node_list = new_value['node'].tolist()
jumlah = jumlah_node-5
node_id = node_list[-jumlah:]

folder_results = Path("JSON/Experiment_topology/")
folder_results.mkdir(parents=True, exist_ok=True)
folder_results = str(folder_results)+"/"

# Cari mana node mempunyai centrality paling tinggi untuk dijadikan source
centrality = nx.betweenness_centrality(t.G)
nx.set_node_attributes(t.G, name="centrality", values=centrality)
nx.write_gexf(t.G, folder_results+str(jumlah_aplikasi)+"_aplikasi_topology"+str(no)+".graphml")

#print(new_value)
new_value.to_csv(folder_results+str(jumlah_aplikasi)+'_aplikasi_topology'+str(no)+'.csv', index=False)

# Create JSON placement pakai fungsi create_placement
lamb = [155]
create_pl = create_population(node_id, name_app, name_module, app_jumlah, name_message, lamb, no)