from xml.etree import ElementTree as ET
import sys
import sqlite_utils

KML = "{Z:\Repositories\TourismMap\passes.kml}"


def iterate_kml(filepath):
    fp = open(filepath)
    parser = ET.XMLPullParser(["end"])
    while True:
        chunk = fp.read(1024 * 8)
        parser.feed(chunk)
        for event, element in parser.read_events():
            assert event == "end"
            if element.tag == f"{KML}Placemark":
                datetime = element.find(f".//{KML}when").text
                source = element.find(f".//{KML}name").text.split("Source: ")[-1]
                longitude, latitude = map(
                    float, element.find(f".//{KML}coordinates").text.split(",")
                )
                yield {
                    "datetime": datetime,
                    "source": source,
                    "latitude": latitude,
                    "longitude": longitude,
                }
        if not chunk:
            break


if __name__ == "__main__":
    db = sqlite_utils.Database("phone-locations.db")
    db["locations"].insert_all(iterate_kml(sys.argv[-1]))