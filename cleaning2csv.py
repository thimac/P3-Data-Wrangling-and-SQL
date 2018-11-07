# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint
import codecs
import re
import cerberus
import schema
import csv

#SQL table schema
SCHEMA = schema.schema

OSMFILE='SaoPaulo-RegiaoCentral.osm'

#CSV files
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

#regular expression to recognize patterns
lower = re.compile(r'^([a-z]|_)*$')  #only lower letters with or without the underscore in the middle
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$') #two words with the pattern above separated by a colon
problemchars = re.compile(r'[=\+\/\&\<\>;\'"\?\%#\$@\,\. \t\r\n]') #catches all the characters not acceptable (such as =, +, & etc)

#################################################################################

#################################################################################
#ADDRESS CLEANING

#expected addrs type
expected = ["Rua", "Avenida", "Largo", "Ladeira", "Praça", "Marquês", "Viaduto", "Parque", "Alameda", "Travessa", "Vila"]

expected_error = ["Rúa", "R.", "Av.", "praça", "Al.", "rua", "Rue", "Sapopemba", "Alfonso Bovero"]

#problems found
mapping = { "Rúa": "Rua",
	    "rua": "Rua",
	    "Rue": "Rua",
            "Av.": "Avenida",
            "praça": "Praça",
	    "Al."  : "Alameda",
            "Sapopemba": "Avenida Sapopemba",
	    "Alfonso Bovero": "Avenida Prof. Alfonso Bovero"
	    
            }

def update_street (addrstreet):
"""Update street names

    Receive a street name, see if it is right and return the result 

    Args:
        addrstreet: A string with the given street name.

    Returns:
        A string with a street name in the correct pattern.
    """

    street_name = addrstreet.attrib['v'].split(' ')[0]
    if street_name.encode('utf-8') not in expected:
	return update_name(addrstreet.attrib['v'], mapping)

    return addrstreet.attrib['v']

def update_name(name, mapping):
"""Update name: this function assists the update_street.

    Receive a street name, see if it is mapped and return the new name

    Args:
        name: A string with the given street name.
	mapping: A dict mapping the wrong suffix into the right ones

    Returns:
        A string with a street name in the correct pattern.
    """
    temp = name.split(" ")

    if temp[0].encode('utf-8') in expected_error:
    	temp[0] = mapping[temp[0].encode('utf-8')].decode('utf-8')
	name = ' '.join(temp)
    else:
	#cases that there is no prefix for the address(street, avenue etc) - all found in this dataset are streets (Rua)
	name = ' '.join(temp)
	name = "Rua "+name

    return name

#################################################################################

#################################################################################
#POSTAL CODE CLEANING


def update_postalcode(psstring):
"""Update postalcode

    Receive a postalcode, see if it is right and return the result 

    Args:
        psstring: A string with the given postalcode(s).

    Returns:
        A string with the postalcode(s) in the right pattern (0xxxx-xxx)
	or a message in the cases that it is wrong.
    """

    postcodes = psstring.split(";")
    newpostcodes = []

    for postcode in postcodes:
    	fix = re.findall('[0-9]+', postcode)
    	fix = ''.join(fix)

	newps = fix[0:5]+"-"+fix[5:8]

    	if (len(fix) == 8):
    		try:
        		int(fix)
    		except:
        		newps = "Wrong size"
        
    		if fix[0] != "0":
        		newps = "Wrong area"
    	else:
		newps = "Wrong size"

	newpostcodes.append(newps)

    return ';'.join(newpostcodes)


#################################################################################

#################################################################################
#PHONE NUMBER CLEANING

def update_phone(phone):
"""Update phone numbers

    Receive a phone numbers, put in the correct pattern and return.

    Args:
        phone: A string with the given phone number(s)

    Returns:
        A string with the phone number(s) in the right pattern (+55 11xxxxxxxx or +55 11xxxxxxxxx)
    """

    phones = phone.split(";")

    newphones = []

    for phon in phones:
	temp = re.findall('[0-9]+', phon)
	temp = ''.join(temp)

	if temp[0:2] != "55":
		if temp[0:2] != "11":
			temp = "+55 11"+temp
		else:
			temp = "+55 "+temp
	else:
		temp = "+"+temp[0:2]+" "+temp[2:len(temp)]

	newphones.append(temp)
	

    return ';'.join(newphones)
	
	

#################################################################################

#################################################################################
#DATA CLEANING AND EXPORTING TO CSV

#lists with fields used in the sql tables
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

def get_tags(tags_fields, elem, element):
"""get tags

    Get tags, sees if it is right and return the tags cleaned.

    Args:
        tags_fields: A string with the tag field (node_tags or way_tags).
	elem: A string with the element tag.
	element: A string with the element node or way.

    Returns:
        A string with the tag, and if the tag is a street, postcode or a phone, 
	it will be cleaned.
    """

    temp = {}
    temp[tags_fields[0]] = element.attrib['id']

    if elem.attrib['k'] == "addr:street":
    	temp[tags_fields[2]] = update_street(elem)
    elif elem.attrib['k'] == "addr:postcode":
	temp[tags_fields[2]] = update_postalcode(elem.attrib['v'])
    else:
	if elem.attrib['k'] == "phone" or elem.attrib['k'] == "contact:phone":
		temp[tags_fields[2]] = update_phone(elem.attrib['v'])
	else:
		temp[tags_fields[2]] = elem.attrib['v']
                    
    if lower_colon.search(elem.attrib['k']):
        split_temp = elem.attrib['k'].split(":")
        if len(split_temp) == 2:
            temp[tags_fields[1]] = split_temp[1]
            temp[tags_fields[3]] = split_temp[0]
        else:
            temp[tags_fields[1]] = ":".join(split_temp[1:])
            temp[tags_fields[3]] = split_temp[0]
    else:
        temp[tags_fields[1]] = elem.attrib['k']
        temp[tags_fields[3]] = "regular"
    
    return temp;


def shape_element(element):
"""Clean and shape node or way XML element to Python dict

    Args:
	element: A string with the element node or way.

    Returns:
        A a dict with the fields that will be in the sql tables
    """

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  #Handle secondary tags the same way for both node and way elements

    if element.tag == 'node':
        for attribute in element.attrib:
            if attribute in NODE_FIELDS:
                node_attribs[attribute] = element.attrib[attribute]
                
        for elem in element.iter():
            if elem.tag == "tag":
                if problemchars.search(elem.attrib['k']):
                    pass
                else:
                    tags.append(get_tags(NODE_TAGS_FIELDS, elem, element))
        return {'node': node_attribs, 'node_tags': tags}

    elif element.tag == 'way':
        i=0
        for attribute in element.attrib:
            if attribute in WAY_FIELDS:
                way_attribs[attribute] = element.attrib[attribute]

        for elem in element.iter():
            temp={}
            if elem.tag == "nd":
                temp[WAY_NODES_FIELDS[0]] = element.attrib['id']
                temp[WAY_NODES_FIELDS[1]] = elem.attrib['ref']
                temp[WAY_NODES_FIELDS[2]] = i
                i=i+1
                way_nodes.append(temp)
            elif elem.tag == "tag":
                tags.append(get_tags(WAY_TAGS_FIELDS, elem, element))
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


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
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

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


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSMFILE, validate=True)




#################################################################################
