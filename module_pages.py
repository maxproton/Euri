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
        disallowed = re.findall(r'Disallow:\s*(/\S*)', robots_content)
        non_sitemap_urls = [url for url in urls if 'sitemap' not in url.lower()]
        for disallow in disallowed:
            non_sitemap_urls.append(f"https://{domain}{disallow}")
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

def get_urls_from_file(file_path):

    urls = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Strip whitespace and skip empty lines
                url = line.strip()
                if url:
                    urls.append(url)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_path}")
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")

    return urls
def check_pages(dictionary_path, domain, verbose, no_found_size, no_found_text, no_found_size_tol):

    url_keywords = get_urls_from_file(dictionary_path)
    existing_pages = []

    for page in url_keywords:
        url = f"https://{domain}/{page.strip()}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code in (200, 401):
                if no_found_size > 0:
                    headers = response.headers
                    content_length = headers.get('Content-Length')
                    if content_length:
                        content_length = int(content_length)
                        if verbose:
                            print(f"[Info] Page size: {content_length}")
                        if abs(content_length - no_found_size) <= int(no_found_size_tol):
                            if verbose:
                                print(f"[Info][Page] {url} not found according to content length check.")
                        else:
                            existing_pages.append(url)
                # If the user has provided a key string that is present in all no found pages, we can test for this
                elif no_found_text != "":
                    content = response.text
                    if no_found_text in content:
                        if verbose:
                            print(f"[Info][Page] {url} not found according to string matching.")
                    else:
                        existing_pages.append(url)
                else:
                    # User has not provided a content length or a string check, so assuming returning a 200 is correct
                    existing_pages.append(url)
            else:
                if verbose:
                    print(f"[Info][URL NOT FOUND] {url} ({response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"[Error] Could not fetch {url}: {e}")

    return existing_pages
