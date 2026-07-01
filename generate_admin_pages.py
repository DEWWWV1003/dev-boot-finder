import os

def build_page(title, body_content, out_filename):
    with open('templates/admin.html', 'r', encoding='utf-8') as f:
        base = f.read()
    
    # We want to replace everything inside <main class="main-content"> ... </main>
    # We can do this with regex or string splitting
    import re
    
    # Find the start of main-content
    start_str = '<main class="main-content">'
    end_str = '</main>'
    
    start_idx = base.find(start_str)
    end_idx = base.rfind(end_str)
    
    if start_idx != -1 and end_idx != -1:
        # Construct new content with the standard topbar
        topbar = """
            <!-- Topbar -->
            <header class="topbar">
                <h2>""" + title + """</h2>
                <div class="topbar-right">
                    <div class="topbar-icons" style="display: flex; align-items: center; gap: 20px; margin-right: 20px;">
                        <a href="{{ url_for('admin_fraud') }}" style="text-decoration: none;">
                            <div class="alert-bell" id="alertBell" style="position: relative; color: var(--text-secondary); font-size: 1.2rem;">
                                <i class="fa-regular fa-bell"></i>
                                <div class="alert-dot" id="alertDot" style="position: absolute; top: -2px; right: -2px; width: 8px; height: 8px; background-color: #ef4444; border-radius: 50%; display: none;"></div>
                            </div>
                        </a>
                        <div class="admin-profile" style="display: flex; align-items: center; gap: 10px;">
                            <div style="width: 35px; height: 35px; background: var(--accent-pink); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white;">
                                A
                            </div>
                            <span>Admin</span>
                        </div>
                    </div>
                </div>
            </header>
            <div class="dash-content">
        """
        
        new_page = base[:start_idx + len(start_str)] + topbar + body_content + "\n            </div>\n" + base[end_idx:]
        
        with open('templates/' + out_filename, 'w', encoding='utf-8') as f:
            f.write(new_page)

# 1. Inventory
inventory_body = """
                <div style="background: rgba(255, 42, 133, 0.05); border: 1px solid var(--border-color); border-radius: 8px; padding: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h3 style="margin: 0; color: var(--accent-pink);">Boot Inventory</h3>
                        <button style="background: var(--accent-pink); color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;"><i class="fa-solid fa-plus"></i> Add New Boot</button>
                    </div>
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="border-bottom: 1px solid var(--border-color); text-align: left;">
                                <th style="padding: 10px;">Image</th>
                                <th style="padding: 10px;">Name</th>
                                <th style="padding: 10px;">Brand</th>
                                <th style="padding: 10px;">Price</th>
                                <th style="padding: 10px;">Stock</th>
                                <th style="padding: 10px;">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for b in boots %}
                            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                                <td style="padding: 10px;"><img src="{{ b['image_url'] }}" width="50" style="border-radius: 4px;"></td>
                                <td style="padding: 10px; color: var(--text-primary);">{{ b['name'] }}</td>
                                <td style="padding: 10px; color: var(--text-secondary);">{{ b['brand'] }}</td>
                                <td style="padding: 10px; font-weight: bold; color: var(--accent-blue);">${{ "%.2f"|format(b['price']) }}</td>
                                <td style="padding: 10px;"><span style="color: #4ade80;">In Stock (42)</span></td>
                                <td style="padding: 10px;">
                                    <button style="background: transparent; border: 1px solid var(--accent-blue); color: var(--accent-blue); padding: 5px 10px; border-radius: 4px; cursor: pointer; margin-right: 5px;">Edit</button>
                                    <button style="background: transparent; border: 1px solid #ef4444; color: #ef4444; padding: 5px 10px; border-radius: 4px; cursor: pointer;">Del</button>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
"""

# 2. Marketing
marketing_body = """
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div style="background: rgba(181, 55, 242, 0.05); border: 1px solid var(--border-color); border-radius: 8px; padding: 20px;">
                        <h3 style="margin-top: 0; color: var(--accent-purple);"><i class="fa-solid fa-ticket"></i> Promo Codes</h3>
                        <p style="color: var(--text-secondary);">Create and manage discount codes.</p>
                        <div style="margin-top: 20px; display: flex; gap: 10px;">
                            <input type="text" placeholder="e.g. SUMMER20" style="flex-grow: 1; background: #000; border: 1px solid var(--border-color); color: white; padding: 10px; border-radius: 4px;">
                            <input type="number" placeholder="Discount %" style="width: 100px; background: #000; border: 1px solid var(--border-color); color: white; padding: 10px; border-radius: 4px;">
                            <button style="background: var(--accent-purple); color: white; border: none; padding: 10px 20px; border-radius: 4px; font-weight: bold;">Create</button>
                        </div>
                        <div style="margin-top: 20px; border-top: 1px solid var(--border-color); padding-top: 10px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.5); padding: 10px; border-radius: 4px;">
                                <div><strong style="color: white;">WELCOME10</strong> <span style="color: var(--text-secondary); margin-left: 10px;">10% Off</span></div>
                                <span style="color: #4ade80;">Active</span>
                            </div>
                        </div>
                    </div>
                    <div style="background: rgba(0, 229, 255, 0.05); border: 1px solid var(--border-color); border-radius: 8px; padding: 20px;">
                        <h3 style="margin-top: 0; color: var(--accent-blue);"><i class="fa-solid fa-image"></i> Storefront Banner</h3>
                        <p style="color: var(--text-secondary);">Manage the hero banner on the user storefront.</p>
                        <div style="margin-top: 20px;">
                            <label style="color: var(--text-secondary); display: block; margin-bottom: 5px;">Banner Headline</label>
                            <input type="text" value="New DBF X Collection Drops Friday!" style="width: 100%; background: #000; border: 1px solid var(--border-color); color: white; padding: 10px; border-radius: 4px; margin-bottom: 15px;">
                            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
                                <input type="checkbox" id="bannerActive" checked>
                                <label for="bannerActive" style="color: white;">Banner is Live</label>
                            </div>
                            <button style="background: var(--accent-blue); color: #000; border: none; padding: 10px 20px; border-radius: 4px; font-weight: bold; width: 100%;">Update Storefront</button>
                        </div>
                    </div>
                </div>
"""

# 3. Analytics
analytics_body = """
                <div style="background: rgba(0, 0, 0, 0.2); border: 1px solid var(--border-color); border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                    <h3 style="margin-top: 0; color: var(--accent-pink);"><i class="fa-solid fa-chart-pie"></i> Revenue Breakdown</h3>
                    <div style="display: flex; gap: 20px; margin-top: 20px;">
                        <div style="flex: 1; background: rgba(255, 42, 133, 0.1); border-radius: 8px; padding: 20px; text-align: center;">
                            <h4 style="color: var(--text-secondary); margin: 0 0 10px 0;">Speed Boots</h4>
                            <h2 style="color: white; margin: 0;">$14,250</h2>
                            <span style="color: #4ade80;"><i class="fa-solid fa-arrow-trend-up"></i> +12%</span>
                        </div>
                        <div style="flex: 1; background: rgba(181, 55, 242, 0.1); border-radius: 8px; padding: 20px; text-align: center;">
                            <h4 style="color: var(--text-secondary); margin: 0 0 10px 0;">Control Boots</h4>
                            <h2 style="color: white; margin: 0;">$8,900</h2>
                            <span style="color: #4ade80;"><i class="fa-solid fa-arrow-trend-up"></i> +5%</span>
                        </div>
                        <div style="flex: 1; background: rgba(0, 229, 255, 0.1); border-radius: 8px; padding: 20px; text-align: center;">
                            <h4 style="color: var(--text-secondary); margin: 0 0 10px 0;">Power Boots</h4>
                            <h2 style="color: white; margin: 0;">$5,400</h2>
                            <span style="color: #ef4444;"><i class="fa-solid fa-arrow-trend-down"></i> -2%</span>
                        </div>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div style="background: rgba(0, 0, 0, 0.2); border: 1px solid var(--border-color); border-radius: 8px; padding: 20px;">
                        <h4 style="margin-top: 0; color: var(--text-primary);">Top Selling Brands</h4>
                        <ul style="list-style: none; padding: 0; margin: 0;">
                            <li style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid var(--border-color);">
                                <span style="color: var(--text-secondary);">Nike</span>
                                <strong style="color: white;">45%</strong>
                            </li>
                            <li style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid var(--border-color);">
                                <span style="color: var(--text-secondary);">Adidas</span>
                                <strong style="color: white;">35%</strong>
                            </li>
                            <li style="display: flex; justify-content: space-between; padding: 10px 0;">
                                <span style="color: var(--text-secondary);">Puma</span>
                                <strong style="color: white;">20%</strong>
                            </li>
                        </ul>
                    </div>
                    <div style="background: rgba(0, 0, 0, 0.2); border: 1px solid var(--border-color); border-radius: 8px; padding: 20px; display: flex; align-items: center; justify-content: center;">
                        <div style="text-align: center; color: var(--text-secondary);">
                            <i class="fa-solid fa-map-location-dot" style="font-size: 3rem; margin-bottom: 10px; color: var(--accent-purple);"></i>
                            <p>Global Heatmap Loading...</p>
                        </div>
                    </div>
                </div>
"""

# 4. Support
support_body = """
                <div style="display: flex; height: 600px; gap: 20px;">
                    <div style="width: 300px; background: rgba(0,0,0,0.2); border: 1px solid var(--border-color); border-radius: 8px; display: flex; flex-direction: column;">
                        <div style="padding: 15px; border-bottom: 1px solid var(--border-color);">
                            <h4 style="margin: 0; color: white;">Active Tickets <span style="background: var(--accent-pink); padding: 2px 8px; border-radius: 10px; font-size: 0.8rem; margin-left: 10px;">3</span></h4>
                        </div>
                        <div style="flex-grow: 1; overflow-y: auto;">
                            <div style="padding: 15px; border-bottom: 1px solid var(--border-color); border-left: 3px solid var(--accent-pink); background: rgba(255, 255, 255, 0.05); cursor: pointer;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                    <strong style="color: white;">John Doe</strong>
                                    <small style="color: var(--text-secondary);">10m ago</small>
                                </div>
                                <div style="color: var(--text-secondary); font-size: 0.9rem;">Order #442 delivery issue...</div>
                            </div>
                            <div style="padding: 15px; border-bottom: 1px solid var(--border-color); cursor: pointer;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                    <strong style="color: white;">Jane Smith</strong>
                                    <small style="color: var(--text-secondary);">1h ago</small>
                                </div>
                                <div style="color: var(--text-secondary); font-size: 0.9rem;">Return policy question...</div>
                            </div>
                        </div>
                    </div>
                    <div style="flex-grow: 1; background: rgba(0,0,0,0.2); border: 1px solid var(--border-color); border-radius: 8px; display: flex; flex-direction: column;">
                        <div style="padding: 15px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h4 style="margin: 0; color: white;">John Doe</h4>
                                <small style="color: var(--text-secondary);">john.doe@example.com | Order #442</small>
                            </div>
                            <button style="background: transparent; border: 1px solid var(--accent-purple); color: var(--accent-purple); padding: 5px 15px; border-radius: 4px;">Resolve Ticket</button>
                        </div>
                        <div style="flex-grow: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px;">
                            <div style="align-self: flex-start; max-width: 70%;">
                                <div style="background: rgba(255,255,255,0.05); padding: 10px 15px; border-radius: 15px 15px 15px 0; color: white;">
                                    Hi, my tracking says delivered but I haven't received my boots yet.
                                </div>
                                <small style="color: var(--text-secondary); margin-top: 5px; display: block;">10:24 AM</small>
                            </div>
                        </div>
                        <div style="padding: 15px; border-top: 1px solid var(--border-color); display: flex; gap: 10px;">
                            <input type="text" placeholder="Type your response..." style="flex-grow: 1; background: #000; border: 1px solid var(--border-color); color: white; padding: 10px; border-radius: 20px; outline: none;">
                            <button style="background: var(--accent-pink); color: white; border: none; width: 40px; height: 40px; border-radius: 50%;"><i class="fa-solid fa-paper-plane"></i></button>
                        </div>
                    </div>
                </div>
"""

build_page("Inventory Management", inventory_body, "admin_inventory.html")
build_page("Marketing & Promotions", marketing_body, "admin_marketing.html")
build_page("Advanced Analytics", analytics_body, "admin_analytics.html")
build_page("Support Desk", support_body, "admin_support.html")
print("Templates generated successfully.")
