# Euri
### We send his crazy ass accross the internet and back again looking for treasure.

#### Project Scope
Euri combines the principals and ideas of various OSINT tools into one single place, primarily to save time and make data collection more uniformed. We arn't inventing the wheel here, so where technology exists already and its open source we use it, and credit it's creator accordingly. 

## Currently supported features
### DNS lookup
we perform a standard DNS lookup and collect the DNS records, if there happen to be CNAMES which match the subdomain parsers requirements we add that to
the subdomains list. The parser tries to match all dns record types, this includes a list of
less common ones, if you want to skip the less common ones, use the following argument 
```commandline
--suppress-less-common-dns
```

### Subdomain lookup
Using the google search API Euri performs a lookup using good dorks to try and discover subdomains. 
It then does a subdomain enumeration check using the inbuilt dictionary. To skip the google look up use the flag :
```commandline
--no-google 
```
to skip the subdomain enumeration use:
```commandline
--no-subdomain-brute
```
### SSL Certificate Lookup
Euri will check the content of the ssl certificate from the main site and verify the issuer, and valid from and valid too dates

### Header grab and analysis
The next thing it does is pulls the headers from the website and stores them for analysis, 
the analysis part it looks for hints of technology stack, which it late combines with the page analysis
if you wish to skip the analysis use the following flag
```commandline
--no-header-check
```

### Cookie Grabbing 
After its obtained a headers list, it finds the cookies and takes them and puts them in its cookie jar
for consumption later.

### Lists
Its important to note Euri does not ship with lists re-installed. Please place your own 
lists for enumeration in the lists folder under the appropriate name. 