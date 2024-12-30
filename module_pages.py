import random
import string
import aiohttp
import asyncio
from aiohttp import ClientTimeout
import subprocess
import requests
import re
from xml.etree import ElementTree
from bs4 import BeautifulSoup

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

def extract_html_sitemap(domain):
    if "https://" not in domain:
        domain = f"https://{domain}"
    domain = f"{domain}/sitemap"

    try:
        response = requests.get(domain, timeout=10)
        response.raise_for_status()
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        urls = []
        for link in links:
            link_url = link['href']
            if not link_url.startswith('http'):
                link_url = domain + link_url if link_url.startswith('/') else f"{domain}/{link_url}"
            try:
                # Make a HEAD request to get the status code (without downloading the content!)
                link_response = requests.head(link_url, timeout=5)
                link_response.raise_for_status()  # Will raise an exception for 4xx, 5xx errors
                urls.append(link_url)
            except requests.exceptions.RequestException as e:
                print(f"{link_url} is dead")
                # return nothing.
        return urls
    except requests.exceptions.RequestException as e:
        print(f"[Error] Could not fetch sitemap {domain}")
        return []

def get_all_sitemap_urls(domain):
    robots_txt = fetch_robots_txt(domain)
    sitemap_urls = extract_sitemaps_from_robots(robots_txt)
    html_sitemap = extract_html_sitemap(domain)
    if not sitemap_urls:
        sitemap_urls = guess_sitemaps(domain)

    all_urls = []
    for sitemap_url in sitemap_urls:
        urls = fetch_sitemap(sitemap_url)
        all_urls.extend(urls)
    if html_sitemap is not None:
        all_urls.append(html_sitemap)

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

def compare_with_tolerance(val1, val2, val3, tolerance=0.1):
    values = [val1, val2, val3]
    reference = min(values)  # Use the minimum value as the reference

    for value in values:
        if abs(value - reference) > reference * tolerance:
            return False  # If any value is outside the tolerance range, return False

    return True

def get_page_size(domain):
    length = 6
    random_string_one = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    random_string_two = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    random_string_three = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    if "https://" not in domain:
        domain = "https://" + domain

    try:

        response_one = requests.get(domain + "/" + random_string_one, timeout=10)
        if response_one.status_code != 200:
            return "Return status was not 200"
        length_one = len(response_one.text)
        response_two = requests.get(domain + "/" + random_string_two, timeout=10)
        length_two = len(response_two.text)
        response_three = requests.get(domain + "/" + random_string_three, timeout=10)
        length_three = len(response_three.text)

        if compare_with_tolerance(length_one, length_two, length_three):
            value = (length_one + length_two + length_three)/3
            print(f"Use the flag --no-found-size {value}")
            return ""
        else:
            print(f"Unable to establish a sensible size these are the sizes I got back [{domain}/{random_string_one}]{length_one}")
            print(f"[{domain}/{random_string_two}]{length_two}")
            print(f"[{domain}/{random_string_three}]{length_three}")
            print(f"perhaps target some text on the error page and use the flag --no-found-text [text]")
            return ""
    except Exception as e:
        return f"[Error] Could not fetch {domain}: {e}"

def check_pages(dictionary_path, domain, verbose, no_found_size, no_found_text):

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
                        if abs(content_length - no_found_size) <= float(0.1):
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
