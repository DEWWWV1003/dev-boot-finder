import glob
import re

files = glob.glob('templates/admin_*.html')
files.append('templates/admin.html')

link = '<li><a href="{{ url_for(\'admin_ai\') }}"><i class="fa-solid fa-microchip"></i> AI Sizing Engine</a></li>\n'

for f in files:
    with open(f, 'r') as file:
        content = file.read()
    
    if 'url_for(\'admin_ai\')' not in content:
        # Insert after Support Desk
        content = content.replace('<li><a href="{{ url_for(\'admin_support\') }}"><i class="fa-solid fa-headset"></i> Support Desk</a></li>',
                                  '<li><a href="{{ url_for(\'admin_support\') }}"><i class="fa-solid fa-headset"></i> Support Desk</a></li>\n                ' + link)
        with open(f, 'w') as file:
            file.write(content)
        print(f"Patched {f}")
