import requests

config_files = {
    "/web.config": "IIS configuration file for .NET applications, can contain sensitive server and app settings.",
    "/appsettings.json": "ASP.NET Core configuration file, often includes sensitive application settings and secrets.",
    "/applicationHost.config": "IIS global configuration file, contains site-level and server-level configuration.",
    "/.htaccess": "Apache per-directory configuration file, controls access and overrides settings.",
    "/httpd.conf": "Apache global configuration file, manages server-level directives.",
    "/nginx.conf": "Nginx global configuration file, includes server block settings and proxy configurations.",
    "/server.xml": "Tomcat configuration file, includes server and service definitions.",
    "/web.xml": "Tomcat and Java web application configuration file, includes servlet definitions.",
    "/config.php": "PHP application configuration file, commonly used in frameworks like Joomla, WordPress, or custom apps.",
    "/configuration.php": "Joomla global configuration file, contains database and application settings.",
    "/sites/default/settings.php": "Drupal configuration file, includes database connection details and paths.",
    "/env.php": "Magento configuration file, includes database and deployment settings.",
    "/app/etc/local.xml": "Magento 1 configuration file, contains database credentials and encryption keys.",
    "/config.json": "Generic JSON configuration file, used by many modern frameworks and applications.",
    "/Config/config.yaml": "Symfony YAML configuration file, contains application settings.",
    "/.env": "Environment variable configuration file, often used in modern apps like Laravel, Symfony, and Django.",
    "/app/etc/env.php": "Magento 2 configuration file, contains sensitive information about the application setup.",
    "/include/config.php": "Generic PHP configuration file, often used in custom applications.",
    "/wp-config.php": "WordPress core configuration file, includes database connection info and security keys.",
    "/index.php": "Often the entry point for PHP applications, sometimes exposes internal paths if misconfigured.",
    "/default.aspx": "ASP.NET default page file, can expose debug or directory listing data.",
    "/local/settings.py": "Django local settings file, may expose database info and secret keys.",
    "/api/configuration.json": "JSON configuration file for APIs, includes endpoint settings and keys.",
    "/storage/logs/laravel.log": "Laravel log file, can expose stack traces and sensitive application data.",
    "/storage/framework/cache/data": "Laravel cached data, sometimes reveals serialized data with sensitive information.",
    "/tmp/deployment-config.json": "Temporary deployment configuration files left over by CI/CD processes.",
    "/WEB-INF/web.xml": "Java application descriptor file, may reveal servlet and context information.",
    "/META-INF/context.xml": "Java application's context configuration file, often contains JNDI resource details.",
    "/resources/application.yml": "Spring Boot application YAML file, can expose sensitive app settings.",
    "/config/database.yml": "Ruby on Rails database configuration file, contains DB credentials.",
    "/Gemfile": "Ruby on Rails gem dependency file, can expose project metadata.",
    "/composer.json": "PHP Composer package dependency file, can reveal framework versions and sensitive paths.",
    "/composer.lock": "Dependency resolution file for PHP applications, can show sensitive package details.",
    "/package.json": "Node.js project dependency file, reveals module information and versions.",
    "/gulpfile.js": "Node.js task runner file, sometimes leaks development paths and tool usage.",
    "/Gruntfile.js": "Node.js task runner configuration file, may reveal internal configurations.",
    "/config/config.inc.php": "phpMyAdmin configuration file, contains sensitive authentication details.",
    "/phpinfo.php": "PHP info file, if left public can reveal server and PHP configuration details.",
    "/core/config/schema.yml": "Symfony or custom framework schema configuration, defines entity structures.",
    "/local/config.yaml": "Generic local YAML configuration, may contain settings and credentials."
}

git_files = [
    "/.git/",
    "/.git/config",
    "/.git/HEAD",
    "/.git/index",
    "/.git/description",
    "/.git/logs/HEAD",
    "/.git/logs/refs/heads/master",
    "/.git/refs/heads/master",
    "/.git/refs/remotes/origin/HEAD",
]

def enumerate_git(domain, verbose):
    results = {}
    for git_file in git_files:
        url = f"https://{domain}{git_file}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                if verbose:
                    print(f"[Info][FOUND-GIT] {git_file}")
                results[git_file] = response.text
            if response.status_code == 403:
                if verbose:
                    print(f"[Info][GIT][403] FORBIDDEN {git_file}")
            if response.status_code == 404:
                if verbose:
                    print(f"[Info][GIT][404] NOT FOUND {git_file}")
            if response.status_code == 500:
                if verbose:
                    print(f"[Info][GIT][500] IT WENT WRONG {git_file}")
        except requests.RequestException as e:
            if verbose:
                print(f"[Error] {git_file} - Could not retrieve: {e}")

    return results

def get_git(domain, verbose):
    if "https://" not in domain:
        domain = "https://" + domain
    git_results = enumerate_git(domain, verbose)

    if "/.git/config" in git_results:
        if verbose:
            print("[Info][GIT] Extracting `.git/config` details...")
        config_content = git_results["/.git/config"]
        parsed_info = extract_git_config(config_content)
        if verbose:
            print(f"[Info][GIT] Repository Info: {parsed_info}")

    return git_results

def extract_git_config(config_content):
    git_info = {}
    for line in config_content.splitlines():
        if line.startswith("[remote"):
            git_info["remote"] = line.split()[-1]
        if "url" in line:
            git_info["url"] = line.split("=", 1)[-1].strip()
    return git_info

def check_for_config_files(domain, verbose):

    results = {}
    if "https://" not in domain:
        domain = "https://" + domain

    for file_path, description in config_files.items():
        url = f"https://{domain}{file_path}"
        if verbose:
            print(f"[Info] Checking for config file {url}")
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                results[file_path] = response.text
        except requests.RequestException as e:
            if verbose:
                print(f"Error: {str(e)}") # Save it anyway there might be something here

    return results
