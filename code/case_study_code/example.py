#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
import pprint

def count_tags(filename):
    # YOUR CODE HERE
    tags = {}
    tree = ET.parse(filename)
    root = tree.getroot()
    #tags[root.tag] = 1
    for child in root.iter():
        if child.tag in tags:
            tags[child.tag] = tags[child.tag] + 1
        else:
            tags[child.tag] = 1
    
    return tags

def test():

    xml_file = "data.xml"
    tags = count_tags(xml_file)
    pprint.pprint(tags)
    assert tags == {'data': 1,
                    'country': 3,
                    'rank': 3,
                    'year': 3,
                    'gdppc': 3,
                    'neighbor': 5}


if __name__ == "__main__":
    test()