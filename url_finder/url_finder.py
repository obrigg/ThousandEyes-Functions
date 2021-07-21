import requests
import os
import json
import time
import argparse
from rich.progress import track


def get_all_subdomains(domain: str, last_subdomain=""):

    total_subdomains = []
    isFinished = False

    while not isFinished:
        subdomains = get_more_subdomains(investigated_domain, last_subdomain)
        if subdomains == "Error":
            isFinished = True
        elif subdomains == "429":
            print("Waiting 1 hour and trying again...")
            time.sleep(3600)
        elif len(subdomains) > 0:
            total_subdomains += subdomains
            last_subdomain = subdomains[-1]
            with open(f'./output/{investigated_domain}.txt', 'a') as f:
                for subdomain in subdomains:
                    f.write(f"{subdomain}\n")
            print(f"Gatheres {len(total_subdomains)} so far... last one is: {last_subdomain}")
        #
        if len(subdomains) < 21:
            isFinished = True
    #
    print(f"Gatered {len(total_subdomains)} sub-domains")
    return(total_subdomains)


def get_more_subdomains(domain: str, last_subdomain: str):
    subdomains = []
    if last_subdomain != "":
        url = base_url + domain + f"?offsetName={last_subdomain}"
    else:
        url = base_url + domain
    response = requests.get(url, headers=headers)
    #
    if response.status_code == 200:
        for domain in response.json():
            subdomains.append(domain['name'])
        return(subdomains)
    elif response.status_code == 429:
        print("Receive a 429 status code")
        return("429")
    else:
        print(f"Received an error: {response.status_code} || {response.text}")
        return("Error")


if __name__ == '__main__':
    base_url = "https://investigate.umbrella.com/subdomains/"
    umbrella_token = os.environ.get('UMBRELLA_TOKEN')
    headers = {'Authorization': f'Bearer {umbrella_token}',
                'Accept': 'application/json'}

    # Getting a domain to query, either from an argument, a file,  or from user's input
    parser = argparse.ArgumentParser(description='ThousandEyes & Umbrella URL locator')
    parser.add_argument('--domain', help="domain to investigate", type=str)
    parser.add_argument('--file', help="file with domains to investigate", type=str)
    parser.add_argument('--cont', help="continuing a previous run? True/False", type=bool, default=False)
    args = parser.parse_args()
    if args.file is not None:
        with open(args.file, 'r') as f:
            total_subdomains = f.read().splitlines()
        if args.cont and args.domain is not None:
            investigated_domain = args.domain
            last_subdomain = total_subdomains[-1]
            print(f"Continuing from {last_subdomain}")
            total_subdomains += get_all_subdomains(investigated_domain, last_subdomain)
        print(f"Gatered {len(total_subdomains)} sub-domains")
        #
        if "/" in args.file:
            investigated_domain = args.file[args.file.rfind("/"):args.file.rfind(".txt")]
        else:
            investigated_domain = args.file[:args.file.rfind(".txt")]
    else:
        if args.domain is None:
            investigated_domain = input("Kindly enter the domain you would like to investigate: ")
        else:
            investigated_domain = args.domain
        total_subdomains = get_all_subdomains(investigated_domain)
      