import re

with open(r'C:\Users\SB Info\.gemini\antigravity\scratch\football_boots_store\templates\jerseys.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add data-id to buttons
content = content.replace('<button class="btn-add-jersey">', '<button class="btn-add-jersey" data-id="{{ j.id }}">')

# Add JS logic
js_logic = """
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
    document.querySelectorAll('.btn-add-jersey').forEach(btn => {
        btn.addEventListener('click', function() {
            const jerseyId = this.getAttribute('data-id');
            const button = this;
            
            fetch('/api/cart/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ jersey_id: jerseyId })
            }).then(res => res.json()).then(data => {
                if(data.success) {
                    const originalText = button.innerHTML;
                    button.innerHTML = '<i class="fa-solid fa-check me-2"></i> Added!';
                    button.style.backgroundColor = '#28a745';
                    button.style.borderColor = '#28a745';
                    
                    setTimeout(() => {
                        button.innerHTML = originalText;
                        button.style.backgroundColor = '';
                        button.style.borderColor = '';
                    }, 2000);
                }
            }).catch(err => console.error(err));
        });
    });
</script>
</body>
"""
content = content.replace('<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>\n</body>', js_logic)

with open(r'C:\Users\SB Info\.gemini\antigravity\scratch\football_boots_store\templates\jerseys.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated jerseys.html")
