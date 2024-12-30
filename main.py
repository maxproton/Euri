import csv

import argparse
import banner
import module_framework
import module_headers
import module_ssl
import ports
import json
import module_dns
import module_subdomain
import module_ssl
import module_headers
import module_email
import module_pages
import module_report
import module_config
import module_content_analysis
from dotenv import load_dotenv
import os
import hashlib

domain = ""
dns_records = {}
sub_domains = {}
pages = []
ssl_certificates = {}
headers = {}
cookies = {}
email_addresses = []
technology_stack = {}
config_files = {}
git_repo = {}
images = {}
links = {}
social = {}
repo = {}
word_count = 0
dictionary = {}
content_hash = ""
ip_addresses = []
comments = []

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process a file and perform operations on its lines.")
    parser.add_argument("-d", "--domain", type=str, required=True, help="Initial Domain")
    parser.add_argument("-s", "--suppress-less-common-dns", action="store_true",  help="Suppress less common DNS record checks")
    parser.add_argument("-v", "--verbose", action="store_true", help="Shows you everything!")
    parser.add_argument("-g", "--no-google", action="store_true", help="Do not perform google searches")
    parser.add_argument("-aa", "--no-header-check", action="store_true", help="Do not analyse the resultant header for clues to the framework")
    parser.add_argument("-bb", "--no-subdomain-brute", action="store_true", help="Do not perform a subdomain brute force")
    parser.add_argument("-te", "--no-found-size", type=int, required=False, help="Some sites return 200 with custom error page, use this to specify the size of the error page")
    parser.add_argument("-ta", "--no-found-text", type=str, required=False, help="Some sites return 200 with custom error page, use this to specify the text to look for in an error page")
    parser.add_argument("-ba", "--check-page", action="store_true", help="Use this to find out the average page size of an error page")
    parser.add_argument("-bc", "--exif", action="store_true",
                        help="Use this to just check imags on the system for exif data")
    parser.add_argument("-bd", "--direct", action="store_true",
                        help="Use this to just check imags on the system for exif data directly")
    return parser.parse_args()

if __name__ == '__main__':
    print(banner.banner)
    args = parse_arguments()
    load_dotenv()

    if args.check_page:
        if args.domain is None:
            print(f"[Error] no Domain provided use --domain [domain]")
            exit(1)
        else:
            print(module_pages.get_page_size(args.domain))
        exit(1)

    if args.exif:
        if args.domain is None:
            print(f"[Error] no Domain provided use --domain [domain]")
            exit(1)
        elif args.direct:
            print(f"[Task] Checking images on {args.domain}")
            images = module_content_analysis.extract_image_direct(args.domain)
            data = {
                'title': f"Euri image report for {args.domain}",
                'heading': f"Target: {args.domain}",
                'images': images,
            }

            report_title = module_report.generate_image_summary(data, args.domain)
            print(f"[Task] Finshed. Report available at {report_title}")
        else:
            # all images and meta data
            print(f"[Task] Checking images on {args.domain}")
            content = module_content_analysis.get_content(args.domain)
            images = module_content_analysis.extract_image_metadata(content, args.domain)
            if args.verbose:
                for image_url, metadata in images.items():
                    print(f"[Info][Images] Image {image_url} contains the following metadata")
                    for metadata_key, metadata_value in metadata.items():
                        print(f"[Info][Images][{image_url}] {metadata_key} : {metadata_value}")
            print(f"[Task] Generating Report..")

            data = {
                'title': f"Euri image report for {args.domain}",
                'heading': f"Target: {args.domain}",
                'images': images,
            }

            report_title = module_report.generate_image_summary(data, args.domain)
            print(f"[Task] Finshed. Report available at {report_title}")
        exit(1)

    # DNS lookup
    print(f"[Task] Performing DNS Lookup for {args.domain}.")
    dns_records = module_dns.dns_enumeration(
        args.domain,
        args.suppress_less_common_dns,
        args.verbose
    )
    if args.verbose:
        print("[Info] DNS RECORDS")
        for type, answer in dns_records.items():
            for record in answer:
                print(f"{type} Record: {record}")

    # Enumerate over the txt records and check they have not put an email address in it
    for type, answer in dns_records.items():
        for record in answer:
            if record == "TXT":
                email_addresses = email_addresses + module_email.extract_emails(answer)

    # Subdomain lookup
    print(f"[Task] Performing non-bruteforce subdomain collection for {args.domain}.")
    dns_subdomains = module_subdomain.find_subdomains_with_nslookup(args.domain)
    google_dorks_subdomain = []
    if not args.no_google:
        print(f"[Task] Performing google search")
        google_dorks_subdomain = module_subdomain.google_search_links(
            args.domain,
             os.getenv("GOOGLE_SEARCH_API_KEY"),
            os.getenv("GOOGLE_SEARCH_ID"),
            1,
            100
        )

    brute_force_subdomains = []
    if not args.no_subdomain_brute:
        print(f"[Task] Performing Subdomain enumberation from dictionary lists/subdomains.txt on {args.domain}.")
        brute_force_subdomains = module_subdomain.run_subdomain_enumeration("lists/subdomains.txt", args.domain, args.verbose)

    sub_domains["new"] = google_dorks_subdomain + dns_subdomains + brute_force_subdomains
    if args.verbose:
        for subdomain in sub_domains["new"]:
            print(f"[Info] {subdomain} Found")


    # SSL Certificate Parsing of main domain
    print(f"[Task] Performing SSL cert analysis.")
    ssl_certificates["main"] = module_ssl.ssl_cert_analysis(args.domain)
    if args.verbose:
        print(f"[Info][SSL] Subject: {ssl_certificates['main']['subject']}")
        print(f"[Info][SSL] Issuer: {ssl_certificates['main']['issuer']}")
        print(f"[Info][SSL] Valid-From: {ssl_certificates['main']['valid_from']}")
        print(f"[Info][SSL] Valid-To: {ssl_certificates['main']['valid_to']}")
    email_addresses = email_addresses + module_email.extract_emails(ssl_certificates['main']['subject'])
    email_addresses = email_addresses + module_email.extract_emails(ssl_certificates['main']['issuer'])

    # Header extraction from main domain
    print(f"[Task] Getting all header values for {args.domain}.")
    headers[args.domain] = module_headers.get_header(args.domain)
    if args.verbose:
        for key, header in headers[args.domain].items():
            print(f"[Info][Header] {key} : {header}")

    # Sometimes emails are stashed in the headers?
    for key, header in headers[args.domain].items():
        email_addresses = email_addresses + module_email.extract_emails(header)

    # Enumerate cookies
    cookies = module_headers.get_cookies(headers[args.domain].items())

    if args.verbose:
        for key, value in cookies.items():
            print(f"[Info][Cookie] {key} : {value}")

    # Check Robots and Sitemap for pages
    print(f"[Task] Collecting pages from available sitemaps {args.domain}.")
    robots = module_pages.robots(args.domain)
    sitemaps = module_pages.get_all_sitemap_urls(args.domain)

    # Enumerate using page file to find pages
    enumeration_list_pages = "lists/pages.txt"
    print(f"[Task] Enumerating pages from list {enumeration_list_pages}.")
    no_found_size = 0
    if args.no_found_size is not None:
        try:
            no_found_size = int(args.no_found_size)
        except Exception:
            no_found_size = 0

    no_found_text = ""
    if args.no_found_text is not None:
        try:
            no_found_text = str(args.no_found_text)
        except Exception:
            no_found_text = ""

    pages = module_pages.check_pages(
        enumeration_list_pages,
        args.domain,
        args.verbose,
        no_found_size,
        no_found_text
    )

    server = {}

    # Check technology stack in headers for hints at the type of server and version number
    print(f"[Task] Checking technology stack.")
    for key, header in headers[args.domain].items():
        if key != "Set-Cookie" and key != "Cookie":
            server.update(module_framework.check_for_server_hinting(header))

    technology_stack['server'] = server
    if args.verbose:
        for type, server_hinting in technology_stack['server'].items():
            print(f"[Info] Server hinting {type} - {server_hinting['version']} - {server_hinting['description']}")

    print(f"[Task] Stealing cookies and putting them in our jar.")
    cookie_stack = []
    for key, value in cookies.items():
        cookie_stack = cookie_stack + module_framework.check_for_cookie_hinting(key)
    technology_stack['language'] = cookie_stack

    if args.verbose:
        for cook in technology_stack['language']:
            print(f"[Info] language : {cook}")

    print(f"[Task] Checking for presents of libraries.")
    library_frameworks = module_framework.find_web_frameworks(args.domain)
    technology_stack['web_technology'] = library_frameworks

    if args.verbose:
        for library in library_frameworks:
            print(f"[Info] {library}")

    # Check for config files
    print(f"[Task] Checking for config files.")
    config_files = module_config.check_for_config_files(args.domain, args.verbose)
    if args.verbose:
        for config_file, config_description in config_files.items():
            print(f"[Info] Found Config file {config_file} - {config_description}")

    # .git and git content
    print(f"[Task] Checking for git repos.")
    git_repo = module_config.get_git(args.domain, args.verbose)
    if args.verbose:
        if git_repo:
            print(f"[Info] Found Git tresure..")
            for name, description in git_repo.items():
                print(f"[Info][GIT] {name} : : {description}")
        else:
            print("[Info] Not git repos found :(")

    # Content Analysis block
    # ----------------------
    print(f"[Task] Starting content analysis.")
    content = module_content_analysis.get_content(args.domain)

    # all links and indexing (interal add external note)
    print(f"[Task] Checking link in content.")
    links = module_content_analysis.link_harvest(args.domain, content, args.verbose)

    if args.verbose:
        for keys, values in links.items():
            if keys == "live":
                for url in values:
                    print(f"[Info][Live] {url}")
            if keys == "dead":
                for url in values:
                    print(f"[Info][Dead] {url}")
            if keys == "403":
                for url in values:
                    print(f"[Info][unauthorised] {url}")

    #establish how many of those links are images
    link_images = {}
    for key, values in links.items():
        if key == "live":
            for value in values:
                if module_content_analysis.check_link_for_image(value):
                    link_images[value] = value

    # all images and meta data
    print(f"[Task] Checking images on {args.domain}")
    images = module_content_analysis.extract_image_metadata(content, args.domain, link_images, args.verbose)
    if args.verbose:
        for image_url, metadata in images.items():
            print(f"[Info][Images] Image {image_url} contains the following metadata")
            for metadata_key, metadata_value in metadata.items():
                print(f"[Info][Images][{image_url}] {metadata_key} : {metadata_value}")

    # social media links
    print(f"[Task] Checking for Social Media links.")
    social = module_content_analysis.find_social_media(links)

    if args.verbose:
        for social_key, social_value in social.items():
            print(f"[Info][Social] Social media link discovered for {social_value}")

    # git references
    print(f"[Task] Checking for Source Control Links.")
    repo = module_content_analysis.find_github_references(links)

    if args.verbose:
        for git_key, git_value in repo.items():
            print(f"[Info][Repo] Found {git_value} : {git_key}")

    # email references
    print(f"[Task] Checking html content for emails")
    email_addresses = email_addresses + module_email.extract_emails(module_content_analysis.remove_html(content))

    if args.verbose:
        print(f"[Info][Email] Count so far: ")
        for email_address in email_addresses:
            print(f"[Info][Email]{email_address}")

    # word count
    words = module_content_analysis.remove_html(content).split()
    word_count = len(words)
    print(f"[Task] Word count complete. There are {word_count}")

    # dictionary generation
    print(f"[Task] Collecting dictionary of words")
    for word in words:
        dictionary[word.lower()] = word
    dictionary = {key: dictionary[key] for key in sorted(dictionary)}

    if args.verbose:
        for word in dictionary.items():
            print(f"[Info][Dictionary] Adding {word} to dictionary")

    # hash value
    content_hash = {
        'SHA512': hashlib.sha512(module_content_analysis.remove_html(content).encode()).hexdigest(),
        'SHA256': hashlib.sha256(module_content_analysis.remove_html(content).encode()).hexdigest(),
        'MD5': hashlib.md5(module_content_analysis.remove_html(content).encode()).hexdigest()
    }
    print(f"[Task] Creating content hashes.")

    if args.verbose:
        for key, content in content_hash.items():
            print(f"[Info][Hash][{key}]{content}")

    # ip extraction
    print(f"[Task] Extracting IP addresses")
    ip_addresses = module_content_analysis.extract_ip_addresses(content)
    for key, value in dns_records.items():
        if key == "A":
            for ip_address in value:
                ip_addresses.append(ip_address)

    if args.verbose:
        for ip in ip_addresses:
            print(f"[Info][ip] {ip} discovered in body of document and A records")

    # comments extractor
    print(f"[Task] Comment hunting")
    comments = module_content_analysis.extract_comments_from_html(content)

    if args.verbose:
        for comment in comments:
            print(f"[Info][comment] {comment}")

    print(f"[Task] Generating Report..")

    data = {
        'title': f"Euri report for {args.domain}",
        'heading': f"Target: {args.domain}",
        'dns_records': dns_records,
        'sub_domains': sub_domains,
        'pages': pages,
        'ssl_certificates': ssl_certificates,
        'headers': headers,
        'cookies': cookies,
        'email_addresses': email_addresses,
        'technology_stack': technology_stack,
        'config_files': config_files,
        'git_repo': git_repo,
        'images': images,
        'links': links,
        'social': social,
        'repo': repo,
        'word_count': word_count,
        'dictionary': dictionary,
        'content_hash': content_hash,
        'ip_addresses': ip_addresses,
        'comments': comments
    }


    report_title = module_report.generate_summary(data, args.domain)
    print(f"[Task] Finshed. Report available at {report_title}")