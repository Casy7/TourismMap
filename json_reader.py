from os.path import isfile, join
from os import listdir, replace
import json


class JsonReader:
    def __init__(self) -> None:
        cathegories = {
            "1": [""]
        }
    
    def get_all_points(self):
        mypath = ".\\jsons\\"

        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        passes = []
        for path in onlyfiles:
            with open(".\\jsons\\"+path, 'r', encoding="UTF8") as txt:
                data = txt.read()

            passes += list(json.loads(data)["passes"])
        return passes
