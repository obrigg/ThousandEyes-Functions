import requests
import os
import json
import argparse
from rich.progress import track

def get_more_subdomains(domain: str, last_subdomain: str):
    subdomains = []
    if last_subdomain != "":
        url = base_url + domain + f"?offsetName={last_subdomain}"
    else:
        url = base_url + domain
    response = requests.get(url, headers=headers).json()
    for domain in response:
        subdomains.append(domain['name'])
    return(subdomains)


def check_domain(domain: str):
    print(f"Accessing {domain}")
    try:
        response = requests.get(f"http://{domain}")
        if response.status_code == 200:
            print(f"\033[1;32mDomain {domain} is accessible\033[0m")
            return(domain)
    except:
        pass
    return("")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ThousandEyes & Umbrella URL locator')
    parser.add_argument('--domain', help="domain to investigate", type=str)
    args = parser.parse_args()
    if args.domain is None:
        investigated_domain = input("Kindly enter the domain you would like to investigate: ")
    else:
        investigated_domain = args.domain

    umbrella_token = os.environ.get('UMBRELLA_TOKEN')
    headers = {'Authorization': f'Bearer {umbrella_token}',
                'Accept': 'application/json'}
    base_url = "https://investigate.umbrella.com/subdomains/"

    total_subdomains = []
    responding_domains = []
    isFinished = False
    last_subdomain = ""

    while not isFinished:
        subdomains = get_more_subdomains(investigated_domain, last_subdomain)
        if len(subdomains) < 21:
            isFinished = True
        if len(subdomains) > 0:
            total_subdomains += subdomains
            last_subdomain = subdomains[-1]
            print(f"Gatheres {len(total_subdomains)} so far... last one is: {last_subdomain}")
    #
    print(f"Gatered {len(total_subdomains)} sub-domains")
    print("Let's try accessing them...")

    for step in track(range(len(total_subdomains))):
        if check_domain(total_subdomains[step]) != "":
            responding_domains.append(total_subdomains[step])

    domains = ""
    print("\n\nResponding domains:")
    for domain in responding_domains:
        print(f"\t{domain}")
        domains += domain + "\n"

    with open(f'{investigated_domain}.txt', 'w') as f:
        f.writelines(domains)
