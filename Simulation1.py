"""

    Created on Wed Nov 22 15:03:21 2017

    @author: isaac

"""
import random
import networkx as nx
import argparse
from pathlib import Path

import operator
import copy
import time
import numpy as np

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
from yafs.distribution import deterministic_distribution,deterministicDistributionStartPoint

from yafs.application import fractional_selectivity

RANDOM_SEED = 1

def create_application(name):
    # APLICATION
    a = Application(name=name)

    a.set_modules([{"Generator":{"Type":Application.TYPE_SOURCE}},
                   {"Actuator": {"Type": Application.TYPE_SINK}}
                   ])

    m_egg = Message("M.Action", "Generator", "Actuator", instructions=100, bytes=10)
    a.add_source_messages(m_egg)

    return a



def create_json_topology():
    """
        TOPOLOGY DEFINITION

    Some attributes of fog entities (nodes) are approximate
    """

    t = Topology()
    t.G=nx.barabasi_albert_graph(20, 5)


    ls = list(t.G.nodes)
    li = {x: int(x) for x in ls}
    nx.relabel_nodes(t.G, li, False) #Transform str-labels to int-labels


    print("Nodes: %i" %len(t.G.nodes()))
    print("Edges: %i" %len(t.G.edges()))
    #MANDATORY fields of a link
    # Default values =  {"BW": 1, "PR": 1}
    valuesOne = {x :1 for x in t.G.edges()}

    #print(valuesOne)

    nx.set_edge_attributes(t.G, name='BW', values=valuesOne)
    nx.set_edge_attributes(t.G, name='PR', values=valuesOne)

    return t



# @profile
def main(simulated_time):

    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    folder_results = Path("results/")
    folder_results.mkdir(parents=True, exist_ok=True)
    folder_results = str(folder_results)+"/"

    """
    TOPOLOGY from a json
    """
    #t = Topology()
    t = create_json_topology()
    #t.load(t_json)
    nx.write_gexf(t.G,folder_results+"testing_mikel.graphml") # you can export the Graph in multiples format to view in tools like Gephi, and so on.

    print(t)

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


    print(main_fog_device)


    """
    APPLICATION
    """
    app1 = create_application("Aplikasi A")
    app2 = create_application("Aplikasi B")

    """
    PLACEMENT algorithm
    """
    #placement = CloudPlacement("onCloud") # it defines the deployed rules: module-device
    #placement.scaleService({"ServiceA": 1})

    placement = NoPlacementOfModules("empty")


    """
    POPULATION algorithm
    """

    number_generators = int(len(t.G)*0.1)
    print(number_generators)
    dDistribution = deterministicDistributionStartPoint(3000,300,name="Deterministic")
    dDistributionSrc = deterministic_distribution(name="Deterministic", time=10)
    pop1 = Evolutive(top5_devices,number_generators,name="top",activation_dist=dDistribution)
    pop1.set_sink_control({"app":app1.name,"number": 1, "module": app1.get_sink_modules()})
    pop1.set_src_control(
        {"number": 1, "message": app1.get_message("M.Action"), "distribution": dDistributionSrc}
        )


    pop2 = Statical(number_generators,name="Statical")
    pop2.set_sink_control({"id": main_fog_device, "number": number_generators, "module": app2.get_sink_modules()})

    pop2.set_src_control(
        {"number": 1, "message": app2.get_message("M.Action"), "distribution": dDistributionSrc})


    """--
    SELECTOR algorithm
    """
    #Their "selector" is actually the shortest way, there is not type of orchestration algorithm.
    #This implementation is already created in selector.class,called: First_ShortestPath
    selectorPath = MinimunPath()

    #selectorPath1 = BroadPath()

    #selectorPath2 = CloudPath_RR()

    """
    SIMULATION ENGINE
    """

    stop_time = simulated_time
    s = Sim(t, default_results_path=folder_results+"run_aplikasi_B")
    #s.deploy_app2(app1, placement, pop1, selectorPath)
    s.deploy_app2(app2, placement, pop1, selectorPath)


    """
    RUNNING - last step
    """
    s.run(stop_time, show_progress_monitor=False)  # To test deployments put test_initial_deploy a TRUE
    s.print_debug_assignaments()

    # s.draw_allocated_topology() # for debugging

if __name__ == '__main__':
    import logging.config
    import os

    logging.config.fileConfig(os.getcwd()+'/logging.ini')

    start_time = time.time()
    main(simulated_time=1000)

    print("\n--- %s seconds ---" % (time.time() - start_time))

    ### Finally, you can analyse the results:
    # print "-"*20
    # print "Results:"
    # print "-" * 20
    # m = Stats(defaultPath="Results") #Same name of the results
    # time_loops = [["M.A", "M.B"]]
    # m.showResults2(1000, time_loops=time_loops)
    # print "\t- Network saturation -"
    # print "\t\tAverage waiting messages : %i" % m.average_messages_not_transmitted()
    # print "\t\tPeak of waiting messages : %i" % m.peak_messages_not_transmitted()PartitionILPPlacement
    # print "\t\tTOTAL messages not transmitted: %i" % m.messages_not_transmitted()
