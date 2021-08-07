import asyncio
import argparse
from time import ctime
from aiohttp import ClientSession, ClientTimeout, ClientConnectorCertificateError

async def fetch(sem, domain, session):
    async with sem:
        print(f"Checking: {domain}")
        try:
            async with session.get(f"http://{domain}", timeout=timeout) as response:
                asyncio.sleep(0.1)
                if response.status == 200:
                    print(f"\033[1;32mDomain {domain} is accessible\033[0m")
                    responding_domains.append(domain)
                    with open(f'./output/{investigated_domain}-responding.txt', 'a') as f:
                        f.write(f"{domain}\n")

                return await response.read()

        except ClientConnectorCertificateError as e:
            try:
                async with session.get(f"http://{domain}", timeout=timeout, ssl=False) as response:
                    asyncio.sleep(0.1)
                    if response.status == 200:
                        print(f"\033[1;31mDomain {domain} is accessible\033[0m")
                        responding_domains.append(domain)
                        with open(f'./output/{investigated_domain}-responding.txt', 'a') as f:
                            f.write(f"{domain}\t\t\tUntrusted Certificate\n")

                    return await response.read()
            except:
                return(None)
                
        except:
            return(None)


async def run():
    tasks = []
    # create instance of Semaphore
    sem = asyncio.Semaphore(batch)

    # Create client session that will ensure we dont open new connection
    # per each request.
    async with ClientSession() as session:
        for domain in domains_to_check:
            # pass Semaphore and session to every GET request
            tasks.append(fetch(sem, domain, session))

        responses = await asyncio.gather(*tasks, return_exceptions=True)

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
    try:
        loop.run_until_complete(run())
    finally:
        loop.close()

    t1 = ctime()
    print(f"\n\n{len(responding_domains)} out of {len(domains_to_check)} domains have responded.")
    print(f"Started at: {t0}\nFinished at:{t1}")
