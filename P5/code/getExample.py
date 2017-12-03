#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lxml.etree as ET  # Use cElementTree or lxml if too slow
import datetime as dtm

OSM_FILE = "../Data/Sydney_Australia.osm"  # Replace this with your osm file
SAMPLE_FILE = "Sydney_sample.osm"


def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with open(SAMPLE_FILE, 'wb') as output:
    start_time = dtm.datetime.now()
    print("start processing at :", start_time)

    output.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write(b'<osm>\n')

    # Write every kth top level element
    k = 10
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write(b'</osm>')

    print("finish processing. Total time cost: ", dtm.datetime.now() - start_time)