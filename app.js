// Dev Boot Finder - Frontend Core Application Logic with Boot Finder Recommendation Engine

document.addEventListener('DOMContentLoaded', () => {
    // Parse URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const initialSearch = urlParams.get('search') || '';

    // State Management for Catalog
    let state = {
        gender: 'Male',
        position: '',
        brands: [],
        maxPrice: 300,
        searchQuery: initialSearch,
        sortBy: 'default',
        studType: '',
        bootCategory: '',
        era: ''
    };

    // Store fetched boots for client-side sorting/operations
    let currentBootsList = [];
    let lockerCount = 0;
    
    // Boot Finder Wizard State
    let wizardStep = 1;
    let recommendationMatch = null;

    // DOM Elements - Catalog
    const productGrid = document.getElementById('product-grid');
    const resultsCount = document.getElementById('results-count');
    const loader = document.getElementById('loader');
    const noResults = document.getElementById('no-results');
    const activeBadgesList = document.getElementById('active-badges-list');
    
    // Filters & Sorting Input Elements
    const genderTabs = document.querySelectorAll('.gender-tab');
    const positionCards = document.querySelectorAll('.position-card');
    const brandFilters = document.querySelectorAll('.brand-filter');
    const priceRange = document.getElementById('price-range');
    const priceVal = document.getElementById('price-val');
    const sortSelect = document.getElementById('sort-select');
    const headerSearch = document.getElementById('header-search');
    const resetFiltersBtn = document.getElementById('reset-filters-btn');
    
    // Modal Elements
    const detailModal = document.getElementById('detail-modal');
    const modalClose = document.getElementById('modal-close');
    const modalImg = document.getElementById('modal-img');
    const modalName = document.getElementById('modal-name');
    const modalPrice = document.getElementById('modal-price-tag');
    const modalDesc = document.getElementById('modal-desc-tag');
    const modalFeaturesList = document.getElementById('modal-features-list');
    const modalLegendsList = document.getElementById('modal-legends-list');
    const modalBrandTag = document.getElementById('modal-brand-tag');
    const modalPositionTag = document.getElementById('modal-position-tag');
    const modalColorwayTag = document.getElementById('modal-colorway-tag');
    const modalRatingTag = document.getElementById('modal-rating-tag');
    const lockerBadge = document.querySelector('.cart-badge');

    // Toast Elements
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toast-msg');

    // Boot Finder Wizard DOM Elements
    const finderWizard = document.getElementById('finder-wizard');
    const finderResultBanner = document.getElementById('finder-result-banner');
    const wizardStepElements = document.querySelectorAll('.wizard-step');
    const stepIndicators = document.querySelectorAll('.step-indicator');
    const wizardPrevBtn = document.getElementById('wizard-prev-btn');
    const wizardNextBtn = document.getElementById('wizard-next-btn');

    // Recommendation Banner DOM Elements
    const recommendBootName = document.getElementById('recommend-boot-name');
    const recommendPriorityBadge = document.getElementById('recommend-priority-badge');
    const recommendBootDesc = document.getElementById('recommend-boot-desc');
    const recommendBootPrice = document.getElementById('recommend-boot-price');
    const recommendBootRating = document.getElementById('recommend-boot-rating');
    const recommendBootLegends = document.getElementById('recommend-boot-legends');
    const recommendBootImg = document.getElementById('recommend-boot-img');
    const recommendViewBtn = document.getElementById('recommend-view-btn');
    const recommendResetBtn = document.getElementById('recommend-reset-btn');

    // Initialize Application
    init();

    function init() {
        if (state.searchQuery && headerSearch) {
            headerSearch.value = state.searchQuery;
        }
        fetchBoots();
        setupEventListeners();
        setupWizard();
    }

    // --- EVENT LISTENERS ---
    function setupEventListeners() {
        // Gender switching (Male / Female Main Sections)
        genderTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                genderTabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                state.gender = tab.getAttribute('data-gender');
                fetchBoots();
            });
        });

        // Position switching (GK, DEF, MID, ATT Subsections)
        positionCards.forEach(card => {
            card.addEventListener('click', () => {
                const selectedPos = card.getAttribute('data-position');
                
                if (state.position === selectedPos) {
                    state.position = '';
                    card.classList.remove('active');
                } else {
                    positionCards.forEach(c => c.classList.remove('active'));
                    card.classList.add('active');
                    state.position = selectedPos;
                }
                
                fetchBoots();

                // Smooth scroll to catalog grid
                document.getElementById('catalog-section').scrollIntoView({ behavior: 'smooth' });
            });
        });

        // Brand selection changes
        brandFilters.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                updateBrandState();
                fetchBoots();
            });
        });

        // Price slider inputs
        priceRange.addEventListener('input', (e) => {
            priceVal.textContent = `$${e.target.value}`;
            state.maxPrice = parseFloat(e.target.value);
        });

        priceRange.addEventListener('change', () => {
            fetchBoots();
        });

        // Search text input (search both boots and players)
        headerSearch.addEventListener('input', (e) => {
            state.searchQuery = e.target.value.trim();
            fetchBoots();
        });

        // Sorting changes
        sortSelect.addEventListener('change', (e) => {
            state.sortBy = e.target.value;
            processAndRender();
        });

        // Reset Filters action
        resetFiltersBtn.addEventListener('click', resetAllFilters);

        // ── Stud Type chips ──────────────────────────────────────────────────
        const studChips = document.querySelectorAll('#stud-filter-chips .stud-chip');
        studChips.forEach(chip => {
            chip.addEventListener('click', () => {
                studChips.forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
                state.studType = chip.getAttribute('data-stud') || '';
                fetchBoots();
            });
        });

        // ── Boot Category chips ──────────────────────────────────────────────
        const catChips = document.querySelectorAll('#category-filter-chips .stud-chip');
        catChips.forEach(chip => {
            chip.addEventListener('click', () => {
                catChips.forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
                state.bootCategory = chip.getAttribute('data-cat') || '';
                fetchBoots();
            });
        });

        // Modal close button
        modalClose.addEventListener('click', closeModal);
        detailModal.addEventListener('click', (e) => {
            if (e.target === detailModal) {
                closeModal();
            }
        });

        // Locker Add action
        document.querySelector('.add-to-cart-action').addEventListener('click', () => {
            lockerCount++;
            lockerBadge.textContent = lockerCount;
            showToast("Boot added to your Locker!");
            closeModal();
        });

        // filterEra custom event (fired from vintage section buttons)
        document.addEventListener('filterEra', (e) => {
            const era = e.detail.era || '';
            state.era = era;
            state.studType = '';
            state.bootCategory = '';
            document.querySelectorAll('#stud-filter-chips .stud-chip').forEach((c, i) => c.classList.toggle('active', i === 0));
            document.querySelectorAll('#category-filter-chips .stud-chip').forEach((c, i) => c.classList.toggle('active', i === 0));
            fetchBoots();
        });
    }

    // --- BOOT FINDER WIZARD HANDLERS ---
    function setupWizard() {
        // Next Step Action
        wizardNextBtn.addEventListener('click', () => {
            if (wizardStep < 3) {
                wizardStep++;
                updateWizardUI();
            } else {
                generateRecommendation();
            }
        });

        // Previous Step Action
        wizardPrevBtn.addEventListener('click', () => {
            if (wizardStep > 1) {
                wizardStep--;
                updateWizardUI();
            }
        });

        // Reset Recommendation wizard
        recommendResetBtn.addEventListener('click', () => {
            finderResultBanner.style.display = 'none';
            finderWizard.style.display = 'block';
            wizardStep = 1;
            updateWizardUI();
            
            // Clear checked radios to restart
            document.querySelectorAll('.option-card input[type="radio"]').forEach((radio, index) => {
                if (index === 0 || index === 2 || index === 6) { // Default selections
                    radio.checked = true;
                } else {
                    radio.checked = false;
                }
            });
        });

        // Trigger Detailed view from recommendation
        recommendViewBtn.addEventListener('click', () => {
            if (recommendationMatch) {
                window.location.href = '/boot/' + recommendationMatch.id;
            }
        });
    }

    function updateWizardUI() {
        // Toggle Step Screens
        wizardStepElements.forEach(step => {
            step.classList.remove('active');
            if (parseInt(step.getAttribute('data-step')) === wizardStep) {
                step.classList.add('active');
            }
        });

        // Toggle Indicators
        stepIndicators.forEach(indicator => {
            indicator.classList.remove('active');
            if (parseInt(indicator.getAttribute('data-step')) === wizardStep) {
                indicator.classList.add('active');
            }
        });

        // Configure Buttons
        if (wizardStep === 1) {
            wizardPrevBtn.disabled = true;
            wizardNextBtn.textContent = 'Next Step';
        } else if (wizardStep === 2) {
            wizardPrevBtn.disabled = false;
            wizardNextBtn.textContent = 'Next Step';
        } else if (wizardStep === 3) {
            wizardPrevBtn.disabled = false;
            wizardNextBtn.textContent = 'Generate Recommendation';
        }
    }

    function generateRecommendation() {
        // Gather selected parameters
        const gender = document.querySelector('input[name="finder-gender"]:checked').value;
        const position = document.querySelector('input[name="finder-position"]:checked').value;
        const priority = document.querySelector('input[name="finder-priority"]:checked').value;

        showLoader(true);

        // Fetch query to match recommendation criteria
        fetch(`/api/boots?gender=${gender}&position=${position}&priority=${priority}`)
            .then(res => res.json())
            .then(boots => {
                showLoader(false);
                if (boots.length > 0) {
                    // Pick the highest rated boot that matches
                    boots.sort((a, b) => b.rating - a.rating);
                    recommendationMatch = boots[0];
                    displayRecommendation(recommendationMatch);
                } else {
                    // Fallback to position + gender match if strict priority is empty
                    fetch(`/api/boots?gender=${gender}&position=${position}`)
                        .then(res => res.json())
                        .then(fallbackBoots => {
                            if (fallbackBoots.length > 0) {
                                fallbackBoots.sort((a, b) => b.rating - a.rating);
                                recommendationMatch = fallbackBoots[0];
                                displayRecommendation(recommendationMatch);
                            } else {
                                showToast("No matching boot profile found.", true);
                            }
                        });
                }
            })
            .catch(err => {
                console.error(err);
                showLoader(false);
                showToast("Error processing recommendation.", true);
            });
    }

    function displayRecommendation(boot) {
        // Hydrate Banner
        recommendBootName.textContent = boot.name;
        recommendPriorityBadge.textContent = boot.priority;
        recommendBootDesc.textContent = boot.description;
        recommendBootPrice.textContent = `$${boot.price.toFixed(2)}`;
        recommendBootRating.innerHTML = `<i class="fa-solid fa-star"></i> ${boot.rating.toFixed(1)} Rating`;
        recommendBootImg.src = boot.image_url;
        recommendBootImg.alt = boot.name;

        // Populate Legends
        recommendBootLegends.innerHTML = '';
        boot.legends.forEach(player => {
            const span = document.createElement('span');
            span.className = 'legend-pill';
            span.textContent = player;
            recommendBootLegends.appendChild(span);
        });

        // Hide Wizard, Show Banner
        finderWizard.style.display = 'none';
        finderResultBanner.style.display = 'grid';

        // Apply filters to main catalog below as well, syncing catalog view
        syncCatalogToRecommendation(boot.gender, boot.position);
    }

    function syncCatalogToRecommendation(gender, position) {
        // Sync Gender tab
        genderTabs.forEach(t => {
            t.classList.remove('active');
            if (t.getAttribute('data-gender') === gender) t.classList.add('active');
        });
        state.gender = gender;

        // Sync Position Card
        positionCards.forEach(c => {
            c.classList.remove('active');
            if (c.getAttribute('data-position') === position) c.classList.add('active');
        });
        state.position = position;

        // Trigger Catalog refresh
        fetchBoots();
    }

    // --- STATE MODIFIERS ---
    function updateBrandState() {
        state.brands = Array.from(brandFilters)
            .filter(i => i.checked)
            .map(i => i.value);
    }

    function resetAllFilters() {
        state.position = '';
        state.brands = [];
        state.maxPrice = 300;
        state.searchQuery = '';
        state.sortBy = 'default';
        state.studType = '';
        state.bootCategory = '';
        state.era = '';

        // Reset DOM inputs
        positionCards.forEach(c => c.classList.remove('active'));
        brandFilters.forEach(cb => cb.checked = false);
        priceRange.value = 300;
        priceVal.textContent = '$300';
        headerSearch.value = '';
        sortSelect.value = 'default';

        // Reset stud chips
        document.querySelectorAll('#stud-filter-chips .stud-chip').forEach((c, i) => c.classList.toggle('active', i === 0));
        document.querySelectorAll('#category-filter-chips .stud-chip').forEach((c, i) => c.classList.toggle('active', i === 0));

        // Synchronize Active Gender Tab
        const activeTab = document.querySelector('.gender-tab.active');
        state.gender = activeTab ? activeTab.getAttribute('data-gender') : 'Male';

        fetchBoots();
    }

    // --- API OPERATIONS ---
    function fetchBoots() {
        showLoader(true);

        let params = new URLSearchParams();
        if (state.gender)       params.append('gender',        state.gender);
        if (state.position)     params.append('position',      state.position);
        if (state.brands.length > 0) params.append('brands', state.brands.join(','));
        if (state.searchQuery)  params.append('search',        state.searchQuery);
        if (state.maxPrice < 300) params.append('max_price',   state.maxPrice);
        if (state.studType)     params.append('stud_types',    state.studType);
        if (state.bootCategory) params.append('boot_category', state.bootCategory);
        if (state.era)          params.append('era',           state.era);

        fetch(`/api/boots?${params.toString()}`)
            .then(res => {
                if (!res.ok) throw new Error("API call error");
                return res.json();
            })
            .then(data => {
                currentBootsList = data;
                processAndRender();
                showLoader(false);
            })
            .catch(err => {
                console.error(err);
                showLoader(false);
                showToast("Error retrieving boot catalog.", true);
            });
    }

    // Client-side sort and final UI render
    function processAndRender() {
        let boots = [...currentBootsList];

        if (state.sortBy === 'price-low') {
            boots.sort((a, b) => a.price - b.price);
        } else if (state.sortBy === 'price-high') {
            boots.sort((a, b) => b.price - a.price);
        } else if (state.sortBy === 'rating') {
            boots.sort((a, b) => b.rating - a.rating);
        }

        renderBadges();
        renderProductGrid(boots);
    }

    // --- DOM RENDERING ---
    function renderProductGrid(boots) {
        productGrid.innerHTML = '';
        resultsCount.textContent = `Showing ${boots.length} boot${boots.length === 1 ? '' : 's'}`;

        if (boots.length === 0) {
            noResults.style.display = 'block';
            productGrid.style.display = 'none';
            return;
        }

        noResults.style.display = 'none';
        productGrid.style.display = 'grid';

        boots.forEach(boot => {
            const card = document.createElement('div');
            card.classList.add('product-card');
            card.setAttribute('data-position', boot.position);

            const legendsHtml = boot.legends.length > 0
                ? `<div class="card-legends"><i class="fa-solid fa-shield-halved"></i> Worn by: ${boot.legends.slice(0, 2).join(', ')}</div>`
                : '';

            const studType  = boot.stud_type  || 'FG';
            const studLabel = {
                FG:'Firm Ground', SG:'Soft Ground', AG:'Artificial', TF:'Turf',
                IC:'Indoor', HG:'Hard Ground', MG:'Multi Ground'
            }[studType] || studType;

            const eraHtml = (boot.era === 'Vintage')
                ? `<span class="era-badge-vintage"><i class="fa-solid fa-clock-rotate-left"></i> Vintage</span>`
                : '';

            card.innerHTML = `
                <div class="card-img-container">
                    <div class="card-badges">
                        <span class="card-badge badge-brand">${boot.brand}</span>
                        <span class="card-badge badge-pos">${boot.position}</span>
                    </div>
                    <img src="${boot.image_url}" alt="${boot.name}" loading="lazy">
                </div>
                <div class="card-details">
                    <div class="card-rating">
                        <i class="fa-solid fa-star"></i>
                        <span>${boot.rating.toFixed(1)}</span>
                        <span class="stud-type-badge stud-${studType}" style="margin-left:auto">${studType}</span>
                        <span class="boot-cat-chip">${boot.boot_category}</span>
                        ${eraHtml}
                    </div>
                    <h3>${boot.name}</h3>
                    <div class="card-colorway">${boot.colorway}</div>
                    <div class="boot-surface-label"><i class="fa-solid fa-map-marker-alt"></i> ${studLabel} &mdash; ${boot.surface}</div>
                    ${legendsHtml}
                    <p class="card-desc">${boot.description}</p>
                    <div class="card-footer">
                        <span class="card-price">$${boot.price.toFixed(2)}</span>
                        <button class="card-btn details-action-btn" data-id="${boot.id}">View Details</button>
                    </div>
                </div>
            `;

            card.querySelector('.details-action-btn').addEventListener('click', () => {
                window.location.href = '/boot/' + boot.id;
            });

            productGrid.appendChild(card);
        });
    }

    function renderBadges() {
        activeBadgesList.innerHTML = '';
        
        if (state.position) {
            createBadge(state.position, () => {
                state.position = '';
                positionCards.forEach(c => c.classList.remove('active'));
                fetchBoots();
            });
        }

        state.brands.forEach(brand => {
            createBadge(brand, () => {
                state.brands = state.brands.filter(b => b !== brand);
                const checkbox = Array.from(brandFilters).find(cb => cb.value === brand);
                if (checkbox) checkbox.checked = false;
                fetchBoots();
            });
        });

        if (state.maxPrice < 300) {
            createBadge(`Max $${state.maxPrice}`, () => {
                state.maxPrice = 300;
                priceRange.value = 300;
                priceVal.textContent = '$300';
                fetchBoots();
            });
        }
    }

    function createBadge(text, onRemove) {
        const pill = document.createElement('span');
        pill.classList.add('badge-pill');
        pill.innerHTML = `
            <span>${text}</span>
            <button aria-label="Remove filter"><i class="fa-solid fa-xmark"></i></button>
        `;
        pill.querySelector('button').addEventListener('click', onRemove);
        activeBadgesList.appendChild(pill);
    }

    function showLoader(visible) {
        loader.style.display = visible ? 'flex' : 'none';
        if (visible) {
            productGrid.style.display = 'none';
            noResults.style.display = 'none';
        }
    }

    // --- MODAL OPERATIONS ---
    function openModal(bootId) {
        fetch(`/api/boots/${bootId}`)
            .then(res => res.json())
            .then(boot => {
                if (boot.error) {
                    showToast(boot.error, true);
                    return;
                }
                
                modalImg.src = boot.image_url;
                modalImg.alt = boot.name;
                modalName.textContent = boot.name;
                modalPrice.textContent = `$${boot.price.toFixed(2)}`;
                modalDesc.textContent = boot.description;
                modalBrandTag.textContent = boot.brand;
                modalPositionTag.textContent = boot.position;
                modalColorwayTag.textContent = boot.colorway;
                modalRatingTag.innerHTML = `<i class="fa-solid fa-star"></i> ${boot.rating.toFixed(1)}`;
                
                // Stud Type Badge in modal
                const modalStudTag = document.getElementById('modal-stud-tag');
                if (modalStudTag) {
                    const st = boot.stud_type || 'FG';
                    modalStudTag.textContent = st;
                    modalStudTag.className = `modal-badge stud-badge stud-type-badge stud-${st}`;
                }

                // Color Code Position Tag
                modalPositionTag.style.borderColor = `var(--color-${boot.position.toLowerCase().substring(0, 3)})`;
                modalPositionTag.style.color = `var(--color-${boot.position.toLowerCase().substring(0, 3)})`;

                // Render legends list
                modalLegendsList.innerHTML = '';
                boot.legends.forEach(player => {
                    const span = document.createElement('span');
                    span.className = 'legend-pill';
                    span.textContent = player;
                    modalLegendsList.appendChild(span);
                });

                // Render Specifications list with surface info prepended
                modalFeaturesList.innerHTML = '';
                const surfaceLi = document.createElement('li');
                surfaceLi.innerHTML = `<strong style="color:var(--accent-blue)">Surface:</strong> ${boot.surface}`;
                modalFeaturesList.appendChild(surfaceLi);
                boot.key_features.forEach(feat => {
                    const li = document.createElement('li');
                    li.textContent = feat;
                    modalFeaturesList.appendChild(li);
                });

                detailModal.classList.add('open');
                document.body.style.overflow = 'hidden'; 
            })
            .catch(err => {
                console.error(err);
                showToast("Failed to retrieve boot details.", true);
            });
    }

    function closeModal() {
        detailModal.classList.remove('open');
        document.body.style.overflow = ''; 
    }

    // --- TOAST NOTIFICATIONS ---
    function showToast(message, isError = false) {
        toastMsg.textContent = message;
        if (isError) {
            toast.style.borderColor = 'var(--accent-pink)';
            toast.querySelector('i').className = 'fa-solid fa-circle-exclamation';
            toast.querySelector('i').style.color = 'var(--accent-pink)';
        } else {
            toast.style.borderColor = 'var(--accent-green)';
            toast.querySelector('i').className = 'fa-solid fa-circle-check';
            toast.querySelector('i').style.color = 'var(--accent-green)';
        }
        
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
});

// ── User avatar dropdown toggle ────────────────────────────────────────────────
(function() {
    const avatarBtn  = document.getElementById('user-avatar-btn');
    const dropMenu   = document.getElementById('user-dropdown-menu');

    if (!avatarBtn || !dropMenu) return;

    avatarBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = dropMenu.classList.toggle('open');
        avatarBtn.classList.toggle('open', isOpen);
    });

    // Close when clicking outside
    document.addEventListener('click', () => {
        dropMenu.classList.remove('open');
        avatarBtn.classList.remove('open');
    });
})();

// ── Global helper: surface card "Filter XX Boots" button  ─────────────────────
// Called via onclick="filterByStud('FG')" from surface guide cards
function filterByStud(studCode) {
    // Activate matching stud chip in sidebar
    const chips = document.querySelectorAll('#stud-filter-chips .stud-chip');
    chips.forEach(c => {
        const isTarget = c.getAttribute('data-stud') === studCode;
        c.classList.toggle('active', isTarget);
    });

    // Scroll to catalog
    const catalog = document.getElementById('catalog-section');
    if (catalog) catalog.scrollIntoView({ behavior: 'smooth' });

    // Trigger click on the matching chip to fire its event listener
    const target = document.querySelector(`#stud-filter-chips [data-stud="${studCode}"]`);
    if (target) target.click();
}
