# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint
import codecs
import re

OSMFILE='SaoPaulo-RegiaoCentral.osm'

#regular expression to recognize patterns 
lower = re.compile(r'^([a-z]|_)*$') #only lower letters with or without the underscore in the middle
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$') #two words with the pattern above separated by a colon
problemchars = re.compile(r'[=\+\/\&\<\>;\'"\?\%#\$@\,\. \t\r\n]') #catches all the characters not acceptable (such as =, +, & etc)

###############################################################################

###############################################################################
#HOW MANY TAGS OF EACH TYPE

def count_tags(filename):
"""count tags

    Receive a XML file  and count how many each tag are in it 

    Args:
        filename: the XML file name

    Returns:
        A dict with the number of the tags
    """

    data = {}
    
    tree = ET.parse(filename)
    root = tree.getroot()

    for child in tree.iter():
        data[child.tag] = 0
    for child in tree.iter():
        data[child.tag] = data[child.tag] + 1
        
    return data

#################################################################################

#################################################################################
#TYPE OF TAGS
def key_type(element, keys):
"""Key type

    Verifies the element type (using the regex) and count them 

    Args:
        element: the element tag
	keys: a dict with the counted elements

    Returns:
        A dict with the counted elements
    """

    if element.tag == "tag":
        
        if lower.search(element.attrib['k']):
            keys["lower"] = keys["lower"] + 1
        elif lower_colon.search(element.attrib['k']):
            keys["lower_colon"] = keys["lower_colon"] + 1
        elif problemchars.search(element.attrib['k']):
            keys["problemchars"] = keys["problemchars"] + 1
        else:
            keys["other"] = keys["other"] + 1

    return keys


def process_map(filename):
""" Iterates over the XML file to count the element types """

    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys

#################################################################################

#################################################################################
#STREET AUDIT

#expected addrs type
expected = ["Rua", "Avenida", "Largo", "Ladeira", "Praça", "Marquês", "Viaduto", "Parque", "Alameda", "Travessa", "Vila"]

#expected errors found in the prior analysis
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

def audit_street_type(street_types, street_name):
""" Verifies if the street name is expected """

    street_type = street_name.split(' ')[0]
    if street_type.encode('utf-8') not in expected:
        street_types[street_type].add(street_name)


def audit_st(osmfile):
"""Street audit

    Receives the XML file and verifies if the streets are correct

    Args:
        osmfile: XML file

    Returns:
        A dict with all the street outside the standard
    """

    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.attrib['k'] == "addr:street":
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()

    return street_types

def update_name(name, mapping):
""" Cleaning part: performs the street name corrections """

    temp = name.split(" ")

    if temp[0].encode('utf-8') in expected_error:
    	temp[0] = mapping[temp[0].encode('utf-8')].decode('utf-8')
	name = ' '.join(temp)
    else:
	#cases that there is no prefix for the address(street, avenue etc) - all found in this dataset are streets (Rua)
	name = ' '.join(temp)
	name = "Rua "+name

    return name


def street_audit(osmfile):
""" Cleaning part: performs the street name corrections """

    st_types = audit_st(osmfile)

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
	    stringout = name+" => "+better_name
	    print stringout.encode('utf-8')


#################################################################################

#################################################################################
#POSTAL CODE AUDIT

def parser(psstring):
"""Postalcode parser

    Parser over the given postal code and print 
    if it is not correct

    Args:
        psstring: postal code(s)
    """

    postcodes = psstring.split(";")

    for postcode in postcodes:
    	fix = re.findall('[0-9]+', postcode) #regex to find only the numbers in the string
    	fix = ''.join(fix)

    	if (len(fix) == 8):
    		try:
        		int(fix)
    		except:
        		print "postcode is not a number"
        
    		if fix[0] != "0":
        		print "postcode error - area code error :",postcode

    	else:
		print "postcode error - format is wrong :",postcode



def is_postcode(elem):
    return (elem.attrib['k'] == "addr:postcode")

def postcode_audit(osmfile):
"""Postalcode audit: Parser over XML file an audit the postal codes """

    osm_file = open(osmfile, "r")
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_postcode(tag):
                    parser(tag.attrib['v'])
    osm_file.close()

#################################################################################

#################################################################################

def test(test_type):
""" Executes the functions defined in the ipynb file """

    if test_type == "count_tags":
	toprint = count_tags(OSMFILE)
    elif test_type == "key_type":
    	toprint = process_map(OSMFILE)
    elif test_type == "street_audit":
	street_audit(OSMFILE)
	return
    elif test_type == "postcode_audit":
	postcode_audit(OSMFILE)
	return

    pprint.pprint(toprint)
    print "\n \n"
