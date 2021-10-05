import requests
import os
import json

def get(api_url: str):
    headers = {"Accept": "application/json"}
    url = base_url + api_url
    try:
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            return(response.json())
        else:
            print(f"Error: {response.json()['errorMessage']}")
    except:
        print("Error: Failed to get response")
        return (None)


def post(api_url: str, data: dict):
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    url = base_url + api_url
    try:
        response = requests.post(url=url, headers=headers, data=json.dumps(data))
        if response.status_code == 200 or response.status_code == 201:
            return(response.json())
        elif response.status_code == 204:
            return("OK")
        else:
            print(f"Error: {response.json()['errorMessage']}")
    except:
        print("Error: Failed to get response")
        return (None)


def get_label_id(label_name: str):
    label_list = get(f'groups.json?aid={aid}')['groups']
    for label in label_list:
        if label['name'] == label_name:
            return(label['groupId'])
    print(f"Error: Label {label_name} was not found.")
    raise ValueError(f"Label {label_name} was not found.")


def has_internal_dns_servers(networkProbeId: str, dns_interest_list: list) -> bool:
    """
    This function will fetch the DNS servers of each Probe, and compare it to the
    list of internal DNS servers.
    If the probe includes an internal DNS server - it will return "True".
    If the probe doesn't includes an internal DNS server - it will return "False".
    """
    network_probe_details = get(f"endpoint-data/network-topology/{networkProbeId}?aid={aid}&format=json')['networkProbes']")['networkProbes']
    dns_server_list = network_probe_details[0]['networkProfile']['dnsServers']
    if any(item in dns_server_list for item in dns_interest_list):
        return(True)
    else:
        return(False)


try:
    token = os.environ.get('TE_TOKEN')
    user = os.environ.get('TE_USER')
except:
    print("Error: Missing ThousandEyes User/Token...")

################################################################
#                         User Inputs                          # 
################################################################

aid = 12345
interval = "5m"
dns_interest_list = ["172.28.0.1", "172.28.0.2", 
                    "172.31.0.1", "172.31.0.2",
                    "172.19.0.1", "172.19.0.2",
                    "172.20.201.1", "172.20.201.2"]
connected_label_name = "API_TEST1"

################################################################

base_url = f"http://{user}:{token}@api.thousandeyes.com/v6/"
network_probe_list = get(f'endpoint-data/network-topology.json?window={interval}&aid={aid}')['networkProbes']
connected_label_id = get_label_id(connected_label_name)
agent_list_checked = []
agent_list_to_label = []

# Check the probes for internal DNS servers
for network_probe in network_probe_list:
    if network_probe['agentId'] not in agent_list_checked:
        agent_list_checked.append(network_probe['agentId'])
        if has_internal_dns_servers(network_probe['networkProbeId'], dns_interest_list):
            agent_list_to_label.append(network_probe['agentId'])

# Craft the payload
agent_list_to_label_payload = []
for agent in agent_list_to_label:
    agent_list_to_label_payload.append({"agentId": agent})

label_update_payload = {
	"name": connected_label_name,
	"endpointAgents": agent_list_to_label_payload
}

# Update labels
post(f"groups/{connected_label_id}/update.json?aid={aid}", label_update_payload)

# TODO: Handle a situation where the list is empty - the API call will return an error.
