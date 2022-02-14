import json
from random import randrange

#asasa
# Requirement app dan jumlah APP
jumlah_app = 7
no_module = 99
# ==========================
req_ram = 4
byte_m = 4000
ipt = 600
deadline = 9999

# Buat JSON File Aplikasi
JSONfile=[]
for i in range(jumlah_app):
    module_sel = randrange(no_module)
    string ={
        "name": str(i),
        "transmission": [
            {
                "module": str(i)+"_"+str(module_sel),
                "message_in": "M.USER.APP."+str(i)
            }
        ],
        "module": [
            {
                "RAM": str(randrange(req_ram)),
                "type": "MODULE",
                "id": module_sel,
                "name": str(i)+"_"+str(module_sel)
            }
        ],
        "deadline": randrange(deadline),
        "message": [
            {
                "d": str(i)+"_"+str(module_sel),
                "bytes": randrange(byte_m),
                "name": "M.USER.APP."+str(i),
                "s": "None",
                "id": 0,
                "instructions": randrange(ipt)
            }
        ],
        "id": i
    }
    JSONfile.append(string)

#print(JSONfile)
# Serializing json 
json_object = json.dumps(JSONfile, indent = 2)
  
# Writing json
with open("JSON/"+str(jumlah_app)+" Aplikasi.json", "w") as outfile:
    outfile.write(json_object)

