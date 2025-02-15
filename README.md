```
            /$$      /$$ /$$$$$$$  /$$$$$$$                                         
            | $$$    /$$$| $$__  $$| $$__  $$                                        
            | $$$$  /$$$$| $$  \ $$| $$  \ $$  /$$$$$$   /$$$$$$$  /$$$$$$  /$$$$$$$ 
            | $$ $$/$$ $$| $$$$$$$/| $$$$$$$/ /$$__  $$ /$$_____/ /$$__  $$| $$__  $$
            | $$  $$$| $$| $$____/ | $$__  $$| $$$$$$$$| $$      | $$  \ $$| $$  \ $$
            | $$\  $ | $$| $$      | $$  \ $$| $$_____/| $$      | $$  | $$| $$  | $$
            | $$ \/  | $$| $$      | $$  | $$|  $$$$$$$|  $$$$$$$|  $$$$$$/| $$  | $$
            |__/     |__/|__/      |__/  |__/ \_______/ \_______/ \______/ |__/  |__/
                                                                         
                                                                         
                                                                         

                                  (c) Maxproton Labs
                            Licensed under Apache License 2.0

              Please do not use in military or for illegal purposes.
         (This is the wish of the author and non-binding. Many people working
          in these organizations do not care for laws and ethics anyways.
               You are not one of the "good" ones if you ignore this.)
```

## Overview

This tool processes a given domain and performs various operations on its lines. It allows for suppression of certain checks, customization of error detection, and provides detailed verbosity control.

## Features

- Analyze a given domain for various attributes.
- Option to suppress less common DNS record checks.
- Control verbosity of output.
- Disable Google search queries.
- Skip header analysis for framework detection.
- Disable subdomain brute force.
- Custom handling for websites that return 200 status codes with error pages.

## Installation

Ensure you have Python installed (>=3.6). Clone this repository and navigate into the directory:

Run the install bash.

Please note!! --break-system-packages is used!
```bash
git clone https://github.com/maxproton/MpRecon
cd MpRecon
bash install.sh
```
## Usage
### Basic
```bash
python main.py --domain example.com [OPTIONS]
```
### Supress DNS and use Verbose
```bash
python main.py --domain example.com --verbose --suppress-less-common-dns
```
### Disable Google Search and header check
```bash
python main.py --domain example.com --no-google --no-header-check
```
### Custom Error Pages 
Sometimes these are a pain! so you can customise the detection of error pages for page enumeration
```bash
python main.py --domain example.com --no-found-size 1024 --no-found-text "Error occurred"
```

## Arguments

| Argument                    | Short Flag | Description                                                                 | Required |
|-----------------------------|------------|-----------------------------------------------------------------------------|----------|
| --domain                    | -d         | The initial domain to analyze.                                               | Yes      |
| --suppress-less-common-dns   | -s         | Suppress less common DNS record checks.                                      | No       |
| --verbose                   | -v         | Show detailed output of all operations.                                      | No       |
| --no-google                 | -g         | Disable Google search queries.                                               | No       |
| --no-header-check           | -aa        | Skip analysis of response headers for framework clues.                       | No       |
| --no-subdomain-brute        | -bb        | Disable subdomain brute force.                                               | No       |
| --no-found-size             | -te        | Define the expected size of an error page (useful for sites that return 200 on errors). | No       |
| --no-found-text             | -ta        | Define text expected in an error page to filter false positives.             | No       |

## Using google search
In order to use the google search feature you need to add your keys to the following in the .env file

```bash
GOOGLE_SEARCH_API_KEY="{key}"
GOOGLE_SEARCH_ID="{id}"
```
## Custom report folder
By default the setup creates a directory /reports. You can specify your own folder in the .env file
by changing the following :

```commandline
REPORT_DIR="reports"
```
### Custom lists 
MPRecon doesn't come with alot of lists, it ships with two sets of 'test' lists. You can change the lists directory
in the .env file under 
```commandline
LIST_DIR="lists"
```
Please note there must be two .txt files within which ever folder you use called 
```commandline
pages.txt
subdomains.txt
```
These are not customisable fields. 

## Licence
Licensed under Apache License 2.0
