import json 

with open("./data/sample_data.json", "r") as f:
    data = json.load(f)

print(data)
