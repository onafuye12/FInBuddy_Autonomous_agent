import re

with open('finBuddy.py') as f:
    content = f.read()

imports = re.findall(r'^import (\w+)|^from (\w+)', content, re.M)
dependencies = {imp[0] or imp[1] for imp in imports if imp[0] or imp[1]}

# Filter out standard library modules
std_lib = {'os', 'json', 'datetime', 'timedelta'}  # Add others as needed
external_deps = dependencies - std_lib

print("\n".join(sorted(external_deps)))