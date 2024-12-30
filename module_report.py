from jinja2 import Environment, FileSystemLoader
from datetime import datetime

def generate_summary(data, domain):
    domain = domain.split('/', 1)[0]

    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template/standard_report.html')
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y%m%d%H%M%S")
    data['file_name'] = f"reports/{domain}-{formatted_time}-"
    output = template.render(data)
    with open(f"reports/{domain}-{formatted_time}-report-standard.html", 'w') as f:
        f.write(output)

    with open(f"reports/{domain}-{formatted_time}-dictionary.txt", "w") as file:
        for item in data['dictionary']:
            file.write(f"{item}\n")

    with open(f"reports/{domain}-{formatted_time}-links.txt", "w") as file:
        for item in data['links']['live']:
            file.write(f"{item}\n")

    return f"reports/{domain}-{formatted_time}-report-standard.html"

def generate_image_summary(data, domain):
    domain = domain.split('/', 1)[0]

    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template/image_report.html')

    output = template.render(data)
    current_time = datetime.now()

    formatted_time = current_time.strftime("%Y%m%d%H%M%S")
    with open(f"reports/{domain}-{formatted_time}-report-image.html", 'w') as f:
        f.write(output)

    return f"reports/{domain}-{formatted_time}-report-image.html"