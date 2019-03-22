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
argparser.add_argument("filename", help="Either predandmin.json, local.json, or subfiles.json.")
argparser.add_argument("SERVERCFG", nargs="?", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
cliArguments = argparser.parse_args()

aspace = archivesspace.ArchivesSpace()
aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
aspace.connect()

logging.basicConfig(level=logging.INFO)

## -----CACHING SETUP----- ##

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

## Running new queries after agents and subjects have been added ##
identifier_1 = 'corporate_after1'
identifier_2 = 'people_after1'
identifier_3 = 'subjects_after1'

query_input = input('Run agent/subject cache? Yes or no?\n')

if query_input == 'yes':
	ca_query = makeQuery('corporate')
	set_in_data_cache(identifier_1, ca_query, 5)

	pa_query = makeQuery('people')
	set_in_data_cache(identifier_2, pa_query, 5)

	sub_query = makeQuery('subject')
	set_in_data_cache(identifier_3, sub_query, 5)

	ca_response = get_from_cache(identifier_1, CACHE_DICTION)
	pa_response = get_from_cache(identifier_2, CACHE_DICTION)
	sub_response = get_from_cache(identifier_3, CACHE_DICTION)
else:
	ca_response = get_from_cache(identifier_1, CACHE_DICTION)
	pa_response = get_from_cache(identifier_2, CACHE_DICTION)
	sub_response = get_from_cache(identifier_3, CACHE_DICTION)


## -----Cleaning YWCA Agent/Subject Data in Mapping Spreadsheet----- ##

def dataAgentSplit(json_obj):
	# Splits agents and appends only their authority ids to a list
	try:
		agent_data = []
		agents = json_obj['agent_subject_name'].split(';')
		for agent in agents:
			agent = agent.split('|')
			auth_id = agent[-1].strip()
			agent_data.append(auth_id)
		json_obj['agent_subject_name'] = agent_data

	except:
		pass

	return json_obj


def dataSubjectSplit(json_obj):
	# Splits subjects and appends only their authority ids to a list
	try:
		subs_topic = []
		topic_subjects = json_obj['subjects_topic'].split(';')
		for sub in topic_subjects:
			sub = sub.split('|')
			sub_id = sub[-1].strip()
			subs_topic.append(sub_id)
		json_obj['subjects_topic'] = subs_topic

	except:
		pass

	try:
		subs_geo = []
		geo_subjects = json_obj['subjects_geographic'].split(';')
		for sub in geo_subjects:
			sub = sub.split('|')
			sub_id = sub[-1].strip()
			subs_geo.append(sub_id)
		json_obj['subjects_geographic'] = subs_geo

	except:
		pass

	try:
		subs_genre = []
		genre_subjects = json_obj['subjects_genre'].split(';')
		for sub in genre_subjects:
			sub = sub.split('|')
			sub_id = sub[-1].strip()
			subs_genre.append(sub_id)
		json_obj['subjects_genre'] = subs_genre

	except:
		pass

	return json_obj


def dataAgentSubjectSplit(json_obj):
	# Calls agent and subject split functions together
	dataAgentSplit(json_obj)
	dataSubjectSplit(json_obj)

	return json_obj


## -----Getting Resource Records for YWCA Microfilm----- ##

def getSeries(resource_num):
    ' Returns first level down children of given resource '

    logging.info('Retrieving Series level children of Resource %s' % resource_num)
    resource_num = str(resource_num)
    series_lst = []

    record = aspace.get('/repositories/2/resources/' + resource_num + '/tree')

    if record['children']:
        for child in record['children']:
            logging.info('Adding each first level child of Resource %s to a list' % resource_num)
            series_lst.append(child)

    return series_lst


def getSeriesUri(series):
    return series['record_uri']


def getChildUri(child):
    # logging.debug('Returning URI for Archival Object %s' % child['record_uri'])
    return child['record_uri']


def getChildUris(series):  # Could probably be reworked
    ' Returns list of child URIs for the child of a parent resource '
    ' Assumes searching through a single series in a record group '

    # logging.info('Retrieving URIs for each child of Series %s passed' % series)
    child_uris = []  # Starting list to append to
    children = series['children']  # Children of the series, which is itself the child of a record group

    child_uris.append(getSeriesUri(series))

    for child in children:
        child_uris.append(getChildUri(child))
        if child['children']:
            for child in child['children']:
                child_uris.append(getChildUri(child))
                if child['children']:
                    for child in child['children']:
                        child_uris.append(getChildUri(child))
                        if child['children']:
                            for child in child['children']:
                                child_uris.append(getChildUri(child))
                                if child['children']:
                                    for child in child['children']:
                                        child_uris.append(getChildUri(child))
                                        if child['children']:
                                            for child in child['children']:
                                                child_uris.append(getChildUri(child))
                                                if child['children']:
                                                    for child in child['children']:
                                                        child_uris.append(getChildUri(child))


    return child_uris


def getAllResourceUris(resource_num):
    ' Calls getSeries and getChildUris to return all the Archival Object URIs for a resource '
    
    # logging.info('Calling getSeries and getChildUris for Resource %s' % resource_num)
    hierarchy = getSeries(resource_num)
    uri_lst = []
    for level in hierarchy:
        logging.info('Adding all Archival Object URIs for Resource to list')
        uri_lst.extend(getChildUris(level))

    return uri_lst


## ---- Getting Agent Data from Other Files ---- ##

all_agents = [] # Combines People and Corporate Agents into a single list
all_agents.extend(ca_response)
all_agents.extend(pa_response)

agent_ids_and_uris = [] # Only authority id and uri are needed
for agent in all_agents:
	try:
		auth = agent['display_name']['authority_id']
		uri = agent['uri']
		agent_ids_and_uris.append((auth, uri))
	except KeyError:
		pass

# Turn into dictionary
agent_ids_and_uris = dict(agent_ids_and_uris)


## ---- Getting Subject Data from Other File ---- ##

sub_ids_and_uris = [] # Only authority id and uri are needed
for sub in sub_response:
	try:
		auth = sub['authority_id']
		uri = sub['uri']
		sub_ids_and_uris.append((auth, uri))
	except KeyError:
		pass

# Turn into dictionary
sub_ids_and_uris = dict(sub_ids_and_uris)


## ==== Change Out Agent/Subject Auth IDs for URIs ==== ##
## -- ON BOTH FUNCTIONS MAKE SURE SUBJECT AND AGENT CACHE DATA IS CURRENT -- ##

def replaceSubjectAuthIDwithURI(json_obj, sub_ids_and_uris):
	try:
		gs_ids = []
		for auth_id in json_obj['subjects_genre']:
			if auth_id in sub_ids_and_uris.keys():
				uri = sub_ids_and_uris[auth_id]
				gs_ids.append(uri)
			json_obj['subjects_genre'] = gs_ids
	except:
		pass

	try:
		geo_ids = []
		for auth_id in json_obj['subjects_geographic']:
			if auth_id in sub_ids_and_uris.keys():
				uri = sub_ids_and_uris[auth_id]
				geo_ids.append(uri)
			json_obj['subjects_geographic'] = geo_ids
	except:
		pass

	try:
		top_ids = []
		for auth_id in json_obj['subjects_topic']:
			if auth_id in sub_ids_and_uris.keys():
				uri = sub_ids_and_uris[auth_id]
				top_ids.append(uri)
			json_obj['subjects_topic'] = top_ids
	except:
		pass

	return json_obj	


def replaceAgentAuthIDwithURI(json_obj, agent_ids_and_uris):
	try:
		agent_uris = []
		for auth_id in json_obj['agent_subject_name']:
			if auth_id in agent_ids_and_uris.keys():
				uri = agent_ids_and_uris[auth_id]
				agent_uris.append(uri)
			json_obj['agent_subject_name'] = agent_uris

	except:
		pass

	return json_obj


def replaceAllAuthIDsWithURIs(json_obj, agent_ids_and_uris, sub_ids_and_uris):
	change_one = replaceAgentAuthIDwithURI(json_obj, agent_ids_and_uris)
	change_two = replaceSubjectAuthIDwithURI(change_one, sub_ids_and_uris)

	return change_two


## ==== Retrieving YWCA Microfilm Records ==== ##
## Querying all Microfilm Records to cache ##

query_input_2 = input('Run microfilm query? Yes or no?\n')
identifier = makeIdentifier('microfilm_archival_objects')

if query_input_2 == 'yes':
	microfilm_uris = getAllResourceUris(659)

	microfilm_records = []
	logging.info('Getting Archival Object records')
	for uri in microfilm_uris:
		record = aspace.get(uri) 
		microfilm_records.append(record)

	logging.info('Putting data into the cache')
	set_in_data_cache(identifier, microfilm_records, 30)
	response = get_from_cache(identifier, CACHE_DICTION)
else:
	response = get_from_cache(identifier, CACHE_DICTION)

## ---- Functions to Retrieve, Modify, and Post Archival Object Record with Subs/Agents Linked ---- ##

def getAOrecord(json_data_obj):
	# Retrieves Archival Object record 
	uri = json_data_obj['ref_id']
	record = aspace.get(uri)

	return record


def getAllSubs(json_data_obj):
	# Combines JSON Object subjects fields into single list
	all_subs = []
	for sub in json_data_obj['subjects_genre']:
		all_subs.append(sub)
	for sub in json_data_obj['subjects_topic']:
		all_subs.append(sub)
	for sub in json_data_obj['subjects_geographic']:
		all_subs.append(sub)

	return all_subs


def getDataDict(json_data_obj, record):
	# Takes the Archival Object record and adds Agent and Subject URIs to it for posting
	record['linked_agents'] = []

	for agent in json_data_obj['agent_subject_name']:
		dictionary = {'ref': agent, 'role': 'subject', 'terms': []}
		record['linked_agents'].append(dictionary)

	record['subjects'] = []
	subs = getAllSubs(json_data_obj)
	for sub in subs:
		dictionary = {'ref': sub}
		record['subjects'].append(dictionary)

	return record


def postRecord(json_data_obj):
	# Calls all functions and posts updated record
	record = getAOrecord(json_data_obj)
	record_to_post = getDataDict(json_data_obj, record)
	posted = aspace.post(record['uri'], requestData=record_to_post)

	return posted

## -----YWCA Data----- ##

filename = cliArguments.filename
with open(filename) as json_file:
	try:
		json_data = json.load(json_file)

	except ValueError:
		exit(1)

## ---- Updating JSON_DATA to INCLUDE AO URIS ---- ##

ids_and_uris = []
for obj in response:
	ref_id = obj['ref_id']
	uri = obj['uri']
	ids_and_uris.append((ref_id, uri))


for obj in json_data['rows']:
	for num in ids_and_uris:
		if num[0] == obj['ref_id']:
			obj['ref_id'] = num[1]


'*****************************'
'Cleaning the spreadsheet data'
'*****************************'

for obj in json_data['rows']:
	change = dataAgentSubjectSplit(obj)

'***********************'
'Posting Updated Records'
'***********************'

for obj in json_data['rows']:
	try:
		updated_obj = replaceAllAuthIDsWithURIs(obj, agent_ids_and_uris, sub_ids_and_uris)
		posted = postRecord(updated_obj)
		print(posted)
	except:
		print('Failed: ', obj['ref_id'])
