import json
import random
from random import randrange

#asasa
# Requirement app dan jumlah APP
jumlah_app = 30
no_module = 99
# ==========================
req_ram = [1, 2, 3, 4, 5, 6]
min_byte = 1500
max_byte = 4500
min_ipt = 20
max_ipt = 60
min_deadline = 300
max_deadline = 50000

# Buat JSON File Aplikasi
JSONfile=[]
for i in range(jumlah_app):
    module_sel = randrange(no_module)
    string ={
        "name": str(i),
        "transmission": [
            {
                "message_out": str(i)+"_("+str(i)+"-"+str(i+1)+")",
                "module": str(i)+"_"+str(i),
                "message_in": "M.USER.APP."+str(i)
            },
            {
                "module": str(i)+"_"+str(i+1),
                "message_in": str(i)+"_("+str(i)+"-"+str(i+1)+")"
            },
        ],
        "module": [
            {
                "RAM": random.choice(req_ram),
                "type": "MODULE",
                "id": i,
                "name": str(i)+"_"+str(i)
            }, 
            {
                "RAM": random.choice(req_ram),
                "type": "MODULE",
                "id": i+1,
                "name": str(i)+"_"+str(i+1)
            },
        ],
        "deadline": randrange(min_deadline, max_deadline),
        "message": [
            {
                "d": str(i)+"_"+str(i), 
                "bytes": randrange(min_byte, max_byte), 
                "name": "M.USER.APP."+str(i), 
                "s": "None", 
                "id": i, 
                "instructions": randrange(min_ipt, max_ipt)
            }, 
            {
                "d": str(i)+"_"+str(i+1), 
                "bytes": randrange(min_byte, max_byte), 
                "name": str(i)+"_("+str(i)+"-"+str(i+1)+")",
                "s": str(i)+"_"+str(i),
                "id": i+1, 
                "instructions": randrange(min_ipt, max_ipt)
            },
        ],
        "id": i
    }
    JSONfile.append(string)

#print(JSONfile)
# Serializing json 
json_object = json.dumps(JSONfile, indent = 2)
  
# Writing json
with open("JSON/Experiment_aplikasi/"+str(jumlah_app)+"_aplikasi.json", "w") as outfile:
    outfile.write(json_object)

