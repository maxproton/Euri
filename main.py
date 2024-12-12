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
from dotenv import load_dotenv
import os

domain = ""
dns_records = {}
sub_domains = {}
pages = []
ssl_certificates = {}
headers = {}
cookies = {}
email_addresses = []
technology_stack = {}

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
    parser.add_argument("-tb", "--no-found-size-tol", type=int, required=False, help="Provide a tolerance level +- for checking content length")
    return parser.parse_args()

if __name__ == '__main__':
    print(banner.banner)
    args = parse_arguments()
    load_dotenv()

    # DNS lookup
    print(f"[Task] Performing DNS Lookup for {args.domain}")
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
    print(f"[Task] Performing non-bruteforce subdomain collection for {args.domain}")
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
        print(f"[Task] Performing Subdomain enumberation from dictionary lists/subdomains.txt on {args.domain}")
        brute_force_subdomains = module_subdomain.run_subdomain_enumeration("lists/subdomains.txt", args.domain, args.verbose)

    sub_domains["new"] = google_dorks_subdomain + dns_subdomains + brute_force_subdomains
    if args.verbose:
        for subdomain in sub_domains["new"]:
            print(f"[Info] {subdomain} Found")


    # SSL Certificate Parsing of main domain
    print(f"[Task] Performing SSL cert analysis")
    ssl_certificates["main"] = module_ssl.ssl_cert_analysis(args.domain)
    if args.verbose:
        print(f"[Info][SSL] Subject: {ssl_certificates['main']['subject']}")
        print(f"[Info][SSL] Issuer: {ssl_certificates['main']['issuer']}")
        print(f"[Info][SSL] Valid-From: {ssl_certificates['main']['valid_from']}")
        print(f"[Info][SSL] Valid-To: {ssl_certificates['main']['valid_to']}")
    email_addresses = email_addresses + module_email.extract_emails(ssl_certificates['main']['subject'])
    email_addresses = email_addresses + module_email.extract_emails(ssl_certificates['main']['issuer'])

    # Header extraction from main domain
    print(f"[Task] Getting all header values for {args.domain}")
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
    print(f"[Task] Collecting pages from available sitemaps {args.domain}")
    robots = module_pages.robots(args.domain)
    sitemaps = module_pages.get_all_sitemap_urls(args.domain)

    # Enumerate using page file to find pages
    enumeration_list_pages = "lists/pages.txt"
    print(f"[Task] Enumerating pages from list {enumeration_list_pages}")
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
        no_found_text,
        args.no_found_size_tol
    )

    server = {}
    # Check technology stack in headers for hints at the type of server and version number
    for key, header in headers[args.domain].items():
        if key != "Set-Cookie" and key != "Cookie":
            server.update(module_framework.check_for_server_hinting(header))

    technology_stack['server'] = server
    if args.verbose:
        for type, server_hinting in technology_stack['server'].items():
            print(f"[Info] Server hinting {type} - {server_hinting['version']} - {server_hinting['description']}")

    cookie_stack = []
    for key, value in cookies.items():
        cookie_stack = cookie_stack + module_framework.check_for_cookie_hinting(key)
    technology_stack['language'] = cookie_stack

    if args.verbose:
        for cook in technology_stack['language']:
            print(f"[Info] language : {cook}")

    library_frameworks = module_framework.find_web_frameworks(args.domain)
    technology_stack['web_technology'] = library_frameworks

    if args.verbose:
        for library in library_frameworks:
            print(f"[Info] {library}")
    #.env and config files
    #.git and git content
    # content analysis
    # all images and meta data
    # all links and indexing (interal add external note)
    # social media link s
    # git hub references
    # email references
    # word count
    # dictionary generation
    # hash value
    # ip extraction
    # checks for links for github, gitlab, bitbucket 

    module_report.generate_summary(technology_stack)