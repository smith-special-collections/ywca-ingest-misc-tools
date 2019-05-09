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

'Functions to add new Subjects to ArchivesSpace'

# For geographical subjects
def getDataDict_sg(sub_object):
	
	if len(str(sub_object['subdivision_1'])) == 0:
		data = { "jsonmodel_type":"subject",
			"external_ids":[],
			"publish":True,
			"used_within_repositories":[],
			"used_within_published_repositories":[],
			"terms":[{ "jsonmodel_type":"term",
			"term": sub_object['term_1'],
			"term_type": sub_object['term_type'],
			"vocabulary":"/vocabularies/1"}],
			"external_documents":[],
			"vocabulary":"/vocabularies/1",
			"authority_id": str(sub_object['authority_id']),
			"source": sub_object['source']}

	elif len(str(sub_object['subdivision_2'])) > 0:
		data = { "jsonmodel_type":"subject",
			"external_ids":[],
			"publish":True,
			"used_within_repositories":[],
			"used_within_published_repositories":[],
			"terms":[{ "jsonmodel_type":"term",
			"term": sub_object['term_1'],
			"term_type": sub_object['term_type'],
			"vocabulary":"/vocabularies/1"}, 
			{"jsonmodel_type":"term",
			"term": sub_object['subdivision_1'],
			"term_type": sub_object['subdivision_1_term_type'],
			"vocabulary":"/vocabularies/1"},
			{"jsonmodel_type":"term",
			"term": sub_object['subdivision_2'],
			"term_type": sub_object['subdivision_2_term_type'],
			"vocabulary":"/vocabularies/1"}],
			"external_documents":[],
			"vocabulary":"/vocabularies/1",
			"authority_id": str(sub_object['authority_id']),
			"source": sub_object['source']}

	else:
		data = { "jsonmodel_type":"subject",
			"external_ids":[],
			"publish":True,
			"used_within_repositories":[],
			"used_within_published_repositories":[],
			"terms":[{ "jsonmodel_type":"term",
			"term": sub_object['term_1'],
			"term_type": sub_object['term_type'],
			"vocabulary":"/vocabularies/1"}, 
			{"jsonmodel_type":"term",
			"term": sub_object['subdivision_1'],
			"term_type": sub_object['subdivision_1_term_type'],
			"vocabulary":"/vocabularies/1"}],
			"external_documents":[],
			"vocabulary":"/vocabularies/1",
			"authority_id": str(sub_object['authority_id']),
			"source": sub_object['source']}

	return data

# For topical subjects
def getDataDict_st(sub_object):
	
	if len(str(sub_object['subdivision_1'])) == 0:
		data = { "jsonmodel_type":"subject",
			"external_ids":[],
			"publish":True,
			"used_within_repositories":[],
			"used_within_published_repositories":[],
			"terms":[{ "jsonmodel_type":"term",
			"term": sub_object['term_1'],
			"term_type": sub_object['term_type'],
			"vocabulary":"/vocabularies/1"}],
			"external_documents":[],
			"vocabulary":"/vocabularies/1",
			"authority_id": sub_object['authority_id'],
			"source": sub_object['source']}

	elif len(str(sub_object['subdivision_3'])) > 0:
		data = { "jsonmodel_type":"subject",
			"external_ids":[],
			"publish":True,
			"used_within_repositories":[],
			"used_within_published_repositories":[],
			"terms":[{ "jsonmodel_type":"term",
			"term": sub_object['term_1'],
			"term_type": sub_object['term_type'],
			"vocabulary":"/vocabularies/1"}, 
			{"jsonmodel_type":"term",
			"term": sub_object['subdivision_1'],
			"term_type": sub_object['subdivision_1_term_type'],
			"vocabulary":"/vocabularies/1"},
			{"jsonmodel_type":"term",
			"term": sub_object['subdivision_2'],
			"term_type": sub_object['subdivision_2_term_type'],
			"vocabulary":"/vocabularies/1"},
			{"jsonmodel_type":"term",
			"term": sub_object['subdivision_3'],
			"term_type": sub_object['subdivision_3_term_type'],
			"vocabulary":"/vocabularies/1"}],
			"external_documents":[],
			"vocabulary":"/vocabularies/1",
			"authority_id": sub_object['authority_id'],
			"source": sub_object['source']}

	elif len(str(sub_object['subdivision_2'])) > 0:
		data = { "jsonmodel_type":"subject",
			"external_ids":[],
			"publish":True,
			"used_within_repositories":[],
			"used_within_published_repositories":[],
			"terms":[{ "jsonmodel_type":"term",
			"term": sub_object['term_1'],
			"term_type": sub_object['term_type'],
			"vocabulary":"/vocabularies/1"}, 
			{"jsonmodel_type":"term",
			"term": sub_object['subdivision_1'],
			"term_type": sub_object['subdivision_1_term_type'],
			"vocabulary":"/vocabularies/1"},
			{"jsonmodel_type":"term",
			"term": sub_object['subdivision_2'],
			"term_type": sub_object['subdivision_2_term_type'],
			"vocabulary":"/vocabularies/1"}],
			"external_documents":[],
			"vocabulary":"/vocabularies/1",
			"authority_id": sub_object['authority_id'],
			"source": sub_object['source']}

	else:
		data = { "jsonmodel_type":"subject",
			"external_ids":[],
			"publish":True,
			"used_within_repositories":[],
			"used_within_published_repositories":[],
			"terms":[{ "jsonmodel_type":"term",
			"term": sub_object['term_1'],
			"term_type": sub_object['term_type'],
			"vocabulary":"/vocabularies/1"}, 
			{"jsonmodel_type":"term",
			"term": sub_object['subdivision_1'],
			"term_type": sub_object['subdivision_1_term_type'],
			"vocabulary":"/vocabularies/1"}],
			"external_documents":[],
			"vocabulary":"/vocabularies/1",
			"authority_id": sub_object['authority_id'],
			"source": sub_object['source']}

	return data

# For genre subjects
def getDataDict_sg(sub_object):
	'Returns data dictionary necessary to add new Person Agent to ArchivesSpace'
		
	data = { "jsonmodel_type":"subject",
	"external_ids":[],
	"publish":True,
	"used_within_repositories":[],
	"used_within_published_repositories":[],
	"terms":[{ "jsonmodel_type":"term",
	"term": sub_object['term_1'],
	"term_type": sub_object['term_type'],
	"vocabulary":"/vocabularies/1"}],
	"external_documents":[],
	"vocabulary":"/vocabularies/1",
	"authority_id": sub_object['authority_id'],
	"source": sub_object['source']}

	return data


def addSubject(data_obj):
	'Adds new Subject to ArchivesSpace'
	count = 0
	try:
		count += 1
		response = aspace.post('/subjects', data_obj)
		return response
		print(count)

	except:
		logging.info('Could not add Subject %s' % data_obj['authority_id'])
		pass


def getDataAndAddGeoSubject(sub_obj):
	sub_dict = getDataDict_sg(sub_obj)
	added_agent = addSubject(sub_dict)

	return added_agent


def getDataAndAddTopSubject(sub_obj):
	sub_dict = getDataDict_st(sub_obj)
	added_subject = addSubject(sub_dict)

	return added_subject


def getDataAndAddGenreSubject(sub_obj):
	sub_dict = getDataDict_sg(sub_obj)
	added_subject = addSubject(sub_dict)

	return added_subject


## -----YWCA Geographical Subject Data----- ##

with open('ywcageosubs.json') as json_file:
    try:
    	json_data_geo = json.load(json_file)
    except ValueError:
    	exit(1)

## -----Adding all Geographical Subjects from the YWCA spreadsheet to a list for comparison with the ASpace data----- ##

ywca_spreadsheet_objs_geo = []
for obj in json_data_geo['rows']:
	auth = obj['authority_id']
	title = obj['term_1']
	ywca_spreadsheet_objs_geo.append((auth, title, obj))


## -----YWCA Topical Subject Data----- ##

with open('ywcatopicsubs.json') as json_file:
    try:
    	json_data_top = json.load(json_file)
    except ValueError:
    	exit(1)

## -----Adding all Topical Subjects from the YWCA spreadsheet to a list for comparison with the ASpace data----- ##

ywca_spreadsheet_objs_top = []
for obj in json_data_top['rows']:
	auth = obj['authority_id']
	ywca_spreadsheet_objs_top.append((auth, obj))


## -----YWCA Genre Subject Data----- ##

with open('ywcagenresubs.json') as json_file:
    try:
    	json_data_gen = json.load(json_file)
    except ValueError:
    	exit(1)

## -----String Cleaning (JSON exported the numbers as factors)----- ## 

for obj in json_data_gen['rows']:
	num = str(obj['authority_id'])
	if len(num) > 9:
		obj['authority_id'] = num[:-2]
	else:
		obj['authority_id'] = num

## -----Adding all Genre Subjects from the YWCA spreadsheet to a list for comparison with the ASpace data----- ##

ywca_spreadsheet_objs_gen = []
for obj in json_data_gen['rows']:
	term = obj['term_1']
	ywca_spreadsheet_objs_gen.append((term, obj))

## -------Adding Subjects to ArchivesSpace------- ## 

# Necessary to run cache before adding subjects 
query_type = input('To run query, type yes. To add subjects, type cache.\n')

identifier = 'subjects_before'

if query_type == 'yes':
	query = makeQuery('subject')
	set_in_data_cache(identifier, query, 5)

if query_type == 'cache':	
	sub_response = get_from_cache(identifier, CACHE_DICTION)
	
	aspace_subject_ids = []
	aspace_subject_titles = []
	for sub in sub_response:
		if 'authority_id' in sub.keys():
			auth = sub['authority_id']
			title = sub['title']
			aspace_subject_ids.append(auth)
			aspace_subject_titles.append(title)

	# Adding geopgrahic subs
	geo_subs_to_add = []
	for obj in ywca_spreadsheet_objs_geo: 
		if obj[1] in aspace_subject_titles:
			pass
		else:
			geo_subs_to_add.append(obj[2])

	for sub in geo_subs_to_add:
		added = getDataAndAddGeoSubject(sub)
		print(added)

	# Adding topical subs
	top_subs_to_add = []
	for obj in ywca_spreadsheet_objs_top: 
		if obj[0] in aspace_subject_ids:
			pass
		else:
			top_subs_to_add.append(obj[1])

	for sub in top_subs_to_add:
		added = getDataAndAddTopSubject(sub)
		print(added)

	# Adding genre subs
	genre_subs_to_add = []
	for obj in ywca_spreadsheet_objs_gen: 
		if obj[0] in aspace_subject_titles:
			pass
		else:
			genre_subs_to_add.append(obj[1])

	for sub in genre_subs_to_add:
		added = getDataAndAddGenreSubject(sub)
		print(added)
