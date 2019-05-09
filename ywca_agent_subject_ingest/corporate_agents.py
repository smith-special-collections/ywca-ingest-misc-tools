import json
import os
from archivesspace import archivesspace
import pprint
import argparse
import logging
from datetime import datetime

# ## -----Connect to ASpace API----- ##

CONFIGFILE = "archivesspace.cfg"

argparser = argparse.ArgumentParser()
argparser.add_argument("SERVERCFG", nargs="?", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
cliArguments = argparser.parse_args()

aspace = archivesspace.ArchivesSpace()
aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
aspace.connect()

logging.basicConfig(level=logging.INFO)


## --------------------------------------------- ##

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
DEBUG = True
CACHE_FNAME = 'cache_file.json'

try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_json = cache_file.read()
    CACHE_DICTION = json.loads(cache_json)
    cache_file.close()
except:
    CACHE_DICTION = {}


def makeIdentifier(query_type):
    identifier = query_type

    return identifier

# must either be corporate, people, or subject
def makeQuery(query_type):
    if query_type == 'corporate':
        uri = '/agents/corporate_entities?all_ids=true'
        ca_agents = aspace.get(uri)
        aspace_ca = []
        for agent in ca_agents:
            logging.info('Querying Corporate Agent %s' % agent)
            record = aspace.get('/agents/corporate_entities/' + str(agent))
            aspace_ca.append(record)
        return aspace_ca
    elif query_type == 'people':
        uri = '/agents/people?all_ids=true'
        pa_agents = aspace.get(uri)
        aspace_pa = []
        for agent in pa_agents:
            logging.info('Querying People Agent %s' % agent)
            record = aspace.get('/agents/people/' + str(agent))
            aspace_pa.append(record)
        return aspace_pa
    elif query_type == 'subject':
        uri = '/subjects?all_ids=true'
        subs = aspace.get(uri)
        aspace_subs = []
        for sub in subs:
            logging.info('Querying Subject %s' % sub)
            record = aspace.get('/subjects/' + str(sub))
            aspace_subs.append(record)
        return aspace_subs
    else:
        error = 'Query type must either be corporate, people, or subject'
        return error


# data is response from makeQuery
def set_in_data_cache(identifier, data, expire_in_days):
    identifier = identifier.upper()
    CACHE_DICTION[identifier] = {
        'values': data,
        'timestamp': datetime.now().strftime(DATETIME_FORMAT),
        'expire_in_days': expire_in_days
    }

    with open(CACHE_FNAME, 'w') as cache_file:
        cache_json = json.dumps(CACHE_DICTION)
        cache_file.write(cache_json)


def has_cache_expired(timestamp_str, expire_in_days):
    now = datetime.now()
    cache_timestamp = datetime.strptime(timestamp_str, DATETIME_FORMAT)
    delta = now - cache_timestamp
    delta_in_days = delta.days

    if delta_in_days > expire_in_days:
        return True
    else:
        return False


def get_from_cache(identifier, cache_dictionary):
    identifier = identifier.upper()
    if identifier in cache_dictionary:
        data_assoc_dict = cache_dictionary[identifier]
        if has_cache_expired(data_assoc_dict['timestamp'],data_assoc_dict["expire_in_days"]):
            if DEBUG:
                print("Cache has expired for {}".format(identifier))
            del cache_dictionary[identifier]
            data = None
        else:
            data = cache_dictionary[identifier]['values']
    else:
        data = None
    return data


'Functions to add new Agents to ArchivesSpace'

def getDataDict_c(agent_object):
	'Returns data dictionary necessary to add new Corporate Agent to ArchivesSpace'

	data = {"jsonmodel_type":"agent_corporate_entity",
	"names":[{"jsonmodel_type":"name_corporate_entity",
	"use_dates":[],
	"authorized":False,
	"is_display_name":True,
	"sort_name_auto_generate":True,
	"rules": agent_object['rules'],
	"primary_name": agent_object['primary_part_of_name'],
	"subordinate_name_1": agent_object['subordinate_name_1'],
	"subordinate_name_2": agent_object['subordinate_name_2'],
	"number":"",
	"sort_name":"auto",
	"dates":"",
	"qualifier":"",
	"authority_id": agent_object['authority_id'],
	"source": agent_object['source'] }],
	"related_agents":[],
	"agent_type":"agent_corporate_entity"}

	return data


def addAgent_c(data_obj):
	'Posts new Corporate Agent to ArchivesSpace'

	try:
		response = aspace.post('/agents/corporate_entities', data_obj)
		return response
	except:
		pass


def getDataAndAddAgent(agent_obj):
	agent_dict = getDataDict_c(agent_obj)
	added_agent = addAgent_c(agent_dict)

	return added_agent


## -----Corporate Agents from YWCA Spreadsheet----- ##
with open('ywcacorporateagents.json') as json_file:
    try:
    	json_data = json.load(json_file)
    except ValueError:
    	exit(1)

## -----Adding all Corporate Agents from the YWCA spreadsheet to a list for comparison with ArchivesSpace data----- ##
ywca_spreadsheet_objs = []
for obj in json_data['rows']:
	if obj['subordinate_name_1'] != "" and obj['subordinate_name_2'] != "": 
		title = obj['primary_part_of_name'] + " " + obj['subordinate_name_1'] + " " + obj['subordinate_name_2']
		# logging.info('Adding Agent %s from spreadsheet to list' % title)
		ywca_spreadsheet_objs.append((title, obj))
	elif obj['subordinate_name_1'] != "" and obj['subordinate_name_2'] == "":
		title = obj['primary_part_of_name'] + " " + obj['subordinate_name_1']
		# logging.info('Adding Agent %s from spreadsheet to list' % title)
		ywca_spreadsheet_objs.append((title, obj))
	else:
		title = obj['primary_part_of_name']
		# logging.info('Adding Agent %s from spreadsheet to list' % title)
		ywca_spreadsheet_objs.append((title, obj))


# Necessary to run the query before adding the agents
query_type = input('To run query, type yes. To add corporate agents, type cache.\n')

identifier = 'corporate_before'

if query_type == 'yes':
	query = makeQuery('corporate')
	set_in_data_cache(identifier, query, 5)

if query_type == 'cache':	
	ca_response = get_from_cache(identifier, CACHE_DICTION)
	
	aspace_agent_names = []
	for agent in ca_response:
		name = agent['title']
		aspace_agent_names.append(name)


	agents_to_add = []
	for obj in ywca_spreadsheet_objs: 
		if obj[0] in aspace_agent_names:
			pass
		else:
			agents_to_add.append(obj[1])
	
	for agent in agents_to_add:
		added = getDataAndAddAgent(agent)
		print(added)	
