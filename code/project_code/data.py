#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json

OSM_FILE = "hongkong.osm"

lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

expected = ["Rd", "Rd.", "Ave", "Ave.", 
            "E", "E.", "W", "W.", "S", "S.", "N", "N."]

mapping = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Ave.": "Avenue",
            "Rd": "Road",
            "Rd.": "Road",
            "E": "East",
            "E.": "East",
            "W": "West",
            "W.": "West",
            "N": "North",
            "N.": "North",
            "S": "South",
            "S.": "South"
            }

def update_name(name, mapping):
    s = street_type_re.search(name)
    if s:
        if s.group(0) in expected:
            name = name.replace(s.group(0), mapping[s.group(0)])

    return name


def is_street_name(elem):
    return (elem.attrib['k'].startswith("addr:street"))


def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        for attrib_key in element.attrib.keys():
            
            if attrib_key not in CREATED and attrib_key not in ["lat", "lon"]:
                node[attrib_key] = element.attrib[attrib_key]

        node["type"] = element.tag
        VALUES = [element.attrib[c] for c in CREATED]
        node["created"] = { k:v for (k,v) in zip(CREATED,VALUES) } 

        if "lat" in element.attrib:
            node["pos"] = [ float(element.attrib["lat"]), 
                            float(element.attrib["lon"]) ]

        # if child tag exist then process it.
        address = dict()
        name = dict()
        for tag in element.iter("tag"):

            if problemchars.search(tag.attrib["k"]):
                pass

            # tag startswith "addr"
            elif tag.attrib["k"].startswith("addr:"):
                if is_street_name(tag):
                    if (tag.attrib["k"] == "addr:street" or tag.attrib["k"] == "addr:street:en"):
                        address[tag.attrib["k"].split(":", 1)[1]] = update_name(tag.attrib["v"], mapping)

                    else:
                        address[tag.attrib["k"].split(":", 1)[1]] = tag.attrib["v"]

                # non-street tags but startswith "addr:"
                else: 
                    address[tag.attrib["k"].split(":", 1)[1]] = tag.attrib["v"]

            # tag startswith "name"
            elif tag.attrib["k"].startswith("name"):
                # name tag contains ":"
                if lower_colon.search(tag.attrib["k"]):
                    if tag.attrib["k"] == "name:en":
                        name["en"] = update_name(tag.attrib["v"], mapping)

                    # non-English name
                    else:
                        name[tag.attrib["k"].split(":", 1)[1]] = tag.attrib["v"]

                else:
                    name[tag.attrib["k"]] = tag.attrib["v"]

            else:
                # other tag (k:v) pairs 
                node[tag.attrib["k"]] = tag.attrib["v"]

        # Add address/name into each node
        if address:
            node["address"] = address

        if name:
            node["name"] = name

        # if element is "way", then process ref attribute
        if element.tag == "way":
            refs = list()

            for elem in element.iter("nd"):
                refs.append(elem.attrib["ref"])
            
            node["node_refs"] = refs

        return node

    else:
        return None


def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data


def test():

    #data = process_map(OSM_FILE, True)
    data = process_map(OSM_FILE, False)
    pprint.pprint(data[0])
    

if __name__ == "__main__":
    test()