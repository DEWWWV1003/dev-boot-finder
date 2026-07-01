import os
import glob
import re

# 1. Update CSS
css_file = 'static/css/dashboard.css'
with open(css_file, 'r', encoding='utf-8') as f:
    css_content = f.read()

# Replace variables and some hardcoded colors
css_content = css_content.replace('var(--accent-red)', 'var(--accent-pink)')
css_content = css_content.replace('rgba(211, 47, 47, 0.1)', 'rgba(255, 42, 133, 0.1)')
css_content = css_content.replace('rgba(211, 47, 47, 0.2)', 'rgba(255, 42, 133, 0.2)')
css_content = css_content.replace('background-color: var(--accent-pink);', 'background: linear-gradient(135deg, var(--accent-pink), var(--accent-purple));')
css_content = css_content.replace('color: var(--accent-pink);', 'background: -webkit-linear-gradient(var(--accent-pink), var(--accent-purple)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;')

with open(css_file, 'w', encoding='utf-8') as f:
    f.write(css_content)

# 2. Update all admin HTML templates' sidebars
new_sidebar_items = """
                <li><a href="{{ url_for('admin_inventory') }}"><i class="fa-solid fa-boxes-stacked"></i> Inventory</a></li>
                <li><a href="{{ url_for('admin_marketing') }}"><i class="fa-solid fa-bullhorn"></i> Marketing</a></li>
                <li><a href="{{ url_for('admin_analytics') }}"><i class="fa-solid fa-chart-line"></i> Analytics</a></li>
                <li><a href="{{ url_for('admin_support') }}"><i class="fa-solid fa-headset"></i> Support Desk</a></li>
"""

for f_path in glob.glob('templates/admin*.html'):
    with open(f_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Check if we already inserted them to prevent duplication
    if 'admin_inventory' not in html_content:
        # Insert after Fraud Detection link
        target = '<li><a href="{{ url_for(\'admin_fraud\') }}"><i class="fa-solid fa-shield-halved"></i> Fraud Detection</a></li>'
        html_content = html_content.replace(target, target + new_sidebar_items)
        
        with open(f_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

print("Updates completed successfully.")
