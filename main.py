import csv

import argparse
import banner
import ports
import json
import module_dns
import module_subdomain

domain = ""
dns_records = {}
sub_domains = {"new", "complete"}
pages = {"new", "complete"}

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process a file and perform operations on its lines.")
    parser.add_argument("-d", "--domain", type=str, required=True, help="Initial Domain")
    parser.add_argument("-s", "--suppress-less-common-dns", action="store_true",  help="Suppress less common DNS record checks")
    parser.add_argument("-v", "--verbose", action="store_true", help="Shows you everything!")
    return parser.parse_args()

if __name__ == '__main__':
    print(banner.banner)
    args = parse_arguments()

    print(f"[Task] Performing DNS Lookup for {args.domain}")
    dns_records = module_dns.dns_enumeration(
        args.domain,
        args.suppress_less_common_dns,
        args.verbose
    )

    print(f"[Task] Performing non-bruteforce subdomain collection for {args.domain}")
    print(module_subdomain.find_subdomains_with_nslookup(args.domain))

    google_dorks_subdomain = module_subdomain.duckduckgo_search(f"{args.domain}")
    for link in google_dorks_subdomain:
        print(link)

