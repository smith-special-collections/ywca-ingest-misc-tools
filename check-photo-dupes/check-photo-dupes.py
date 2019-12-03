import csv
import requests


with open('pids.csv', 'r') as fp:
    reader = csv.DictReader(fp)
    for line in reader:
#        print(line['PID'])
        local_id = line['fgs_label_s']
        solr_query = f"http://compass-fedora-stage.fivecolleges.edu:8080/solr/collection1/select?q=mods_identifier_local_s%3A{local_id}+AND+PID%3Asmith%5C%3A*&fl=PID%2Cfgs_label_s&wt=json&indent=true"
        r = requests.get(solr_query)
        query_results = r.json()
        if query_results['response']['numFound'] == 1:
            result_pid = query_results['response']['docs'][0]['PID']
            result_fgs_label_s = query_results['response']['docs'][0]['fgs_label_s']
            print(line['PID'] +','+ line['fgs_label_s'] +','+ result_pid +','+ result_fgs_label_s)
        elif query_results['response']['numFound'] == 0:
            print(line['PID'] +','+ line['fgs_label_s'] +','+ 'MISSING' +','+ 'MISSING')
        elif query_results['response']['numFound'] > 1:
            print(line['PID'] +','+ line['fgs_label_s'] +','+ 'MULTIPLE' +','+ 'MULTIPE')
