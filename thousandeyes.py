import requests, os, json

################################################################
#                       Basic functions                        # 
################################################################

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


################################################################
#                   Cloud/Enterprise Tests                     # 
################################################################


def get_test_list():
    test_list = get("tests.json")['test']
    return(test_list)


def get_test_details(testId: str):
    test_details = get(f"tests/{testId}.json")['test'][0]
    return(test_details)


def create_test(testType: str, testName: str, data: dict):
    """
    testTypes:agent-to-agent, agent-to-server, http-server, page-load, transactions, web-transactions,
    ftp-server, dns-trace, dns-server, dns-dnssec, dnsp-domain, dnsp-server, sip-server. voice (RTP Stream)

    Data example:
    {
        "agents": [ 
            {"agentId": 113},
            {"agentId": 114},
            {"agentId": 115}
            ], 
        "testName": "API test",
        "server": "www.thousandeyes.com",
        "interval": 300
    }
    """
    test_details = post(f"tests/{testType}/new.json", data)['test'][0]
    return(test_details)


def update_test(testType:str, testId: str, data: dict):
    test_details = post(f"tests/{testType}/{testId}/update", data)['test'][0]
    return(test_details)


def delete_test(testType:str, testId: str):
    status = post(f"tests/{testType}/{testId}/delete", "")
    print(status)


def enable_test(testType:str, testId: str):
    data = {"enabled": 1}
    test_details = post(f"tests/{testType}/{testId}/update", data)['test'][0]
    return(test_details)


def disable_test(testType:str, testId: str):
    data = {"enabled": 0}
    test_details = post(f"tests/{testType}/{testId}/update", data)['test'][0]
    return(test_details)


################################################################
#                       Instant Tests                          # 
################################################################

def create_instant_test(testType: str, data: dict):
    """
    testTypes:agent-to-agent, agent-to-server, http-server, page-load, transactions, web-transactions,
    ftp-server, dns-trace, dns-server, dns-dnssec, dnsp-domain, dnsp-server, sip-server. voice (RTP Stream)

    Data example:
    {
        "agents": [ 
            {"agentId": 113},
            {"agentId": 114},
            {"agentId": 115}
            ], 
        "testName": "API Instant test",
        "server": "www.thousandeyes.com"
    }
    """
    instant_test_details = post(f"instant/{testType}", data)
    return(instant_test_details['test'][0])


################################################################
#                       Endpoint Tests                         # 
################################################################


def get_endpoint_test_list():
    endpoint_test_list = get("endpoint-tests.json")['endpointTest']
    return(endpoint_test_list)


def get_endpoint_test_list_by_type(test_type: str):
    endpoint_test_list = get(f"endpoint-tests/{test_type}.json")['endpointTest']
    return(endpoint_test_list)


def get_endpoint_test_details(testId: str):
    endpoint_test_details = get(f"endpoint-tests/{testId}.json")['endpointTest']
    return(endpoint_test_details)


# TODO: Create an endpoint test


################################################################
#               Setting up the environment                     # 
################################################################

try:
    token = os.environ.get('TE_TOKEN')
    user = os.environ.get('TE_USER')
except:
    print("Error: Missing ThousandEyes User/Token...")

base_url = f"http://{user}:{token}@api.thousandeyes.com/v6/"