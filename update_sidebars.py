import os
import glob

target = '<li><a href="{{ url_for(\'admin_fraud\') }}"><i class="fa-solid fa-shield-halved"></i> Fraud Detection</a></li>'
new_link = '<li><a href="{{ url_for(\'admin_users\') }}"><i class="fa-solid fa-users"></i> Registered Users</a></li>\n                '

for f in glob.glob('templates/admin*.html'):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    if 'admin_users' not in content:
        if target in content:
            new_content = content.replace(target, new_link + target)
            with open(f, 'w', encoding='utf-8') as file:
                file.write(new_content)
            print(f'Updated {f}')
