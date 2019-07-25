from api_class import scrut_api
import csv
import json
import requests
with open('settings.json') as config:
    config = json.load(config)


# set up connection to Scrutinizer.
client = scrut_api.scrut_api_client(
    hostname=config["hostname"],
    authToken=config["authToken"])

ip_list = []
# open up CSV file and create a list of IP addresses.
with open('iplist.csv', mode='r') as csv_file:
    list_of_ips = csv.reader(csv_file, delimiter=',')
    for ip in list_of_ips:
        ip_list.append(ip[0])


def host_index(host):
    index_json = {
        "rm": "quick_search",
        "view": "quick_search",
        "action": "check_hosts",
        "data_requested": json.dumps({"hosts": ["{}".format(host)]}),
        "authToken": client.authToken

    }
    return index_json


ip_to_search = host_index(ip_list[0])

# print(ip_to_search)
data_back = requests.get(
    "https://scrutinizer.plxr.local/fcgi/scrut_fcgi.fcgi", params=ip_to_search, verify=False)

host_returned = data_back.json()


def make_requests():
    data_returned = []
    for ip in ip_list:
        params = host_index(ip)
        data_back = requests.get(
            "https://scrutinizer.plxr.local/fcgi/scrut_fcgi.fcgi", params=params, verify=False)
        hosts_returned = data_back.json()
        host_info = index_data(ip, hosts_returned)
        data_returned.append(host_info)
    return data_returned


def index_data(host_searched, host_returned):
    object_returned = {
        'results': {
            'host_searched':host_searched,
            'just_exporters': [],
            'all_results': [],
            'aggregate_connections': 0
        }
    }
    for ip in host_returned['rows']:
        exporter_ip = ip[0]['label']
        first_seen = ip[1]['label']
        last_seen = ip[2]['label']
        connection = ip[3]['label']
        all_results = {
            'exporter': exporter_ip,
            'first_time': first_seen,
            'last_time': last_seen,
            'connections': connection
         }

        object_returned["results"]['just_exporters'].append(exporter_ip)
        object_returned["results"]['all_results'].append(all_results)
        object_returned["results"]['aggregate_connections'] += int(connection)
    return object_returned


host_info = make_requests()

for host_searched in host_info:
    ip_searched = host_searched['results']['host_searched']
    total_exporters = len(host_searched['results']['just_exporters'])
    aggregates = host_searched['results']['aggregate_connections']
    if total_exporters > 0:
        print("{} was found comminicating on {} exporters. The total ammount of connections accross all devices was {}".format(ip_searched, total_exporters, aggregates))
    else:
        print("{} was not found in the host index search.".format(ip_searched))