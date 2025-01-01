import xml.etree.ElementTree as ET

external = {
    'DNS dumpster': 'https://dnsdumpster.com',
    'Shodan (ip addresses)': 'https://www.shodan.io,',
    'Open Corperate': 'https://opencorporates.com/companies',
    'pwned - check for compromised acounts': 'https://haveibeenpwned.com',
    'dorks': 'https://www.exploit-db.com/google-hacking-database'
}
def has_letter_or_number(s):
    return any(char.isalnum() for char in s)


def is_sitemap_xml(xml_string):
    try:
        # Parse the XML string
        root = ET.fromstring(xml_string)

        # Check if the root tag is <urlset> (specific to sitemaps)
        return root.tag == "urlset"
    except ET.ParseError:
        # If parsing fails, it's not valid XML
        return False