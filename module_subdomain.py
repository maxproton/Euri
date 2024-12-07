import subprocess
import requests
from bs4 import BeautifulSoup

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
        print(f"Error: {e}")
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
            print(f"Error querying {ns}: {e}")

    return subdomains


def duckduckgo_search(query):
    url = "https://html.duckduckgo.com/html/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept': 'application/json text/plain, */*',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'Cors',
        'Sec-Fetch-Site': 'same-site',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }

    # Prepare the payload with the search query
    payload = {'q': query}

    # Send POST request with the search query
    response = requests.post(url, params=payload, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Extract links from the search result
    links = []

    for result in soup.find_all('a', class_='result__a'):
        link = result.get('href')
        if link:
            links.append(link)

    return links
