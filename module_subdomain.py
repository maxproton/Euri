import aiohttp
import asyncio
from aiohttp import ClientTimeout
import subprocess
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def get_ns_records(domain):
    try:
        # Run nslookup to get name servers (NS records)
        result = subprocess.run(['nslookup', '-type=NS', domain], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        # Extract NS records from the output
        ns_records = []
        for line in output.splitlines():
            if 'nameserver' in line:
                ns_records.append(line.split()[-1])

        return ns_records
    except Exception as e:
        print(f"[Error] {e}")
        return []


def find_subdomains_with_nslookup(domain):
    ns_records = get_ns_records(domain)
    subdomains = set()

    for ns in ns_records:
        # Run nslookup again to query each nameserver for subdomains
        try:
            result = subprocess.run(['nslookup', domain, ns], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout.decode('utf-8')

            # Check the output for potential subdomains (e.g., those pointing to a different domain)
            for line in output.splitlines():
                if domain in line and line != domain:
                    subdomains.add(line.split()[0])
        except Exception as e:
            print(f"[Error] querying {ns}: {e}")
    return extract_subdomains(subdomains, domain)

def extract_subdomains(urls, target_domain):
    subdomains = []

    for url in urls:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname if parsed_url.hostname else url

        # Remove any trailing slashes or paths after the domain
        hostname = hostname.split('/')[0]

        # Check if the hostname ends with the target domain
        if hostname.endswith(target_domain):
            # Ensure it's a subdomain by validating the part before the target domain
            prefix = hostname[:-len(target_domain)].rstrip('.')
            if prefix:  # Only add if there's something before the target domain
                hostname = hostname.replace("www.", "")
                if hostname not in subdomains and hostname != target_domain:
                    subdomains.append(hostname)

    return subdomains


def google_search_links(query, api_key, cse_id, start_index=1, num_results=10):
    links = []

    while len(links) < num_results:
        url = f"https://www.googleapis.com/customsearch/v1"
        params = {
            "q": f"site:{query}",
            "key": api_key,
            "cx": cse_id,
            "start": start_index,
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code}, {response.text}")

        data = response.json()

        # Extract links from the search results
        for item in data.get("items", []):
            links.append(item.get("link"))

        # Check if there are more results
        if "nextPage" not in data.get("queries", {}) or len(links) >= num_results:
            break

        # Move to the next page
        start_index += 10

    return extract_subdomains(links[:num_results], query)  # Limit to the requested number of results


async def check_subdomain(session, subdomain_url, verbose):
    if verbose:
        print(f"[Info] Checking {subdomain_url}")
    try:
        async with session.get(subdomain_url) as response:
            if response.status == 200:
                return subdomain_url
    except Exception as e:
        pass  # Ignore errors (e.g., DNS resolution errors)
    return None


async def enumerate_subdomains(dictionary_path, domain, verbose, concurrency=5):
    with open(dictionary_path, "r") as file:
        subdomain_keywords = [line.strip() for line in file if line.strip()]

    found_subdomains = []
    timeout = ClientTimeout(total=10)

    # Create a session with aiohttp
    async with aiohttp.ClientSession(timeout=timeout) as session:
        # Semaphore to control concurrency
        sem = asyncio.Semaphore(concurrency)

        # Define a task for each subdomain
        async def sem_task(subdomain_url):
            async with sem:
                result = await check_subdomain(session, subdomain_url, verbose)
                if result:
                    found_subdomains.append(result)

        # Create tasks for all dictionary keywords
        tasks = []
        for keyword in subdomain_keywords:
            subdomain_url = f"https://{keyword}.{domain}"
            tasks.append(sem_task(subdomain_url))

        # Run all tasks
        await asyncio.gather(*tasks)

    return found_subdomains


def run_subdomain_enumeration(dictionary_path, domain, verbose):
    found_subdomains = asyncio.run(enumerate_subdomains(dictionary_path, domain, verbose))
    if verbose:
        for subdomain in found_subdomains:
            print(f"[Info] Found Subdomain :{subdomain}")
    return found_subdomains

