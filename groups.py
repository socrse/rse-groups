__version__ = '0.1.0'

import json
from pathlib import Path
import xml.etree.ElementTree as ET

import tomli


def generate_geojson():
    data_path = Path("groups.toml")
    geojson_path = Path("groups.json")

    with open(data_path, "rb") as f:
        all_groups = tomli.load(f)

    geo_groups = []

    valid_keys = {"name", "head", "phone", "email", "postcode", "website", "twitter", "lat", "lon"}

    for group_id, group in all_groups.items():
        if "name" not in group:
            raise ValueError(f"The RSE group '{group_id}' is missing the `name` key.")

        if not group.keys() <= valid_keys:
            invalid_keys = group.keys() - valid_keys
            raise ValueError(f"The RSE group '{group_id}' has invalid keys: {invalid_keys}")

        geo_groups.append({
            "type": "Feature",
            "properties": {k:v for k, v in group.items() if k not in ["lat", "lon"]},
            "geometry": {
                "type": "Point",
                "coordinates": [group["lon"], group["lat"]]
            }
        })

    with geojson_path.open("w") as out:
        json.dump(geo_groups, out, indent="  ")

def convert_kml_to_toml():
    """
    This is the code that was used to converty from the old KML file to the TOML file
    """
    kml_path = Path("doc.kml")
    tree = ET.parse(kml_path)
    ns = {"kml": "http://www.opengis.net/kml/2.2"}

    output_path = Path("groups.toml")

    extra_mapping = {
        "Head of RSE": "head",
        "Contact number": "phone",
        "Contact email": "email",
        "Location": "postcode",
        "Website": "website",
        "Twitter Handle": "twitter",
    }

    with open(output_path, "w") as out:
        for place in tree.findall(".//{http://www.opengis.net/kml/2.2}Placemark", ns):
            name = place.find("kml:name", ns).text
            group_id = name.lower().replace(" ", "-").replace(",", "-")
            out.write(f"[{group_id}]\n")
            extra = place.find("kml:ExtendedData", ns)
            new_extra = {"name": name}
            for data in extra.findall("kml:Data", ns):
                key = data.attrib["name"]
                value = data.find("kml:value", ns).text
                if value:
                    new_extra[extra_mapping[key]] = value.strip()

            new_extra = {k: new_extra[k] for k in ["name", "head", "website", "email", "phone", "twitter", "postcode"] if k in new_extra}
            for k, v in new_extra.items():
                out.write(f'{k} = "{v}"\n')
            out.write("\n")
