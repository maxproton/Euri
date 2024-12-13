from jinja2 import Environment, FileSystemLoader
from datetime import datetime

def generate_summary(data):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template/standard_report.html')

    output = template.render(data)
    current_time = datetime.now()

    formatted_time = current_time.strftime("%Y%m%d%H%M%S")
    with open(f"reports/{formatted_time}-report-standard.html", 'w') as f:
        f.write(output)

    return f"reports/{formatted_time}-report-standard.html"