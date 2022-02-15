import random
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

RANDOM_SEED = 1


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

def create_placement_population(node_id, name_app, name_module, app_jumlah, name_message, lamb):
    JSONfile={"initialAllocation" : []}
    JSONfile2={"sources" : []}
    allocation=[]
    popul=[]

    for idx,node in enumerate(node_id):
        in_rg=randrange(app_jumlah)
        string={
            "module_name": str(name_module[in_rg]),
            "app": str(name_app[in_rg]),
            "id_resource": random.choice(node_id)
        }

        string2={
            "id_resource": random.choice(node_id),
            "app": str(name_app[in_rg]),
            "message": str(name_message[in_rg]),
            "lambda": random.choice(lamb)
        }
        allocation.append(string)
        popul.append(string2)

    JSONfile["initialAllocation"] += allocation
    JSONfile2["sources"] += popul

    json_object = json.dumps(JSONfile, indent = 2)
    json_object2 = json.dumps(JSONfile2, indent = 2)

    with open("JSON/Placement_testing.json", "w") as outfile:
        outfile.write(json_object)

    with open("JSON/Population_testing.json", "w") as outfile:
        outfile.write(json_object2)
    return True

def create_json_topology(jumlah_node):

    t = Topology()
    t.G=nx.barabasi_albert_graph(jumlah_node, 3)

    ls = list(t.G.nodes)
    li = {x: int(x) for x in ls}
    nx.relabel_nodes(t.G, li, False)


    # Setting value IPT, RAM, Storage, BW, IPT
    valueIPT = [1000, 1500, 2000, 2500, 3000]
    valueRAM = [1, 2, 3, 4]
    valueStorage = [1, 2]

    valueBW = [1, 2]
    valuePR = [1, 2]

    # Random node mana yg pakek IPT berapa dll
    penentuanBW = {x :random.choice(valueBW) for x in t.G.edges()}
    penentuanPR = {x :random.choice(valuePR) for x in t.G.edges()}
    penentuanIPT = {x :random.choice(valueIPT) for x in t.G.nodes()}
    penentuanRAM = {x :random.choice(valueRAM) for x in t.G.nodes()}
    penentuanStorage = {x :random.choice(valueRAM) for x in t.G.nodes()}

    nx.set_node_attributes(t.G,values=penentuanIPT, name="IPT")
    nx.set_node_attributes(t.G,values=penentuanRAM, name="RAM")
    nx.set_node_attributes(t.G,values=penentuanStorage, name="Storage")
    nx.set_edge_attributes(t.G, name='BW', values=penentuanBW)
    nx.set_edge_attributes(t.G, name='PR', values=penentuanPR)


    dc = nx.degree_centrality(t.G)

    return t, dc

def main(simulated_time):

    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    folder_results = Path("results/")
    folder_results.mkdir(parents=True, exist_ok=True)
    folder_results = str(folder_results)+"/"


    # Panggil fungsi create topology
    jumlah_node = 100
    t, dc = create_json_topology(jumlah_node)

    # Cari centrality besar atau kecil
    data_frame = pd.DataFrame.from_dict({'node': list(dc.keys()),'centrality': list(dc.values())})
    data_frame = data_frame.sort_values('centrality', ascending=False)
    node_list = data_frame['node'].tolist()
    jumlah = jumlah_node-5
    node_id = node_list[-jumlah:]

    # Cari mana node mempunyai centrality paling tinggi untuk dijadikan source
    centrality = nx.betweenness_centrality(t.G)
    nx.set_node_attributes(t.G, name="centrality", values=centrality)
    nx.write_gexf(t.G,folder_results+"graph_topology_simulasi.graphml")

    # Panggil fungsi create aplikasi dari json
    dataApp = json.load(open('JSON/11 Aplikasi.json'))
    apps, name_app, name_module, name_message = create_applications_from_json(dataApp)

    # Jumlah aplikasi -1
    app_jumlah = 10

    # Create JSON placement pakai fungsi create_placement
    lamb = [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200]
    create_pl = create_placement_population(node_id, name_app, name_module, app_jumlah, name_message, lamb)

    # Algoritma placement pakek JSON
    placementJson = json.load(open('JSON/Placement_testing.json'))
    placement = JSONPlacement(name="Placement", json=placementJson)

    # Minimum selector path
    selectorPath = MinimunPath()

    # Population pakai JSON
    dataPopulation = json.load(open('JSON/Population_testing.json'))
    pop = JSONPopulation(name="Statical", json=dataPopulation)

    # setup simulasi
    stop_time = simulated_time
    s = Sim(t, default_results_path="results/Hasil_testing")

    # Deployment dari populasi untuk setiap aplikasi
    for aName in apps.keys():
        print("Deploying app: ",aName)
        pop_app = JSONPopulation(name="Statical_%s"%aName,json={})
        data = []
        for element in pop.data["sources"]:
            if element['app'] == aName:
                data.append(element)
        pop_app.data["sources"]=data

        s.deploy_app2(apps[aName], placement, pop_app, selectorPath)
    
    # Deploy simulation
    s.run(stop_time, test_initial_deploy=False, show_progress_monitor=True)  # TEST to TRUE


if __name__ == '__main__':
    import logging.config
    import os
    pathExperimento = Path("results/")

    logging.config.fileConfig(os.getcwd()+'/logging.ini')

    start_time = time.time()
    print("Running Partition")
    main(simulated_time=100000)

    print("Simulation Done")
