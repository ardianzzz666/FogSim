import random
import networkx as nx
import argparse
from pathlib import Path
import json

import operator
import copy
import time
import numpy as np

from random import randrange

# Configurasi path sediri bois
import sys
sys.path.append('D:\\Michael\\FogSim\\')

from yafs.core import Sim
from yafs.application import Application,Message

#from yafs.population import *
from Evolutive_population import Evolutive,Statical
from yafs.topology import Topology

from simpleSelection import MinimunPath
#from simplePlacement import CloudPlacement
from yafs.placement import *
from yafs.stats import Stats
from yafs.distribution import exponential_distribution, exponentialDistribution
from DynamicPopulation import DynamicPopulation

from yafs.application import fractional_selectivity

RANDOM_SEED = 1


def create_applications_from_json(data):
    applications = {}
    for app in data:
        a = Application(name=app["name"])
        modules = [{"None":{"Type":Application.TYPE_SOURCE}}]
        for module in app["module"]:
            modules.append({module["name"]: {"RAM": module["RAM"], "Type": Application.TYPE_MODULE}})
        a.set_modules(modules)

        ms = {}
        for message in app["message"]:
            ms[message["name"]] = Message(message["name"],message["s"],message["d"],instructions=message["instructions"],bytes=message["bytes"])
            if message["s"] == "None":
                a.add_source_messages(ms[message["name"]])

        for idx, message in enumerate(app["transmission"]):
            if "message_out" in message.keys():
                a.add_service_module(message["module"],ms[message["message_in"]], ms[message["message_out"]], fractional_selectivity, threshold=1.0)
            else:
                a.add_service_module(message["module"], ms[message["message_in"]])

        applications[app["name"]]=a

    return applications



def create_json_topology():

    t = Topology()
    t.G=nx.barabasi_albert_graph(1000, 5)

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

    return t

def main(simulated_time, case, it):

    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    folder_results = Path("results/")
    folder_results.mkdir(parents=True, exist_ok=True)
    folder_results = str(folder_results)+"/"


    # Panggil fungsi create topology
    t = create_json_topology()
    nx.write_gexf(t.G,folder_results+"graph_topology_simulasi.graphml")


    # Cari mana node mempunyai centrality paling tinggi untuk dijadikan source
    centrality = nx.betweenness_centrality(t.G)
    nx.set_node_attributes(t.G, name="centrality", values=centrality)

    sorted_clustMeasure = sorted(centrality.items(), key=operator.itemgetter(1), reverse=True)

    top5_devices =  sorted_clustMeasure[:5]
    main_fog_device = copy.copy(top5_devices[0][0])

    print("-" * 5)
    print("Top 5 centralised nodes:")
    for item in top5_devices:
        print(item)
    print("-"*5)


    # Panggil fungsi create aplikasi dari json
    dataApp = json.load(open('JSON/app.json'))
    apps = create_applications_from_json(dataApp)

    # Algoritma placement
    placement = NoPlacementOfModules("empty")


    # Minimum selector path
    selectorPath = MinimunPath()

    # setup simulasi
    stop_time = simulated_time
    s = Sim(t, default_results_path="results/Hasil_testing")


    # Nentuin populasi
    dataPopulation = json.load(open('JSON/population.json'))
    # setiap aplikasi memiliki population policy yang unique
    for aName in apps.keys():
        data = []
        for element in dataPopulation["sources"]:
            if element['app'] == aName:
                data.append(element)

        distribution = exponentialDistribution(name="Exp", lambd=random.randint(100,200), seed= int(aName)*100+it)
        pop_app = DynamicPopulation(name="Dynamic_%s" % aName, data=data, iteration=it, activation_dist=distribution)
        s.deploy_app2(apps[aName], placement, pop_app, selectorPath)


if __name__ == '__main__':
    import logging.config
    import os

    pathExperimento = Path("results/")
    print("PATH EXPERIMENTO: ",pathExperimento)
    nSimulations = 1
    timeSimulation = 1000000 #100000

    # Multiple simulations
    for i in range(nSimulations):
        start_time = time.time()

        random.seed(i)
        np.random.seed(i)

        logging.info("Running Conquest - %s" %pathExperimento)

        main(simulated_time=timeSimulation, case='CQ',it=i)

        print("\n--- %s seconds ---" % (time.time() - start_time))
        start_time = time.time()

    print("Simulation Done")
