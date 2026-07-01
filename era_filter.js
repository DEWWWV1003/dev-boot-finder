// filterByEra – called from vintage section buttons
function filterByEra(era) {
    // Reset stud + cat chips to "All"
    document.querySelectorAll('#stud-filter-chips .stud-chip').forEach((c, i) => c.classList.toggle('active', i === 0));
    document.querySelectorAll('#category-filter-chips .stud-chip').forEach((c, i) => c.classList.toggle('active', i === 0));

    // Scroll to catalog
    const catalog = document.getElementById('catalog-section');
    if (catalog) catalog.scrollIntoView({ behavior: 'smooth' });

    // Dispatch custom event for the DOMContentLoaded listener
    document.dispatchEvent(new CustomEvent('filterEra', { detail: { era } }));
}
