import socket
import ssl
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend

ssl_cert = {}
def get_ssl_certificate(hostname):
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    with socket.create_connection((hostname, 443)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            der_cert = ssock.getpeercert(binary_form=True)
            cert = x509.load_der_x509_certificate(der_cert, default_backend())
            return cert

def ssl_cert_analysis(domain):
    cert = get_ssl_certificate(domain)
    ssl_cert["subject"] = cert.subject.rfc4514_string()
    ssl_cert["issuer"] = cert.issuer.rfc4514_string()
    ssl_cert["valid_from"] = cert.not_valid_before
    ssl_cert["valid_to"] = cert.not_valid_after

    return ssl_cert

