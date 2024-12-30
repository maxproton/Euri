import requests
import re

frameworks = {
    'cookie': {
        'php': 'PHPSESSID',
        'ASP.NET': 'ASP.NET_SessionId',
        'Java': 'JSESSIONID',
        'Django': 'sessionid',
        'Rails': '_session_id',
        'Laravel': 'laravel_session',
        'Express': 'connect.sid',
        'ColdFusion': 'CFID',
        'ColdFusionAlt': 'CFTOKEN',
        'Spring': 'JSESSIONID',
        'Flask': 'session',
        'Drupal': 'SESS',
        'WordPress': 'wordpress_logged_in_',
        'Magento': 'frontend',
        'Shopify': '_shopify_y'
    },
    'header': {
        'server': {
            'nginx': 'NGINX, a lightweight, high-performance web server and reverse proxy.',
            'Apache': 'Apache HTTP Server, one of the most popular web servers.',
            'cloudflare': 'Cloud flare proxy Services',
            'Microsoft-IIS': 'Microsoft Internet Information Services, a web server for Windows.',
            'LiteSpeed': 'A high-performance, Apache-compatible web server.',
            'Caddy': 'A modern, secure web server with automatic HTTPS.',
            'AkamaiGHost': 'akamai edge server',
            'BigIP': 'F5 BIG-IP - LOAD BALANCER',
            'Fly': 'Fastly CDN',
            'awselb': 'AWS ELB Elastic LOAD BALANCER',
            'Apache-Coyote': 'Apache Tomcat, a server for Java applications',
            'Jetty': 'A lightweight Java-based web server',
            'Gunicorn': 'A Python WSGI HTTP Server',
            'Unicorn': 'A Ruby-based web server',
            'Node.js': 'Indicates a Node.js environment',
            'PHP': 'Indicates the PHP version in the environment',
            'OpenResty': 'A web platform based on Nginx and Lua',
            'Varnish': 'A caching HTTP reverse proxy',
            'Oracle-HTTP-Server': 'Oracle\'s web server',
            'Cowboy': 'A lightweight web server commonly used with Heroku apps',
            'AmazonS3': 'Amazon S3 bucket'
        }
    },
    'library': {
        "Bootstrap": "bootstrap",
        "jQuery": "jquery",
        "AngularJS": "angular",
        "React": "react",
        "Vue.js": "vue",
        "Ember.js": "ember",
        "Backbone.js": "backbone",
        "Foundation": "foundation",
        "Materialize": "materialize",
        "Tailwind CSS": "tailwind",
        "Bulma": "bulma",
        "Lodash": "lodash",
        "Moment.js": "moment",
        "D3.js": "d3",
        "Chart.js": "chart",
        "Highcharts": "highcharts",
        "Leaflet": "leaflet",
        "Three.js": "three",
        "Anime.js": "anime",
        "GSAP": "gsap",
        "Popper.js": "popper",
        "Axios": "axios",
        "Redux": "redux",
        "Alpine.js": "alpine",
        "Knockout.js": "knockout",
        "Gatsby": "gatsby",
        "Next.js": "next",
        "Nuxt.js": "nuxt",
        "Svelte": "svelte",
        "Meteor": "meteor",
        "Express.js": "express",
        "Flask": "flask",
        "Django": "django",
        "Ruby on Rails": "rails",
        "Laravel": "laravel",
        "ASP.NET": "asp.net",
        "Spring": "spring",
        "Symfony": "symfony",
        "CodeIgniter": "codeigniter",
        "Yii": "yii",
        "CakePHP": "cakephp",
        "Play Framework": "playframework",
        "FastAPI": "fastapi",
        "Pyramid": "pyramid",
        "Tornado": "tornado",
        "Koa": "koa",
        "Hapi.js": "hapi",
        "EJS": ".ejs",
        "Pug": ".pug",
        "Handlebars.js": "handlebars",
        "Mustache": "mustache",
        "Webpack": "webpack",
        "Rollup": "rollup",
        "Parcel": "parcel",
        "RequireJS": "require",
        "SystemJS": "system",
        "Jest": "jest",
        "Mocha": "mocha",
        "QUnit": "qunit",
        "Jasmine": "jasmine"
    }
}

def check_for_server_hinting(value):
    identified_hinting = {}

    for hinting, description in frameworks['header']['server'].items():
        # This ensures partial substrings like 'SESS' won't unintentionally match 'PHPSESSID'
        pattern = rf'\b{re.escape(hinting)}\b'
        if re.search(pattern, value):
            identified_hinting[hinting] = {
                'description': description,
                'version': "Not known"
            }
            # Check for version after "/" and update identified_hinting
            version = value.split("/", 1)[1] if "/" in value else "Not known"
            if version is not None:
                identified_hinting[hinting]['version'] = version

    return identified_hinting

def check_for_cookie_hinting(value):
    identified_hinting = []

    for hinting, description in frameworks['cookie'].items():
        pattern = rf'\b{re.escape(description)}\b'
        if re.search(pattern, value):
            identified_hinting.append(hinting)

    return identified_hinting


def find_web_frameworks(url):
    try:
        if "https://" not in url:
            url = "https://" + url
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        html_content = response.text.lower()  # Convert content to lowercase for case-insensitive matching

        detected_frameworks = []

        for framework, identifier in frameworks['library'].items():
            pattern = rf'\b{re.escape(identifier)}\b'
            if re.search(pattern, html_content):
                detected_frameworks.append(framework)
            #if isinstance(identifier, str) and identifier.lower() in html_content:
            #    detected_frameworks.append(framework)

        return detected_frameworks

    except requests.exceptions.RequestException as e:
        print(f"[Error] fetching URL: {e}")

        return []