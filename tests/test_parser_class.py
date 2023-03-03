import pcb_parser
from pcb_parser import PCB
import os 
import json
 
os.chdir(os.path.abspath(os.path.dirname(__file__)))

with open("../data/sample_data.json", 'r') as f:
    data = json.load(f)

pcb = PCB(list(data.values())[0])
pcb.draw('./pcb.png')