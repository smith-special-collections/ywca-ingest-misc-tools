import sys
import os
import requests
import xml.etree.ElementTree as ET
import logging



def parse_title(xml_parser):
    title = xml_parser.find('{http://www.loc.gov/mods/v3}titleInfo/{http://www.loc.gov/mods/v3}title').text
    return title

def get_remote_page_index(pid):
    url = 'https://compass.fivecolleges.edu/islandora/object/' + pid + '/datastream/MODS/download'

    response = requests.get(url)

    remote_xml_parser = ET.fromstring(response.content)
    title = parse_title(remote_xml_parser)
    page_index = int(title.split('-')[-1])
    return page_index

def get_local_page_index(local_xml_filename):
    local_xml_parser = ET.parse(open(local_xml_filename)).getroot()
    title = parse_title(local_xml_parser)
    page_index = int(title.split('_')[-1])
    return page_index

if __name__ == "__main__":
    try:
        local_xml_filename = sys.argv[1]
    except IndexError:
        print( \
        """
        Please provide an xml filename with local id field:
        $ python3 compare_localid_page_islandora_sequence_page.py smith_142075_MODS.xml

        $ cat smith_142075_MODS.xml
        <?xml version="1.0" encoding="UTF-8"?>
        <mods xmlns="http://www.loc.gov/mods/v3" xmlns:mods="http://www.loc.gov/mods/v3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink">
            <titleInfo>
                <title>smith_ssc_324_r021_m002_211</title>
            </titleInfo>
            <identifier type="local">smith_ssc_324_r021_m002_211</identifier>
        </mods>
        $

        Queries prod by default. Edit the code to change that.
        """)
        exit(1)

    filename_elements = os.path.basename(local_xml_filename).split('_')

    pid = filename_elements[0] + ':' + filename_elements[1]
    logging.debug(pid)

    remote_page_index = get_remote_page_index(pid)
    local_page_index = get_local_page_index(local_xml_filename)
    logging.debug(local_xml_filename, pid, remote_page_index, local_page_index)
    if remote_page_index == local_page_index:
        print('pass', local_xml_filename, pid, remote_page_index, local_page_index)
    else:
        print('FAIL', local_xml_filename, pid, remote_page_index, local_page_index)
