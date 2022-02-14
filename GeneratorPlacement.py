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

from yafs.core import Sim
from yafs.application import Application,Message


def create_applications_from_json(data):
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
        ms = {}
        for message in app["message"]:
        	#name_message.append(message("name"))
        	name_message.append(message["name"])
        	ms[message["name"]] = Message(message["name"],message["s"],message["d"],instructions=message["instructions"],bytes=message["bytes"])
        	if message["s"] == "None":
        		a.add_source_messages(ms[message["name"]])
    return name_app, name_module, name_message

# Panggil fungsi create aplikasi dari json
dataApp = json.load(open('JSON/11 Aplikasi.json'))
name_app, name_module, name_message = create_applications_from_json(dataApp)

print(name_message)
node_list = [12, 13, 14, 15, 16, 17]

lamb = [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200]

JSONfile={"initialAllocation" : []}
allocation=[]

for idx,node in enumerate(node_list):
	string={
		"module_name": str(name_module[idx]),
		"app": str(name_app[idx]),
		"id_resource": random.choice(node_list)
	}
	allocation.append(string)

JSONfile["initialAllocation"] += allocation
json_object = json.dumps(JSONfile, indent = 2)
with open("JSON/Placement baru.json", "w") as outfile:
	outfile.write(json_object)


JSONfile2={"sources" : []}
popul=[]
for idx,node in enumerate(node_list):
	string={
		"id_resource": random.choice(node_list),
		"app": str(name_app[idx]),
		"message": str(name_message[idx]),
		"lambda": random.choice(lamb)
	}
	popul.append(string)

JSONfile2["sources"] += popul
json_object = json.dumps(JSONfile2, indent = 2)
with open("JSON/Population baru.json", "w") as outfile:
	outfile.write(json_object)



#    sorted_clustMeasure = sorted(centrality.items(), key=operator.itemgetter(1), reverse=True)
#
#    top5_devices =  sorted_clustMeasure[:5]
#    main_fog_device = copy.copy(top5_devices[0][0])
#
#    print("-" * 5)
#    print("Top 5 centralised nodes:")
#    for item in top5_devices:
#        print(item)
#    print("-"*5)
