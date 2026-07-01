import glob
import os
import re

# 1. Update the 'Settings' link in all admin templates
for f_path in glob.glob('templates/admin*.html'):
    if 'admin_login' in f_path:
        continue
    with open(f_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Find the Settings link which is currently: <li><a href="#"><i class="fa-solid fa-gear"></i> Settings</a></li>
    # Or replace any <a href="#">... Settings</a> with url_for('admin_settings')
    html_content = re.sub(r'<a href="[^"]*">([^<]*Settings)</a>', r'<a href="{{ url_for(\'admin_settings\') }}">\1</a>', html_content)
    
    with open(f_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

# 2. Create admin_settings.html using admin.html as a base
with open('templates/admin.html', 'r', encoding='utf-8') as f:
    base_html = f.read()

# Replace the content of <main class="main-content">
# Find everything from <main class="main-content"> to </main>
main_start = base_html.find('<main class="main-content">')
main_end = base_html.find('</main>', main_start)

if main_start != -1 and main_end != -1:
    # Keep the topbar
    topbar_end = base_html.find('</header>', main_start)
    if topbar_end != -1:
        topbar_end += len('</header>')
    else:
        topbar_end = main_start + len('<main class="main-content">')
        
    before_content = base_html[:topbar_end]
    after_content = base_html[main_end:]
    
    settings_content = """
            <div style="padding: 20px;">
                <h1 style="color: var(--text-primary); margin-bottom: 20px; font-family: 'Outfit', sans-serif;">Security & Legal Settings</h1>
                
                {% if success %}
                <div style="background: rgba(57,255,20,0.1); border: 1px solid var(--accent-green); color: var(--accent-green); padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <i class="fa-solid fa-check"></i> {{ success }}
                </div>
                {% endif %}

                <form method="POST" action="{{ url_for('admin_settings') }}">
                    <!-- Security Lock -->
                    <div class="dash-card" style="margin-bottom: 30px;">
                        <div class="card-header" style="border-bottom: 1px solid var(--border-color); padding-bottom: 15px; margin-bottom: 20px;">
                            <h3 style="color: var(--text-primary);"><i class="fa-solid fa-lock" style="color: var(--accent-pink); margin-right: 10px;"></i>Global Security Lock</h3>
                        </div>
                        <p style="color: var(--text-secondary); margin-bottom: 20px;">Enable this to strictly require login for all storefront pages. Disabling it will allow public access.</p>
                        
                        <div style="display: flex; align-items: center; gap: 15px;">
                            <label class="switch" style="position: relative; display: inline-block; width: 60px; height: 34px;">
                                <input type="checkbox" name="high_security_lock" {% if settings.high_security_lock %}checked{% endif %} style="opacity: 0; width: 0; height: 0;">
                                <span class="slider round" style="position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: var(--bg-dark); border: 1px solid var(--border-color); -webkit-transition: .4s; transition: .4s; border-radius: 34px;"></span>
                            </label>
                            <span style="color: var(--text-primary); font-weight: 600;">Enable Storefront Lockdown</span>
                        </div>
                        <style>
                            .switch input:checked + .slider { background: linear-gradient(135deg, var(--accent-pink), var(--accent-purple)); border-color: transparent; }
                            .switch input:checked + .slider:before { -webkit-transform: translateX(26px); -ms-transform: translateX(26px); transform: translateX(26px); }
                            .slider:before { position: absolute; content: ""; height: 26px; width: 26px; left: 3px; bottom: 3px; background-color: white; -webkit-transition: .4s; transition: .4s; border-radius: 50%; }
                        </style>
                    </div>

                    <!-- Terms of Service -->
                    <div class="dash-card">
                        <div class="card-header" style="border-bottom: 1px solid var(--border-color); padding-bottom: 15px; margin-bottom: 20px;">
                            <h3 style="color: var(--text-primary);"><i class="fa-solid fa-scale-balanced" style="color: var(--accent-blue); margin-right: 10px;"></i>Terms of Service Editor</h3>
                        </div>
                        <p style="color: var(--text-secondary); margin-bottom: 20px;">Edit the legal terms displayed on the public storefront.</p>
                        
                        <textarea name="terms_of_service_text" style="width: 100%; height: 400px; background: var(--bg-dark); color: var(--text-primary); border: 1px solid var(--border-color); padding: 15px; border-radius: 8px; font-family: monospace; font-size: 14px; margin-bottom: 20px; resize: vertical;">{{ settings.terms_of_service_text }}</textarea>
                    </div>

                    <div style="margin-top: 30px; display: flex; justify-content: flex-end;">
                        <button type="submit" style="background: linear-gradient(135deg, var(--accent-pink), var(--accent-purple)); color: white; border: none; padding: 12px 30px; border-radius: 8px; font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 16px; cursor: pointer; display: flex; align-items: center; gap: 10px; transition: all 0.3s ease;">
                            <i class="fa-solid fa-floppy-disk"></i> Save Settings
                        </button>
                    </div>
                </form>
            </div>
    """
    
    final_html = before_content + settings_content + after_content
    with open('templates/admin_settings.html', 'w', encoding='utf-8') as f:
        f.write(final_html)
    print("Created templates/admin_settings.html")
else:
    print("Could not find <main class='main-content'> in admin.html")

print("All done.")
