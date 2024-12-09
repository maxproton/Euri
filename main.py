import csv

import argparse
import banner
import module_headers
import module_ssl
import ports
import json
import module_dns
import module_subdomain
import module_ssl
import module_headers
from dotenv import load_dotenv
import os

domain = ""
dns_records = {}
sub_domains = {}
pages = {}
ssl_certificates = {}
headers = {}

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process a file and perform operations on its lines.")
    parser.add_argument("-d", "--domain", type=str, required=True, help="Initial Domain")
    parser.add_argument("-s", "--suppress-less-common-dns", action="store_true",  help="Suppress less common DNS record checks")
    parser.add_argument("-v", "--verbose", action="store_true", help="Shows you everything!")
    parser.add_argument("-g", "--no-google", action="store_true", help="Do not perform google searches")
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
        print("---DNS RECORDS---")
        for type, answer in dns_records.items():
            for record in answer:
                print(f"{type} Record: {record}")

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

    sub_domains["new"] = google_dorks_subdomain + dns_subdomains
    if args.verbose:
        for subdomain in sub_domains["new"]:
            print(f"subdomain: {subdomain}")


    # SSL Certificate Parsing of main domain
    print(f"[Task] Performing SSL cert analysis")
    ssl_certificates["main"] = module_ssl.ssl_cert_analysis(args.domain)
    if args.verbose:
        print(ssl_certificates["main"]["subject"])
        print(ssl_certificates["main"]["issuer"])
        print(ssl_certificates["main"]["valid_from"])
        print(ssl_certificates["main"]["valid_to"])

    # Header extraction from main domain
    headers[args.domain] = module_headers.get_header(args.domain)
    if args.verbose:
        for key, header in headers[args.domain].items():
            print(f"{key} : {header}")

