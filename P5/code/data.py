#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
After auditing is complete the next step is to prepare the data to be inserted into a SQL database.
To do so you will parse the elements in the OSM XML file, transforming them from document format to
tabular format, thus making it possible to write to .csv files.  These csv files can then easily be
imported to a SQL database as tables.

The process for this transformation is as follows:
- Use iterparse to iteratively step through each top level element in the XML
- Shape each element into several data structures using a custom function
- Utilize a schema and validation library to ensure the transformed data is in the correct format
- Write each data structure to the appropriate .csv files

We've already provided the code needed to load the data, perform iterative parsing and write the
output to csv files. Your task is to complete the shape_element function that will transform each
element into the correct format. To make this process easier we've already defined a schema (see
the schema.py file in the last code tab) for the .csv files and the eventual tables. Using the 
cerberus library we can validate the output against this schema to ensure it is correct.

## Shape Element Function
The function should take as input an iterparse Element object and return a dictionary.

### If the element top level tag is "node":
The dictionary returned should have the format {"node": .., "node_tags": ...}

The "node" field should hold a dictionary of the following top level node attributes:
- id
- user
- uid
- version
- lat
- lon
- timestamp
- changeset
All other attributes can be ignored

The "node_tags" field should hold a list of dictionaries, one per secondary tag. Secondary tags are
child tags of node which have the tag name/type: "tag". Each dictionary should have the following
fields from the secondary tag attributes:
- id: the top level node id attribute value
- key: the full tag "k" attribute value if no colon is present or the characters after the colon if one is.
- value: the tag "v" attribute value
- type: either the characters before the colon in the tag "k" value or "regular" if a colon
        is not present.

Additionally,

- if the tag "k" value contains problematic characters, the tag should be ignored
- if the tag "k" value contains a ":" the characters before the ":" should be set as the tag type
  and characters after the ":" should be set as the tag key
- if there are additional ":" in the "k" value they and they should be ignored and kept as part of
  the tag key. For example:

  <tag k="addr:street:name" v="Lincoln"/>
  should be turned into
  {'id': 12345, 'key': 'street:name', 'value': 'Lincoln', 'type': 'addr'}

- If a node has no secondary tags then the "node_tags" field should just contain an empty list.

The final return value for a "node" element should look something like:

{'node': {'id': 757860928,
          'user': 'uboot',
          'uid': 26299,
       'version': '2',
          'lat': 41.9747374,
          'lon': -87.6920102,
          'timestamp': '2010-07-22T16:16:51Z',
      'changeset': 5288876},
 'node_tags': [{'id': 757860928,
                'key': 'amenity',
                'value': 'fast_food',
                'type': 'regular'},
               {'id': 757860928,
                'key': 'cuisine',
                'value': 'sausage',
                'type': 'regular'},
               {'id': 757860928,
                'key': 'name',
                'value': "Shelly's Tasty Freeze",
                'type': 'regular'}]}

### If the element top level tag is "way":
The dictionary should have the format {"way": ..., "way_tags": ..., "way_nodes": ...}

The "way" field should hold a dictionary of the following top level way attributes:
- id
-  user
- uid
- version
- timestamp
- changeset

All other attributes can be ignored

The "way_tags" field should again hold a list of dictionaries, following the exact same rules as
for "node_tags".

Additionally, the dictionary should have a field "way_nodes". "way_nodes" should hold a list of
dictionaries, one for each nd child tag.  Each dictionary should have the fields:
- id: the top level element (way) id
- node_id: the ref attribute value of the nd tag
- position: the index starting at 0 of the nd tag i.e. what order the nd tag appears within
            the way element

The final return value for a "way" element should look something like:

{'way': {'id': 209809850,
         'user': 'chicago-buildings',
         'uid': 674454,
         'version': '1',
         'timestamp': '2013-03-13T15:58:04Z',
         'changeset': 15353317},
 'way_nodes': [{'id': 209809850, 'node_id': 2199822281, 'position': 0},
               {'id': 209809850, 'node_id': 2199822390, 'position': 1},
               {'id': 209809850, 'node_id': 2199822392, 'position': 2},
               {'id': 209809850, 'node_id': 2199822369, 'position': 3},
               {'id': 209809850, 'node_id': 2199822370, 'position': 4},
               {'id': 209809850, 'node_id': 2199822284, 'position': 5},
               {'id': 209809850, 'node_id': 2199822281, 'position': 6}],
 'way_tags': [{'id': 209809850,
               'key': 'housenumber',
               'type': 'addr',
               'value': '1412'},
              {'id': 209809850,
               'key': 'street',
               'type': 'addr',
               'value': 'West Lexington St.'},
              {'id': 209809850,
               'key': 'street:name',
               'type': 'addr',
               'value': 'Lexington'},
              {'id': '209809850',
               'key': 'street:prefix',
               'type': 'addr',
               'value': 'West'},
              {'id': 209809850,
               'key': 'street:type',
               'type': 'addr',
               'value': 'Street'},
              {'id': 209809850,
               'key': 'building',
               'type': 'regular',
               'value': 'yes'},
              {'id': 209809850,
               'key': 'levels',
               'type': 'building',
               'value': '1'},
              {'id': 209809850,
               'key': 'building_id',
               'type': 'chicago',
               'value': '366409'}]}
"""

import csv
import codecs
import pprint
import re
import lxml.etree as ET
import datetime as dtm

import cerberus

import schema

OSM_PATH = "../Data/sydney_australia.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

PHONENUM = re.compile(r'\+61\s2\s\d{4}\s\d{4}')
POSTCODEPROBLEM = re.compile(r'[\?\n\t\r]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def cleanPhoneData(phone_field):
    phone_num_list = phone_field.split(";")
    audit_phone_num = ''

    for phone_num in phone_num_list:
        m = PHONENUM.match(phone_num)
        if m is None:
            # convert all dashes ("-") to spaces
            if "-" in phone_num:
                phone_num = re.sub("-", " ", phone_num)
            # convert all parenthesis to spaces
            if "(" in phone_num or ")" in phone_num:
                phone_num = re.sub("[()]", "", phone_num)
            # remove all + at the first to make it more convenient to clean data
            phone_num = re.sub("\+", "", phone_num)

            # Also, remove all 61 at the first to make it more convenient to clean data
            if phone_num.startswith("61") is True:
                phone_num = phone_num[2:].strip()

            # phone number starts with 1300 is local calls in Australia, I will ignore them
            if phone_num.startswith("1300 ") or phone_num.startswith("1300") is True:
                pass
            # remove '2' or '02'
            elif phone_num.startswith("2") is True:
                phone_num = phone_num[1:].strip()
            elif phone_num.startswith("02") is True:
                phone_num = phone_num[2:].strip()
            
            # now start to clean the format
            if sum(n.isdigit() for n in phone_num) != 8:
                phone_num = None
            elif re.match(r'^\d{8}$', phone_num) is not None:
                phone_num = phone_num[:4] + " " + phone_num[4:]
            elif re.match(r'^\d{4}\s\d{4}$', phone_num) is not None:
                pass
            else:
                re.sub('\s', '', phone_num)
                phone_num = phone_num[:4] + " " + phone_num[4:]

        if phone_num is not None:
            if m is None:
                # after cleaning, readd "+61 2 " prefix
                phone_num = "+61 2 " + phone_num
            
            if len(audit_phone_num) == 0:
                audit_phone_num = phone_num
            else:
                audit_phone_num = audit_phone_num + ";" + phone_num

    if audit_phone_num == '':
        return None
    else:
        return audit_phone_num


def cleanStateName(state_name):
    if (state_name == 'New South Wales'):
        state_name = 'NSW'
    
    return state_name


def cleanPostCode(postcode):
    if postcode.startswith('NSW') is True:
        postcode = postcode[3:].strip()
    
    matcher = re.search(POSTCODEPROBLEM, postcode)
    if matcher is not None:
        postcode = None

    return postcode




def processSubTag(tag, node_id):
    k_attribute = tag.get('k')
    if PROBLEMCHARS.match(k_attribute):
        return None
    elif LOWER_COLON.match(k_attribute):
        k_type = k_attribute[: k_attribute.find(':')]
        k_key = k_attribute[k_attribute.find(':') + 1 :]
    else:
        k_key = k_attribute
        k_type = 'regular'
    
    value_attribute = tag.get('v')
    if (k_attribute == 'phone'):
        value_attribute = cleanPhoneData(value_attribute)
    elif k_attribute == "addr:state":
        value_attribute = cleanStateName(value_attribute)

    tag_object = None
    if value_attribute is not None:
        tag_object = {}
        tag_object['id'] = node_id
        tag_object['key'] = k_key
        tag_object['type'] = k_type
        tag_object['value'] = value_attribute

    return tag_object

def processSubTagChildren(tagList, elemId):
    node_tag = []
    for child in tagList:
        tag = processSubTag(child, elemId)
        if tag:
            node_tag.append(tag)

    return node_tag


def processNode(element):
    node_attribs = {}
    elemAttribs = element.attrib
    
    node_attribs['id'] = elemAttribs['id']
    node_attribs['user'] = elemAttribs['user']
    node_attribs['uid'] = elemAttribs['uid']
    node_attribs['version'] = elemAttribs['version']
    node_attribs['lat'] = elemAttribs['lat']
    node_attribs['lon'] = elemAttribs['lon']
    node_attribs['timestamp'] = elemAttribs['timestamp']
    node_attribs['changeset'] = elemAttribs['changeset']
    node_tags = processSubTagChildren(list(element), element.get('id'))

    return {"node": node_attribs, "node_tags": node_tags}




def processSubNode(node, node_id, pos):
    node_dict = {}
    node_dict['id'] = node_id
    node_dict['node_id'] = node.get('ref')
    node_dict['position'] = pos
    
    return node_dict

def processSubNodeChildren(nodeList, elemId):
    way_nodes = []
    pos = 0
    for child in nodeList:
        node = processSubNode(child, elemId, pos)
        way_nodes.append(node)
        pos += 1

    return way_nodes

def processWay(element):
    way_attribs = {}
    elemAttribs = element.attrib

    way_attribs['id'] = elemAttribs['id']
    way_attribs['user'] = elemAttribs['user']
    way_attribs['uid'] = elemAttribs['uid']
    way_attribs['version'] = elemAttribs['version']
    way_attribs['timestamp'] = elemAttribs['timestamp']
    way_attribs['changeset'] = elemAttribs['changeset']

    way_children = list(element)

    tags = []
    nodes = []

    for child in way_children:
        if child.tag == 'tag':
            tags.append(child)
        elif child.tag == 'nd':
            nodes.append(child)
    
    way_nodes = processSubNodeChildren(nodes, elemAttribs.get('id'))
    way_tags = processSubTagChildren(tags, elemAttribs.get('id'))

    return {"way": way_attribs, "way_nodes": way_nodes, "way_tags": way_tags}



def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # YOUR CODE HERE
    if element.tag == 'node':
        return processNode(element)
    elif element.tag == 'way':
        return processWay(element)


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.items()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)



# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    print("file_in: " + file_in)

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        # nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        # node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        # ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        # way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        # way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)
        
        
        
        nodes_writer = csv.DictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = csv.DictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = csv.DictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = csv.DictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = csv.DictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        startTime = dtm.datetime.now()

        print("start processing at: ", startTime)

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])
        
        print("finish processing. Time used: ", dtm.datetime.now() - startTime)


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)