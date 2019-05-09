import sys
import requests
import xml.etree.ElementTree as ET

try:
    url = 'https://compass.fivecolleges.edu/islandora/object/' + sys.argv[1] + '/datastream/MODS/download'
except IndexError:
    print( \
    """
    Please provide a pid to query. E.g.
    $ python3 get_object_title.py smith:632926

    Queries prod by default. Edit the code to change that.
    """)
    exit(1)

response = requests.get(url)

xml_parser = ET.fromstring(response.content)
title = xml_parser.find('{http://www.loc.gov/mods/v3}titleInfo/{http://www.loc.gov/mods/v3}title').text
print(title)
