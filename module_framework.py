
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
            'Cowboy': 'A lightweight web server commonly used with Heroku apps'
        }
    }
}

def check_for_server_hinting(value):
    identified_hinting = {}

    for hinting, description in frameworks['header']['server'].items():
        if hinting in value:
            identified_hinting[hinting] = {
                'description': description,
                'version': "Not known"
            }
            version = value.split("/", 1)[1] if "/" in value else "Not known"
            if version is not None:
                identified_hinting[hinting]['version'] = version


    return identified_hinting

def check_for_cookie_hinting(value):
    identified_hinting = []

    for hinting, description in frameworks['cookie'].items():
        if description in value:
            identified_hinting.append(hinting)

    return identified_hinting