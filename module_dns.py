import dns.resolver

dns_records = {}
less_common_records = [
    "PTR",
    "SOA",
    "CAA",
    "NAPTR",
    "DS",
    "DNSKEY",
    "RRSIG",
    "TLSA",
    "SPF",
    "HINFO",
    "LOC",
    "RP",
    "DNAME",
    "URI",
    "AFSDB",
    "SMIMEA",
    "NSAP",
    "EUI48",
    "EUI64"
]

common_records = [
    "A",
    "MX",
    "AAAA",
    "CNAME",
    "TXT",
    "NS",
    "SRV"
]

def dns_enumeration(domain, suppress_less_common, verbose):

    for record_type in common_records:
        record_lookup(domain, record_type, verbose)

    # The user can suppress these less common checks
    if not suppress_less_common:
        for record_type in less_common_records:
            record_lookup(domain, record_type, verbose)

    return dns_records


def record_lookup(domain, type, verbose):
    try:
        #dns.resolver.nameservers = ['8.8.8.8']
        #dns.resolver.timeout = 5  # seconds
        #dns.resolver.lifetime = 5
        answers = dns.resolver.resolve(domain, type)
        for answer in answers:
            if type not in dns_records:
                dns_records[type] = []
            dns_records[type].append(answer)
    except dns.resolver.NoAnswer:
        if verbose:
            print(f"No {type} record found.")
    except Exception as e:
        if verbose:
            print(f"Error: {e}")
