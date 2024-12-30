
import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import requests
import io
from urllib.parse import urlparse
import re

social_media_links = {
    "facebook.com": "Facebook",
    "twitter.com": "Twitter",
    "instagram.com": "Instagram",
    "linkedin.com": "LinkedIn",
    "youtube.com": "YouTube",
    "tiktok.com": "TikTok",
    "pinterest.com": "Pinterest",
    "snapchat.com": "Snapchat",
    "reddit.com": "Reddit",
    "tumblr.com": "Tumblr",
    "twitch.tv": "Twitch",
    "discord.com": "Discord",
    "medium.com": "Medium",
    "vimeo.com": "Vimeo",
    "whatsapp.com": "WhatsApp",
    "wechat.com": "WeChat",
    "itch.io": "Itch"
}

repo = {
    "https://github.com": "GitHub - A web-based platform for version control and collaborative software development, built on Git.",
    "https://gitlab.com": "GitLab - A web-based DevOps lifecycle tool that provides Git repository management and CI/CD pipelines.",
    "https://bitbucket.org": "Bitbucket - A Git-based source control platform with built-in CI/CD by Atlassian.",
    "https://sourceforge.net": "SourceForge - A web-based service for managing and hosting open-source and business projects.",
    "https://gitea.io": "Gitea - A lightweight and self-hosted Git service written in Go.",
    "https://launchpad.net": "Launchpad - A platform by Canonical for open-source project hosting and management, including Bazaar repositories.",
    "https://savannah.gnu.org": "GNU Savannah - A central place for development, maintenance, and distribution of official GNU software and documentation.",
    "https://pagure.io": "Pagure - A lightweight, full-featured, self-hosting Git source control service.",
    "https://rhodecode.com": "RhodeCode - A source code management tool supporting Git, Mercurial, and SVN, for enterprise-level deployments.",
    "https://sourcehut.org": "SourceHut - A simple, lightweight, and fast source control and collaboration platform.",
    "https://gerrit.googlesource.com": "Gerrit - A web-based code review and project management platform for Git repositories.",
    "https://azure.microsoft.com/en-us/services/devops/repos": "Azure DevOps Repos - A set of version control tools by Microsoft integrated into Azure DevOps.",
    "https://codeberg.org": "Codeberg - A free and open-source hosting solution for Git repositories, focused on privacy and transparency.",
    "https://fossil-scm.org": "Fossil - A distributed version control system with built-in bug tracking and wiki support.",
    "https://phabricator.com": "Phabricator - A suite of open-source tools for collaborative development, including source control.",
    "https://bazaar.canonical.com": "Bazaar (Bazaar-NG) - A version control system focused on flexibility and integration by Canonical.",
    "https://tfs.visualstudio.com": "TFS/Azure DevOps Server - Microsoft's on-premise version control and DevOps tool with Git and TFVC support.",
    "https://perforce.com": "Perforce - A proprietary source control management system used for handling large-scale projects.",
    "https://clearcase.com": "ClearCase - An enterprise-grade version control and build software system by IBM."
}
def get_content(domain):
    if "https://" not in domain:
        domain = "https://" + domain
    try:
        response = requests.get(domain, timeout=5)
        if response.status_code == 200:
            return response.text
        if response.status_code == 403:
            return "403"
        if response.status_code == 404:
            return "404"
        if response.status_code == 500:
            return "500"
    except requests.RequestException as e:
        return "0"

def convert_to_degrees(value):
    """Convert GPS coordinates from EXIF format to degrees."""
    def rational_to_float(rational):
        return rational[0] / rational[1] if isinstance(rational, tuple) else float(rational)

    d = rational_to_float(value[0])
    m = rational_to_float(value[1])
    s = rational_to_float(value[2])
    return d + (m / 60.0) + (s / 3600.0)
def extract_image_direct(img_url):
    images = {}
    metadata = {}
    try:
        response = requests.get(img_url, timeout=10)
        response.raise_for_status()
        image_content = io.BytesIO(response.content)
        image = Image.open(image_content)
        metadata['url'] = img_url
        metadata['format'] = image.format
        metadata['size'] = image.size

        exif_data = image._getexif()
        if exif_data:
            exif = {TAGS.get(tag, tag): value for tag, value in exif_data.items()}

            # Camera info
            metadata['camera_info'] = {
                'Make': exif.get('Make'),
                'Model': exif.get('Model'),
            }

            # GPS Info
            gps_info = exif.get('GPSInfo')
            if gps_info:
                gps_parsed = {GPSTAGS.get(key, key): val for key, val in gps_info.items()}
                if 'GPSLatitude' in gps_parsed and 'GPSLongitude' in gps_parsed:
                    latitude = convert_to_degrees(gps_parsed['GPSLatitude'])
                    longitude = convert_to_degrees(gps_parsed['GPSLongitude'])
                    latitude_ref = gps_parsed.get('GPSLatitudeRef', 'N')
                    longitude_ref = gps_parsed.get('GPSLongitudeRef', 'E')

                    if latitude_ref == 'S': latitude = -latitude
                    if longitude_ref == 'W': longitude = -longitude

                    metadata['location'] = f"{latitude}, {longitude}"

    except Exception as e:
        print(f"[Error] Failed to get metadata for image {img_url}: {e}")
    images[img_url] = metadata
    images[img_url] = metadata
    return images

def extract_image_metadata(html_content, domain, link_images, verbose):
    images = {}
    soup = BeautifulSoup(html_content, 'html.parser')
    image_urls = [img.get('src') for img in soup.find_all('img') if img.get('src')]
    image_urls.append(link_images)

    for img_url in image_urls:
        metadata = {}
        img_url = urljoin(domain, img_url)  # Construct absolute URL

        try:
            response = requests.get(img_url, timeout=10)
            response.raise_for_status()
            image_content = io.BytesIO(response.content)
            image = Image.open(image_content)
            metadata['url'] = img_url
            metadata['format'] = image.format
            metadata['size'] = image.size

            exif_data = image._getexif()
            if exif_data:
                exif = {TAGS.get(tag, tag): value for tag, value in exif_data.items()}

                # Camera info
                metadata['camera_info'] = {
                    'Make': exif.get('Make'),
                    'Model': exif.get('Model'),
                }

                # GPS Info
                gps_info = exif.get('GPSInfo')
                if gps_info:
                    def convert_to_degrees(value):
                        d, m, s = value
                        return d[0] / d[1] + (m[0] / m[1]) / 60 + (s[0] / s[1]) / 3600

                    if 2 in gps_info and 4 in gps_info:
                        metadata['location'] = f"{gps_info[1]} {gps_info[2]}, {gps_info[3]}{gps_info[4]}"
                    else:
                        metadata['location'] = exif.get('GPSInfo')
            images[img_url] = metadata
        except Exception as e:
            if verbose:
                print(f"[Error] Failed to get metadata for image {img_url}: {e}")


    return images
def check_link_for_image(link):
    image_extensions = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"]
    if any(link.lower().endswith(ext) for ext in image_extensions):
        return True
    return False


def extract_image_metadata_old(html_content, domain):
    images = {}
    soup = BeautifulSoup(html_content, 'html.parser')
    image_urls = [img.get('src') for img in soup.find_all('img') if img.get('src')]

    for img_url in image_urls:
        metadata = {}
        domain = os.path.dirname(domain)
        if "/" not in img_url:
            img_url = "/" + img_url
        if domain not in img_url:
            img_url = domain + img_url
        try:
            response = requests.get(img_url, timeout=10)
            response.raise_for_status()
            image_content = io.BytesIO(response.content)
            image = Image.open(image_content)
            metadata['url'] = img_url
            metadata['format'] = image.format
            metadata['size'] = image.size

            exif_data = image._getexif()
            if exif_data:
                gps_info = exif.get('GPSInfo')
                if gps_info:
                    def convert_to_degrees(value):
                        d, m, s = value
                        return d[0] / d[1] + (m[0] / m[1]) / 60 + (s[0] / s[1]) / 3600

                    latitude = convert_to_degrees(gps_info[2]) if 2 in gps_info else None
                    longitude = convert_to_degrees(gps_info[4]) if 4 in gps_info else None

                    if latitude and longitude:
                        latitude_ref = gps_info[1]
                        longitude_ref = gps_info[3]

                        # Adjust latitude and longitude based on reference
                        if latitude_ref == 'S': latitude = -latitude
                        if longitude_ref == 'W': longitude = -longitude

                        metadata['location'] = f"{latitude}, {longitude}"

                exif = {TAGS.get(tag, tag): value for tag, value in exif_data.items() if tag in TAGS}

                # Include camera
                metadata['camera_info'] = {
                    'Make': exif.get('Make'),
                    'Model': exif.get('Model'),
                }

                # Extract GPS Info if present
                if 'GPS GPSLatitude' in metadata and 'GPS GPSLongitude' in metadata:
                    latitude = exif.get('GPS GPSLatitude')
                    longitude = exif.get('GPS GPSLongitude')
                    metadata['location'] = f"{latitude} - {longitude}"

        except Exception as e:
            #dont do anything yet
            print(f"[Error] Error getting image {img_url}")
        images[img_url] = metadata

    return images

def link_harvest(domain: str, html_content: str, verbose: bool):
    live_links = []
    access_denied = []
    dead_links = []
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all the <a> tags with href attributes
    links = soup.find_all('a', href=True)
    if "http" not in domain:
        domain = f"https://{domain}"

    for link in links:
        link_url = link['href']

        if not link_url.startswith('http'):
            link_url = domain + link_url if link_url.startswith('/') else f"{domain}/{link_url}"

        try:
            # Make a HEAD request to get the status code (without downloading the content!)
            link_response = requests.head(link_url, timeout=5)
            link_response.raise_for_status()  # Will raise an exception for 4xx, 5xx errors

            if link_response.status_code == 200:
                if link_url not in live_links:
                    live_links.append(link_url)
                    if verbose:
                        print(f"[Info][Link] Link discovered and alive {link_url}")
            if link_response.status_code == 403:
                if link_url not in access_denied:
                    access_denied.append(link_url)
                    if verbose:
                        print(f"[Info][Link] Link discovered with a 403 {link_url}")
            if link_response.status_code == 302:
                if link_url not in live_links:
                    live_links.append(link_url)
                    if verbose:
                        print(f"[Info][Link] Link discovered alive but with a 301 {link_url}")
        except requests.exceptions.RequestException as e:
            if link_url not in dead_links:
                dead_links.append(link_url)
                if verbose:
                    print(f"[Info][Link] Dead link located {link_url}")

    return_items = {
        'live': live_links,
        '403': access_denied,
        'dead': dead_links
    }

    return return_items

def find_social_media(links):
    found_links = {}
    for link in links['live']:
        for base_url, platform in social_media_links.items():
            if base_url in link:
                found_links[link] = platform

    return found_links

def find_github_references(links):
    found_links = {}
    for link in links['live']:
        for base_url, base_description in repo.items():
            if base_url in link:
                found_links[link] = base_description

    return found_links

def remove_html(content):
    soup = BeautifulSoup(content, "html.parser")

    # Remove all script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()

    # Extract the visible text
    visible_text = soup.get_text()

    # Clean up extra spaces, newlines, and tabs
    clean_text = "\n".join(line.strip() for line in visible_text.splitlines() if line.strip())

    return clean_text

def extract_ip_addresses(text):
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    ip_addresses = re.findall(ip_pattern, text)

    valid_ips = [ip for ip in ip_addresses if all(0 <= int(octet) <= 255 for octet in ip.split('.'))]

    return valid_ips


def extract_comments_from_html(html_content):

    html_comment_pattern = r'<!--(.*?)-->'
    # js_comment_pattern = r'//.*?(?=\n|$)'
    html_comments = re.findall(html_comment_pattern, html_content, re.DOTALL)
    # js_comments = re.findall(js_comment_pattern, html_content)
    all_comments = html_comments #+ js_comments

    comments = []
    for cmt in all_comments:
        if cmt != "":
            comments.append(cmt
                            )
    return comments