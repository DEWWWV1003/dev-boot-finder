import re

with open('templates/customizer.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Replace the studs SVG group
old_studs = r'<g id="studs-group">.*?</g>\s*<!-- ─── Upper \(main body\) ─── -->'
new_studs = """<!-- ─── Realistic Conical Studs (Tiempo) ─── -->
                        <g id="studs-conical">
                            <g transform="translate(130, 348)">
                                <ellipse cx="0" cy="22" rx="9" ry="4" fill="url(#stud-shadow)"/>
                                <path d="M-8 0 C-6 8, -9 18, -7 22 L7 22 C9 18, 6 8, 8 0 Z" fill="url(#stud-grad)" stroke="#ccc" stroke-width="0.5"/>
                                <ellipse cx="0" cy="0" rx="8" ry="5" fill="#f0f0f0" stroke="#d0d0d0" stroke-width="0.5"/>
                                <ellipse cx="-2" cy="-1" rx="3" ry="2" fill="url(#stud-highlight)"/>
                            </g>
                            <g transform="translate(185, 352)">
                                <ellipse cx="0" cy="22" rx="9" ry="4" fill="url(#stud-shadow)"/>
                                <path d="M-8 0 C-6 8, -9 18, -7 22 L7 22 C9 18, 6 8, 8 0 Z" fill="url(#stud-grad)" stroke="#ccc" stroke-width="0.5"/>
                                <ellipse cx="0" cy="0" rx="8" ry="5" fill="#f0f0f0" stroke="#d0d0d0" stroke-width="0.5"/>
                                <ellipse cx="-2" cy="-1" rx="3" ry="2" fill="url(#stud-highlight)"/>
                            </g>
                            <g transform="translate(240, 354)">
                                <ellipse cx="0" cy="20" rx="8" ry="3.5" fill="url(#stud-shadow)"/>
                                <path d="M-7 0 C-5 7, -8 16, -6 20 L6 20 C8 16, 5 7, 7 0 Z" fill="url(#stud-grad)" stroke="#ccc" stroke-width="0.5"/>
                                <ellipse cx="0" cy="0" rx="7" ry="4.5" fill="#f0f0f0" stroke="#d0d0d0" stroke-width="0.5"/>
                                <ellipse cx="-2" cy="-1" rx="2.5" ry="1.8" fill="url(#stud-highlight)"/>
                            </g>
                            <g transform="translate(300, 350)">
                                <ellipse cx="0" cy="20" rx="8" ry="3.5" fill="url(#stud-shadow)"/>
                                <path d="M-7 0 C-5 7, -8 16, -6 20 L6 20 C8 16, 5 7, 7 0 Z" fill="url(#stud-grad)" stroke="#ccc" stroke-width="0.5"/>
                                <ellipse cx="0" cy="0" rx="7" ry="4.5" fill="#f0f0f0" stroke="#d0d0d0" stroke-width="0.5"/>
                                <ellipse cx="-2" cy="-1" rx="2.5" ry="1.8" fill="url(#stud-highlight)"/>
                            </g>
                            <g transform="translate(360, 342)">
                                <ellipse cx="0" cy="20" rx="8" ry="3.5" fill="url(#stud-shadow)"/>
                                <path d="M-7 0 C-5 7, -8 16, -6 20 L6 20 C8 16, 5 7, 7 0 Z" fill="url(#stud-grad)" stroke="#ccc" stroke-width="0.5"/>
                                <ellipse cx="0" cy="0" rx="7" ry="4.5" fill="#f0f0f0" stroke="#d0d0d0" stroke-width="0.5"/>
                                <ellipse cx="-2" cy="-1" rx="2.5" ry="1.8" fill="url(#stud-highlight)"/>
                            </g>
                            <g transform="translate(420, 336)">
                                <ellipse cx="0" cy="22" rx="9" ry="4" fill="url(#stud-shadow)"/>
                                <path d="M-8 0 C-6 8, -9 18, -7 22 L7 22 C9 18, 6 8, 8 0 Z" fill="url(#stud-grad)" stroke="#ccc" stroke-width="0.5"/>
                                <ellipse cx="0" cy="0" rx="8" ry="5" fill="#f0f0f0" stroke="#d0d0d0" stroke-width="0.5"/>
                                <ellipse cx="-2" cy="-1" rx="3" ry="2" fill="url(#stud-highlight)"/>
                            </g>
                            <g transform="translate(480, 338)">
                                <ellipse cx="0" cy="22" rx="9" ry="4" fill="url(#stud-shadow)"/>
                                <path d="M-8 0 C-6 8, -9 18, -7 22 L7 22 C9 18, 6 8, 8 0 Z" fill="url(#stud-grad)" stroke="#ccc" stroke-width="0.5"/>
                                <ellipse cx="0" cy="0" rx="8" ry="5" fill="#f0f0f0" stroke="#d0d0d0" stroke-width="0.5"/>
                                <ellipse cx="-2" cy="-1" rx="3" ry="2" fill="url(#stud-highlight)"/>
                            </g>
                            <g transform="translate(530, 342)">
                                <ellipse cx="0" cy="20" rx="8" ry="3.5" fill="url(#stud-shadow)"/>
                                <path d="M-7 0 C-5 7, -8 16, -6 20 L6 20 C8 16, 5 7, 7 0 Z" fill="url(#stud-grad)" stroke="#ccc" stroke-width="0.5"/>
                                <ellipse cx="0" cy="0" rx="7" ry="4.5" fill="#f0f0f0" stroke="#d0d0d0" stroke-width="0.5"/>
                                <ellipse cx="-2" cy="-1" rx="2.5" ry="1.8" fill="url(#stud-highlight)"/>
                            </g>
                        </g>

                        <!-- ─── Bladed Studs (Mercurial) ─── -->
                        <g id="studs-bladed" style="display:none;">
                            <g transform="translate(130, 348)">
                                <ellipse cx="0" cy="22" rx="9" ry="4" fill="url(#stud-shadow)"/>
                                <path d="M-6 0 L-2 22 L6 18 L6 0 Z" fill="url(#stud-grad)" stroke="#ccc" stroke-width="0.5"/>
                                <polygon points="-6,0 6,0 2,2" fill="#f0f0f0" />
                            </g>
                            <g transform="translate(185, 352)">
                                <ellipse cx="0" cy="22" rx="9" ry="4" fill="url(#stud-shadow)"/>
                                <path d="M-5 0 L-1 22 L7 18 L5 0 Z" fill="url(#stud-grad)" stroke="#ccc" stroke-width="0.5"/>
                                <polygon points="-5,0 5,0 1,2" fill="#f0f0f0" />
                            </g>
                            <g transform="translate(240, 354)">
                                <ellipse cx="0" cy="20" rx="8" ry="3.5" fill="url(#stud-shadow)"/>
                                <path d="M-4 0 L0 20 L8 16 L4 0 Z" fill="url(#stud-grad)" stroke="#ccc" stroke-width="0.5"/>
                                <polygon points="-4,0 4,0 0,2" fill="#f0f0f0" />
                            </g>
                            <g transform="translate(300, 350)">
                                <ellipse cx="0" cy="20" rx="8" ry="3.5" fill="url(#stud-shadow)"/>
                                <path d="M-4 0 L1 20 L9 15 L3 0 Z" fill="url(#stud-grad)" stroke="#ccc" stroke-width="0.5"/>
                                <polygon points="-4,0 3,0 0,2" fill="#f0f0f0" />
                            </g>
                            <g transform="translate(360, 342)">
                                <ellipse cx="0" cy="20" rx="8" ry="3.5" fill="url(#stud-shadow)"/>
                                <path d="M-4 0 L2 18 L10 13 L2 0 Z" fill="url(#stud-grad)" stroke="#ccc" stroke-width="0.5"/>
                            </g>
                            <g transform="translate(420, 336)">
                                <ellipse cx="0" cy="22" rx="9" ry="4" fill="url(#stud-shadow)"/>
                                <path d="M-5 0 L4 20 L12 14 L3 0 Z" fill="url(#stud-grad)" stroke="#ccc" stroke-width="0.5"/>
                            </g>
                            <g transform="translate(480, 338)">
                                <ellipse cx="0" cy="22" rx="9" ry="4" fill="url(#stud-shadow)"/>
                                <path d="M-6 0 L4 21 L12 14 L3 0 Z" fill="url(#stud-grad)" stroke="#ccc" stroke-width="0.5"/>
                            </g>
                            <g transform="translate(530, 342)">
                                <ellipse cx="0" cy="20" rx="8" ry="3.5" fill="url(#stud-shadow)"/>
                                <path d="M-5 0 L3 19 L10 13 L2 0 Z" fill="url(#stud-grad)" stroke="#ccc" stroke-width="0.5"/>
                            </g>
                        </g>

                        <!-- ─── Mixed Studs (Copa) ─── -->
                        <g id="studs-mixed" style="display:none;">
                            <g transform="translate(130, 348)">
                                <ellipse cx="0" cy="22" rx="9" ry="4" fill="url(#stud-shadow)"/>
                                <path d="M-8 0 C-6 8, -9 18, -7 22 L7 22 C9 18, 6 8, 8 0 Z" fill="url(#stud-grad)" stroke="#ccc" stroke-width="0.5"/>
                            </g>
                            <g transform="translate(185, 352)">
                                <ellipse cx="0" cy="22" rx="9" ry="4" fill="url(#stud-shadow)"/>
                                <path d="M-5 0 L-1 22 L7 18 L5 0 Z" fill="url(#stud-grad)" stroke="#ccc" stroke-width="0.5"/>
                            </g>
                            <g transform="translate(240, 354)">
                                <ellipse cx="0" cy="20" rx="8" ry="3.5" fill="url(#stud-shadow)"/>
                                <path d="M-7 0 C-5 7, -8 16, -6 20 L6 20 C8 16, 5 7, 7 0 Z" fill="url(#stud-grad)" stroke="#ccc" stroke-width="0.5"/>
                            </g>
                            <g transform="translate(300, 350)">
                                <ellipse cx="0" cy="20" rx="8" ry="3.5" fill="url(#stud-shadow)"/>
                                <path d="M-4 0 L1 20 L9 15 L3 0 Z" fill="url(#stud-grad)" stroke="#ccc" stroke-width="0.5"/>
                            </g>
                            <g transform="translate(360, 342)">
                                <ellipse cx="0" cy="20" rx="8" ry="3.5" fill="url(#stud-shadow)"/>
                                <path d="M-7 0 C-5 7, -8 16, -6 20 L6 20 C8 16, 5 7, 7 0 Z" fill="url(#stud-grad)" stroke="#ccc" stroke-width="0.5"/>
                            </g>
                            <g transform="translate(420, 336)">
                                <ellipse cx="0" cy="22" rx="9" ry="4" fill="url(#stud-shadow)"/>
                                <path d="M-8 0 C-6 8, -9 18, -7 22 L7 22 C9 18, 6 8, 8 0 Z" fill="url(#stud-grad)" stroke="#ccc" stroke-width="0.5"/>
                            </g>
                            <g transform="translate(480, 338)">
                                <ellipse cx="0" cy="22" rx="9" ry="4" fill="url(#stud-shadow)"/>
                                <path d="M-6 0 L4 21 L12 14 L3 0 Z" fill="url(#stud-grad)" stroke="#ccc" stroke-width="0.5"/>
                            </g>
                            <g transform="translate(530, 342)">
                                <ellipse cx="0" cy="20" rx="8" ry="3.5" fill="url(#stud-shadow)"/>
                                <path d="M-7 0 C-5 7, -8 16, -6 20 L6 20 C8 16, 5 7, 7 0 Z" fill="url(#stud-grad)" stroke="#ccc" stroke-width="0.5"/>
                            </g>
                        </g>

                        <!-- ─── Upper (main body) ─── -->"""
html = re.sub(old_studs, new_studs, html, flags=re.DOTALL)

# 2. Add Stud Type UI
old_ui = r'<hr class="divider">\s*<!-- PERSONALIZATION -->'
new_ui = """<div class="section-label" style="margin-top:0; color:#aaa; font-size:0.7rem;">Stud Type</div>
                    <div class="flag-grid" id="stud-type-picker">
                        <div class="flag-btn active" data-type="conical" style="font-size: 0.85rem; width: auto; padding: 0 12px; font-weight: 600;">Tiempo (Conical)</div>
                        <div class="flag-btn" data-type="bladed" style="font-size: 0.85rem; width: auto; padding: 0 12px; font-weight: 600;">Mercurial (Bladed)</div>
                        <div class="flag-btn" data-type="mixed" style="font-size: 0.85rem; width: auto; padding: 0 12px; font-weight: 600;">Copa (Mixed)</div>
                    </div>

                    <hr class="divider">

                    <!-- PERSONALIZATION -->"""
html = re.sub(old_ui, new_ui, html)

# 3. Add JS logic
old_js = r"const customData = {.*?\n        price: 250.00\n    };"
new_js = """const customData = {
        upper: '#ffffff', logo: '#222222', laces: '#222222', soleplate: '#333333',
        text: 'PRO', number: '10', flag: '🇦🇷', icon: '', studType: 'conical',
        price: 250.00
    };"""
html = re.sub(old_js, new_js, html, flags=re.DOTALL)

old_js2 = r"// ═══ Add to Cart ═══"
new_js2 = """// ═══ Stud Type Picker ═══
    document.getElementById('stud-type-picker').querySelectorAll('.flag-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.getElementById('stud-type-picker').querySelectorAll('.flag-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            customData.studType = btn.dataset.type;
            
            document.getElementById('studs-conical').style.display = 'none';
            document.getElementById('studs-bladed').style.display = 'none';
            document.getElementById('studs-mixed').style.display = 'none';
            
            document.getElementById('studs-' + btn.dataset.type).style.display = 'block';
        });
    });

    // ═══ Add to Cart ═══"""
html = html.replace(old_js2, new_js2)

with open('templates/customizer.html', 'w', encoding='utf-8') as f:
    f.write(html)
