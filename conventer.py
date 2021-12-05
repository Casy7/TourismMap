import re
from os.path import isfile, join
from os import listdir, replace
import json
text = ""


def multi_replace(text: str, replace_list: list):
    for replace_pair in replace_list:
        text = text.replace(replace_pair[0], replace_pair[1])
    return text


class PointsConventer():
    def __init__(self) -> None:
        pass

    def convent_all_files(self):
        mypath = ".\\passes\\"

        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        text = ""
        for path in onlyfiles:
            filename = path.split(".")[-2]
            with open(".\\passes\\"+path, 'r', encoding="UTF8") as txt:
                text = txt.read()
                text = text[text.find("\""):]

            start_index = 0
            def match(): return text[start_index:].find("\n")+start_index
            while match() != -1 and start_index < len(text):
                caret = match()
                if text[caret-1:caret+1] != "\"\n":
                    text = text[:caret]+" "+text[caret+1:]
                start_index = caret+1

            start_index = 0

            def s_name_match(): return text.find("\"<table class=\"\"westra_passes\"\">")
            while s_name_match() != -1:
                text = text[:s_name_match(
                )]+text[text.find("<tr><th>Категория сложности", s_name_match()):]

            text = text.replace("\"\n", "\"\n},")
            text = "{\"passes\":[\n"+text+"\n]\n}\n"
            text = text[:]
            replace_pairs = {
                ("\n\"пер.", "{\n\"name\" : \"пер."),
                (",\"false\",", ", "),
                ("</font></h2></th></tr>", "\", "),
                ("<tr><th>Другие названия</th><td>", "\"o_names\" : \""),
                ("</td></tr>", "\", "),
                ("<tr><th>Категория сложности</th><td>", "\"cathegory\" : \""),
                ("<tr><th>Высота</th><td>", "\"height\" : \""),
                ("<tr><th>Характер склонов</th><td>", "\"heels_type\" : \""),
                ("<tr><th>Соединяет</th><td>", "\"connects_with\" : \""),
                ("false\", \"s_name", "s_name"),
                ("\"false\",\"cathegory", "\"cathegory"),
                (",\"пер.", ", \n{\n\"name\" : \"пер.")
            }
            text = multi_replace(text, replace_pairs)
            while text.find("<tr><th>Координаты WGS84</th><td>") != -1:
                i = text.find("<tr><th>Координаты WGS84</th><td>")
                j = text.find("<a href=")
                text = text[0:i] + "\"link\" : \""+text[j+8:]
            text_coma = text.rpartition(",")
            text = text_coma[0]+text_coma[2]

            text = text.replace(
                "\'>Посмотреть подробнее в Каталоге</a></b>\",\"POINT Z ", "\", \"coords\" : \"")
            with open(".\\jsons\\"+filename+".json", 'w', encoding="UTF8") as txt:
                txt.write(text)

    def split_connections_to_atoms(self, json):
        for item in json:
            connects = item["connects_with"]
            atom1 = ""
            atom2 = ""
            delitimers = {
                " и ",
                " - ",
                " — ",
                ", ",
                " с "
            }
            connects = multi_replace(connects, {("Б.", "Большой "),
                                                ("Бол.", "Большой "),
                                                ("М.", "Малый "),
                                                ("Мал.", "Малый "),
                                                ("Пр.", "Правый "),
                                                ("Лев.", "Левый "),
                                                ("Сев.", "Северный "),
                                                ("С.", "Северный "),
                                                ("Южн.", "Южный "),
                                                ("Ю.", "Южный "),
                                                ("Вост.", "Восточный "),
                                                ("В.", "Восточный "),
                                                ("Зап.", "Западный "),
                                                ("З.", "Западный ")})
            connects = " ".join(connects.split())

            for sep in delitimers:
                if sep in connects:
                    # removes duplicate spaces
                    atom1, atom2 = connects.split(sep, 1)
                    name1, name2 = atom1, atom2
                    break
            names = []
            types = ["", ""]
            # В общем. Тут подобие распознавания названий соединений, сюда лучше не смотреть
            c = 0
            for atom in (atom1, atom2):
                name = ""
                for i in range(len(atom)):
                    symbol = atom[i]
                    if symbol.isupper():
                        name += symbol
                        i += 1
                        while i < len(atom) and atom[i].isalpha() or i < len(atom) and atom[i] == "-":
                            name += atom[i]
                            i += 1
                        if i < len(atom)-1 and atom[i] == " " and atom[i+1].isupper() and len(name) > 0 and name[-1] != " ":
                            name += " "
                            while i < len(atom) and atom[i].islower():
                                name += atom[i]
                                i += 1
                        else:
                            break
                        i += 1

                names.append(name)

                type_part = atom.replace(names[c], "")
                if "лед" in type_part:
                    types[c] = "лед"
                elif "р." in type_part or "рек" in type_part:
                    types[c] = "р"
                elif "дол" in type_part:
                    types[c] = "дол"
                elif "с." in type_part or "пос" in type_part:
                    types[c] = "пос"
                elif "ущ" in type_part:
                    types[c] = "ущ"

                if types[0] == "" and types[1] != "":
                    types[0] = types[1]
                elif types[1] == "" and types[0] != "":
                    types[1] = types[0]
                elif types[0] == types[1] == "":
                    types[0] = types[1] = "р"

                c += 1
            # print(types[0]+".", names[0], "-", types[1]+".", names[1])
            item["connect_1_type"] = types[0]
            item["connect_1_name"] = names[0]
            item["connect_2_type"] = types[1]
            item["connect_2_name"] = names[1]

        return json

    def convent_coords(self, json: dict):
        for item in json:
            txt_coords = item["coords"].replace("(", "").replace(")", "")
            list_coords = txt_coords.split()
            item["x_coord"] = float(list_coords[1])
            item["y_coord"] = float(list_coords[0])
            item.pop("coords")
        return json

    def load_cathegory(self, name):

        text = ""
        with open(".\\jsons\\"+name+".json", 'r', encoding="UTF8") as txt:
            text = txt.read()
        passes = json.loads(text)["passes"]
        # passes_formatted = []
        # for pass_json in passes:
        #     passes_formatted.append(self.split_connections_to_atoms(pass_json))
        return passes

    def get_passes_of_cathegory(self, cathegory: int):
        self.convent_all_files()
        passes = []
        passes.extend(self.load_cathegory("uncategorized"))
        passes.extend(self.load_cathegory("uncertain"))

        # TODO ITS A TEST SHIT!!!!!
        if cathegory == -35:
            passes = []
            passes.extend(self.load_cathegory("32B"))
        if cathegory >= 1:
            passes.extend(self.load_cathegory("1A"))
        if cathegory >= 2:
            passes.extend(self.load_cathegory("1B"))
        if cathegory >= 3:
            passes.extend(self.load_cathegory("2A"))
        if cathegory >= 4:
            passes.extend(self.load_cathegory("2B"))
        if cathegory >= 5:
            passes.extend(self.load_cathegory("3A"))
        if cathegory >= 6:
            passes.extend(self.load_cathegory("3B"))
        return self.split_connections_to_atoms(self.convent_coords(passes))


class WayConventer():
    def __init__(self, way) -> None:
        self.way = way
        self.geojson_format = self.generateGeoJSON()

    def generateGeoJSON(self):
        way = self.way
        geojson = {
            "type": "FeatureCollection",
            "features": []
        }
        end_land = way[-1]
        end_land_json = {
            "type": "Feature",
            "geometry": {
                    "type": "Point",
                    "coordinates": [end_land.x_coord, end_land.y_coord]
            },
            "properties": {
                "name": end_land.__str__()
            }
        }
        geojson["features"].append(end_land_json)
        for l_index in range(len(way)-1):
            land = way[l_index]

            land_point = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [land.x_coord, land.y_coord]
                },
                "properties": {
                    "name": land.__str__()
                }
            }
            geojson["features"].append(land_point)

            for connection in land.connections:
                if connection.land == way[l_index+1]:
                    pass_point = {
                        "type": "Feature",
                        "geometry": {
                                "type": "Point",
                                "coordinates": [connection.pass_obj.x_coord, connection.pass_obj.y_coord]
                        },
                        "properties": {
                            "name": connection.pass_obj.name
                        }
                    }
                    geojson["features"].append(pass_point)
                    connection_pass_opposite_land = {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [
                                [connection.land.x_coord, connection.land.y_coord],
                                [connection.pass_obj.x_coord,
                                    connection.pass_obj.y_coord]
                            ]
                        },
                        "properties": {
                            "name": connection.land.__str__()+" - "+connection.pass_obj.name
                        }
                    }
                    geojson["features"].append(connection_pass_opposite_land)
                    connection_pass_land = {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [
                                [land.x_coord, land.y_coord],
                                [connection.pass_obj.x_coord,
                                    connection.pass_obj.y_coord]
                            ]
                        },
                        "properties": {
                            "name": land.__str__()+" - "+connection.pass_obj.name
                        }
                    }
                    geojson["features"].append(connection_pass_land)

            l_index += 1

        with open('html_template/map.json', 'w', encoding="utf-8") as f:
            json.dump(geojson, f)

        mapbox_format = ""
        id = 0
        coords = []
        points = []
        for feature in geojson["features"]:
            json_feature = {}

            if feature["geometry"]["type"] == "LineString":
                json_feature = """"map.addLayer({
                    "id": \'"""+('l' + str(id))+"""\',
                    "type": 'line',
                    "source": {
                        "type": 'geojson',
                        "data": {
                            "type": 'FeatureCollection',
                            "features": [
                                {
                                    "type": 'Feature',
                                    "geometry": {
                                        "type": 'LineString',
                                        "coordinates": """+str(feature["geometry"]["coordinates"])+"""
                                    },
                                    "properties": {
                                        "name": \'"""+feature["properties"]["name"]+"""\'
                                    }
                                }
                            ]
                        }
                    },
                    "layout": {},
                    "paint": {
                        'line-color': '#ff0000',
                        'line-width': 3
                    }
                });\n"""
                txt = str(json_feature).replace("\"", "")
                mapbox_format += txt+"\n"
            else:
                json_feature = {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': feature["geometry"]["coordinates"]
                    },
                    'properties': {
                        'title': feature["properties"]["name"]
                    }
                }
                points.append(json_feature)
                coords = feature["geometry"]["coordinates"]
            id += 1

        txt = ""
        with open('html_template/index.html', 'r', encoding="utf-8") as f:
            txt = f.read()

        fin_text = txt.replace("@@@REPLACETHISTEXT@@@", mapbox_format).replace(
            "@@@COORDS@@@", str(coords)).replace("@@@FEATURES@@@", str(points))

        with open('html_template/index2.html', 'w', encoding="utf-8") as ft:
            ft.write(fin_text)


if __name__ == "__main__":

    conv = PointsConventer()
    conv.split_connections_to_atoms(conv.get_passes_of_cathegory(3))

    # print("succesfully convented")
