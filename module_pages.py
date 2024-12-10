import aiohttp
import asyncio
from aiohttp import ClientTimeout
import subprocess
import requests
import re
from xml.etree import ElementTree

def robots(domain):
    robots_url = f"https://{domain}/robots.txt"
    try:
        response = requests.get(robots_url, timeout=10)
        response.raise_for_status()  # Raise HTTPError if the status is 4xx/5xx
        robots_content = response.text

        # Regular expression to extract URLs
        urls = re.findall(r'(https?://[^\s]+)', robots_content)
        non_sitemap_urls = [url for url in urls if 'sitemap' not in url.lower()]
        return non_sitemap_urls
    except requests.exceptions.RequestException as e:
        print(f"[Error] Could not fetch robots.txt from {domain}: {e}")
        return []

def fetch_robots_txt(domain):
    robots_url = f"https://{domain}/robots.txt"
    try:
        response = requests.get(robots_url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"[Error] Could not fetch robots.txt from {domain}: {e}")
        return ""

def extract_sitemaps_from_robots(robots_txt):
    return re.findall(r'Sitemap:\s*(https?://\S+)', robots_txt)


def guess_sitemaps(domain):
    common_sitemap_paths = [
        "sitemap.xml",
        "sitemap_index.xml",
        "sitemap/sitemap.xml",
        "sitemap-main.xml"
    ]

    return [f"https://{domain}/{path}" for path in common_sitemap_paths]


def fetch_sitemap(sitemap_url):
    try:
        response = requests.get(sitemap_url, timeout=10)
        response.raise_for_status()
        # Parse XML to extract URLs
        tree = ElementTree.fromstring(response.content)
        urls = [elem.text for elem in tree.iter() if elem.tag.endswith("loc")]
        return urls
    except requests.exceptions.RequestException as e:
        print(f"[Error] Could not fetch sitemap {sitemap_url}")
        return []
    except ElementTree.ParseError as e:
        print(f"[Error] Could not parse sitemap (suspect its not real) {sitemap_url}")
        return []


def get_all_sitemap_urls(domain):
    robots_txt = fetch_robots_txt(domain)
    sitemap_urls = extract_sitemaps_from_robots(robots_txt)

    if not sitemap_urls:
        sitemap_urls = guess_sitemaps(domain)

    all_urls = []
    for sitemap_url in sitemap_urls:
        urls = fetch_sitemap(sitemap_url)
        all_urls.extend(urls)

    return all_urls

async def check_page(session, url, verbose, no_found_size, no_found_text, no_found_size_tol):
    if verbose:
        print(f"[Info][Page] Checking {url}")
    try:
        async with session.get(url) as response:
            # 200 being returned doesn't mean there is a page. So we can do some additional checks
            if response.status == 200:
                # If the user has provided a general length of a page that is blank we can check + or - 5
                if no_found_size > 0:
                    headers = response.headers
                    content_length = headers.get('Content-Length')
                    if content_length:
                        content_length = int(content_length)
                        if verbose:
                            print(f"[Info]Page size: {content_length}")
                        if abs(content_length - no_found_size) <= int(no_found_size_tol):
                            if verbose:
                                print(f"[Info][Page] {url} not found according to content length check.")
                        else:
                            return url
                # If the user has provided a key string that is present in all no found pages, we can test for this
                elif no_found_text != "":
                    content = await response.text()
                    if no_found_text in content:
                        if verbose:
                            print(f"[Info][Page] {url} not found according to string matching.")
                    else:
                        return url
                else:
                    # User has not provided a content length or a string check, so assuming returning a 200 is correct
                    return url
    except Exception as e:
        pass  # Ignore errors (e.g., DNS resolution errors)
    return None


async def enumerate_pages(dictionary_path, domain, verbose, no_found_size, no_found_text, no_found_size_tol,concurrency=5):
    with open(dictionary_path, "r") as file:
        url_keywords = [line.strip() for line in file if line.strip()]

    found_subdomains = []
    timeout = ClientTimeout(total=10)

    # Create a session with aiohttp
    async with aiohttp.ClientSession(timeout=timeout) as session:
        # Semaphore to control concurrency
        sem = asyncio.Semaphore(concurrency)

        # Define a task for each subdomain
        async def sem_task(url):
            async with sem:
                result = await check_page(session, url, verbose, no_found_size, no_found_text, no_found_size_tol)
                if result:
                    found_subdomains.append(result)

        # Create tasks for all dictionary keywords
        tasks = []
        for keyword in url_keywords:
            page_url = f"https://{domain}/{keyword}"
            tasks.append(sem_task(page_url))

        # Run all tasks
        await asyncio.gather(*tasks)

    return found_subdomains


def run_page_enumeration(dictionary_path, domain, verbose, no_found_size, no_found_text, no_found_size_tol):
    found_pages = asyncio.run(enumerate_pages(dictionary_path, domain, verbose, no_found_size, no_found_text, no_found_size_tol))
    if verbose:
        for page in found_pages:
            print(f"[Info] Found Page :{page}")
    return found_pages
