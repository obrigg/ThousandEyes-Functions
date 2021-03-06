import asyncio
import argparse
from time import ctime
from aiohttp import ClientSession, ClientTimeout, ClientConnectorCertificateError

async def fetch(domain, session):
    print(f"Checking: {domain}")
    try:
        async with session.get(f"http://{domain}", timeout=timeout) as response:
            if response.status == 200:
                print(f"\033[1;32mDomain {domain} is accessible\033[0m")
                responding_domains.append(domain)
                with open(f'./output/{investigated_domain}-responding.txt', 'a') as f:
                    f.write(f"{domain}\n")

            return await response.read()

    except ClientConnectorCertificateError as e:
        async with session.get(f"http://{domain}", timeout=timeout, ssl=False) as response:
            if response.status == 200:
                print(f"\033[1;31mDomain {domain} is accessible\033[0m")
                responding_domains.append(domain)
                with open(f'./output/{investigated_domain}-responding.txt', 'a') as f:
                    f.write(f"{domain}\t\t\tUntrusted Certificate\n")

            return await response.read()

    except:
        return(None)


async def bound_fetch(sem, domain, session):
    # Getter function with semaphore.
    async with sem:
        await fetch(domain, session)


async def run():
    tasks = []
    # create instance of Semaphore
    sem = asyncio.Semaphore(batch)

    # Create client session that will ensure we dont open new connection
    # per each request.
    async with ClientSession() as session:
        for domain in domains_to_check:
            # pass Semaphore and session to every GET request
            task = asyncio.ensure_future(bound_fetch(sem, domain, session))
            tasks.append(task)

        responses = asyncio.gather(*tasks)
        await responses

if __name__ == '__main__':

    # Getting a domain to query, either from an argument, a file,  or from user's input
    parser = argparse.ArgumentParser(description='ThousandEyes URL checker')
    parser.add_argument('--file', help="file with domains to investigate", type=str)
    args = parser.parse_args()

    if args.file is not None:
        filename = args.file
    else: 
        filename = input("Kindly provide the path/filename for a domain list: ")
    with open(filename, 'r') as f:
        domains_to_check = f.read().splitlines()

    investigated_domain = filename[filename.rfind("/")+1 : filename.rfind(".txt")]
    responding_domains = []
    batch = 25
    timeout = ClientTimeout(total=5)
    t0 = ctime()

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run())
    loop.run_until_complete(future)

    t1 = ctime()
    print(f"\n\n{len(responding_domains)} out of {len(domains_to_check)} domains have responded.")
    print(f"Started at: {t0}\nFinished at:{t1}")
