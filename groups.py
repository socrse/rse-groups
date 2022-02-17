# SPDX-FileCopyrightText: © 2022 Matt Williams <matt@milliams.com>
# SPDX-License-Identifier: MIT

__version__ = '0.1.0'

from difflib import get_close_matches
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import List

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
            suggestions = ((key, list_to_english(get_close_matches(key, valid_keys))) for key in invalid_keys)
            suggestion_texts = [f"Found '{k}', did you mean {s}" if s else f"Found '{k}'" for k, s in suggestions]
            suggestion_text = '\n  '.join(suggestion_texts)
            raise ValueError(f"The RSE group '{group_id}' has invalid keys:\n  {suggestion_text}")

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


def list_to_english(words: List[str]) -> str:
    """
    Examples:
        >>> list_to_english(["a", "b", "c"])
        "'a', 'b' or 'c'"
        >>> list_to_english(["a"])
        "'a'"
    """
    if not words:
        return ""
    *head, tail = words
    tail = f"'{tail}'"
    if head:
        head = ", ".join(f"'{w}'" for w in head)
        return f"{head} or {tail}"
    else:
        return f"{tail}"


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
