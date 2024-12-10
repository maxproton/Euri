import re


def extract_emails(text):
    # Regular expression pattern for email addresses
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    unique_emails = list(set(emails))

    return unique_emails
