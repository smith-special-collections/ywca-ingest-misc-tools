import json
import os
import pprint
import logging
from archivesspace import archivesspace
import argparse
import sys

# ## -----Connect to ASpace API----- ##

CONFIGFILE = "archivesspace.cfg"

argparser = argparse.ArgumentParser()
argparser.add_argument("SERVERCFG", nargs="?", default="DEFAULT", help="Name of the server configuration section e.g. 'production' or 'testing'. Edit archivesspace.cfg to add a server configuration section. If no configuration is specified, the default settings will be used host=localhost user=admin pass=admin.")
cliArguments = argparser.parse_args()

aspace = archivesspace.ArchivesSpace()
aspace.setServerCfg(CONFIGFILE, section=cliArguments.SERVERCFG)
aspace.connect()

logging.basicConfig(level=logging.INFO)


# Record Spreadsheet Data #

with open('predandmin.json') as json_file:
    try:
    	json_data_pred = json.load(json_file)
    except ValueError:
    	exit(1)


with open('subfiles.json') as json_file:
	try:
		json_data_subs = json.load(json_file)
	except ValueError:
		exit(1)


with open('local.json') as json_file:
	try:
		json_data_loc = json.load(json_file)
	except ValueError:
		exit(1)


# Importing Spliting Function
from splitting_functions import *

all_record_metadata_objs = []

for obj in json_data_loc['rows']:
	obj = dataAgentSubjectSplit(obj)
	all_record_metadata_objs.append(obj)

for obj in json_data_pred['rows']:
	obj = dataAgentSubjectSplit(obj)
	all_record_metadata_objs.append(obj)

for obj in json_data_subs['rows']:
	obj = dataAgentSubjectSplit(obj)
	all_record_metadata_objs.append(obj)

# print(pprint.pformat(all_record_metadata_objs[:-2]))
# print('*******')

agents = []
geo_subs = []
top_subs = []
genre_subs = []

for obj in all_record_metadata_objs:
	if len(obj['agent_subject_name']) > 0:
		for name in obj['agent_subject_name']:
			agents.append(name)
	if len(obj['subjects_geographic']) > 0:
		for geo in obj['subjects_geographic']:
			geo_subs.append(geo)
	if len(obj['subjects_topic']) > 0:
		for topic in obj['subjects_topic']:
			top_subs.append(topic)
	if len(obj['subjects_genre']) > 0:
		for genre in obj['subjects_genre']:
			genre_subs.append(genre)


## --------------------------------------------- ##

'Functions to add new Corporate Agents to ArchivesSpace'

def getDataDict_c(agent_object):
	'Returns data dictionary necessary to add new Corporate Agent to ArchivesSpace'

	data = {"jsonmodel_type":"agent_corporate_entity",
	"names":[{"jsonmodel_type":"name_corporate_entity",
	"use_dates":[],
	"authorized":False,
	"is_display_name":True,
	"sort_name_auto_generate":True,
	"rules": "dacs",
	"primary_name": agent_object['name'],
	"subordinate_name_1": "",
	"subordinate_name_2": "",
	"number":"",
	"sort_name":"auto",
	"dates":"",
	"qualifier":"",
	"authority_id": agent_object['id'],
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
		logging.info('Could not add %s' % data_obj['authority_id'])
		pass


def getDataAndAddAgent(agent_obj):
	agent_dict = getDataDict_c(agent_obj)
	added_agent = addAgent_c(agent_dict)

	return added_agent


# for agent in agents:
# 	added = getDataAndAddAgent(agent)
# 	print(added)

'Functions to add new People Agents to ArchivesSpace'

def getDataDict_p(agent_object):
	'Returns data dictionary necessary to add new Person Agent to ArchivesSpace'
		
	try:	
		data = {"jsonmodel_type":"agent_person",
		"names":[{"jsonmodel_type":"name_person",
		"use_dates":[],
		"authorized":False,
		"is_display_name":True,
		"sort_name_auto_generate":True,
		"primary_name": agent_object['last_name'],
		'rest_of_name': agent_object['first_name'],
		"suffix": "",
		"number":"",
		"sort_name":"auto",
		"name_order":"inverted",
		"dates": agent_object['hendrie'],
		"qualifier":"",
		"authority_id": agent_object['id'],
		"source": agent_object['source'] }],
		"related_agents":[],
		"agent_type":"agent_person"}

		return data

	except KeyError:
		pass

	
def addAgent_p(data_obj):
	'Posts new Person Agent to ArchivesSpace'

	try:
		response = aspace.post('/agents/people', data_obj)
		return response
	except:	
		logging.info('Could not add %s' % data_obj['authority_id'])
		pass


def getDataAndAddAgent(agent_obj):
	agent_dict = getDataDict_p(agent_obj)
	if agent_dict != None:
		added_agent = addAgent_p(agent_dict)

		return added_agent
	else:
		return None


'Function to add new Genre Subjects to ArchivesSpace'

def getDataDict_sgenre(sub_object):
	'Returns data dictionary necessary to add new Genre Sub to ArchivesSpace'
	
	try:	
		data = { "jsonmodel_type":"subject",
			"external_ids":[],
			"publish":True,
			"used_within_repositories":[],
			"used_within_published_repositories":[],
			"terms":[{ "jsonmodel_type":"term",
			"term": sub_object['name'],
			"term_type": "genre_form",
			"vocabulary":"/vocabularies/1"}],
			"external_documents":[],
			"vocabulary":"/vocabularies/1",
			"authority_id": sub_object['id'],
			"source": sub_object['source']}
	except TypeError:
		data = {}


	return data


'Function to add new Topical Subjects to ArchivesSpace'

def getDataDict_stop(sub_object):
	
	try:
		data = { "jsonmodel_type":"subject",
			"external_ids":[],
			"publish":True,
			"used_within_repositories":[],
			"used_within_published_repositories":[],
			"terms":[{ "jsonmodel_type":"term",
			"term": sub_object['name'],
			"term_type": "topical",
			"vocabulary":"/vocabularies/1"}],
			"external_documents":[],
			"vocabulary":"/vocabularies/1",
			"authority_id": sub_object['id'],
			"source": sub_object['source']}
	except TypeError:
		data = {}

	return data


'Function to add new Geographic Subjects to ArchivesSpace'

def getDataDict_sgeo(sub_object):
	
	try:
		data = { "jsonmodel_type":"subject",
			"external_ids":[],
			"publish":True,
			"used_within_repositories":[],
			"used_within_published_repositories":[],
			"terms":[{ "jsonmodel_type":"term",
			"term": sub_object['name'],
			"term_type": "geographic", 
			"vocabulary":"/vocabularies/1"}],
			"external_documents":[],
			"vocabulary":"/vocabularies/1",
			"authority_id": sub_object['id'],
			"source": sub_object['source']}
	except TypeError:
		data = {}

	return data


'Function to run after getting specific subject data dicionary to add to ArchivesSpace'

def addSubject(data_obj):
	'Adds new Subject to ArchivesSpace'
	
	try:
		response = aspace.post('/subjects', data_obj)
		return response

	except:
		pass


'Run functions to add missing subjects'

def getDataAndAddGenreSubject(sub_obj):
	sub_dict = getDataDict_sgenre(sub_obj)
	added_subject = addSubject(sub_dict)

	return added_subject


def getDataAndAddTopSubject(sub_obj):
	sub_dict = getDataDict_stop(sub_obj)
	added_subject = addSubject(sub_dict)

	return added_subject


def getDataAndAddGeoSubject(sub_obj):
	sub_dict = getDataDict_sgeo(sub_obj)
	added_subject = addSubject(sub_dict)

	return added_subject


print('Adding genre subjects')
for sub in genre_subs:
	added = getDataAndAddGenreSubject(sub)
	print(added)
print('Done adding genre subjects')

print('Adding top subjects')
for sub in top_subs:
	added = getDataAndAddTopSubject(sub)
	print(added)
print('Done adding top subjects')

print('Adding geo subs')
for sub in geo_subs:
	added = getDataAndAddGeoSubject(sub)
	print(added)
print('Done adding geo subs')
