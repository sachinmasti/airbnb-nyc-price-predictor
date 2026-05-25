// AuraBnb - Script

// ── Particle Background ──────────────────────────────────────────────────────
(function initParticles() {
    const canvas = document.getElementById('bg-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let W = window.innerWidth, H = window.innerHeight;
    canvas.width = W; canvas.height = H;

    window.addEventListener('resize', () => {
        W = canvas.width  = window.innerWidth;
        H = canvas.height = window.innerHeight;
        init();
    });

    const COUNT   = Math.min(Math.floor(W * H / 14000), 90);
    const COLORS  = ['#ff5a5f', '#ec4899', '#8b5cf6', '#0ea5e9'];
    const MAX_DIST = 140;

    class Dot {
        constructor() { this.reset(true); }
        reset(init = false) {
            this.x  = Math.random() * W;
            this.y  = init ? Math.random() * H : H + 5;
            this.r  = Math.random() * 1.8 + 0.5;
            this.vx = (Math.random() - 0.5) * 0.35;
            this.vy = -(Math.random() * 0.4 + 0.1);
            this.color = COLORS[Math.floor(Math.random() * COLORS.length)];
            this.alpha = Math.random() * 0.5 + 0.2;
            this.pulse = Math.random() * Math.PI * 2; // phase offset for twinkle
        }
        update() {
            this.x += this.vx;
            this.y += this.vy;
            this.pulse += 0.025;
            if (this.y < -10) this.reset();
        }
        draw() {
            const twinkle = this.alpha * (0.7 + 0.3 * Math.sin(this.pulse));
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
            ctx.fillStyle = hexToRGBA(this.color, twinkle);
            ctx.fill();
        }
    }

    let dots = [];
    function init() { dots = Array.from({ length: COUNT }, () => new Dot()); }

    function drawConnections() {
        for (let i = 0; i < dots.length; i++) {
            for (let j = i + 1; j < dots.length; j++) {
                const dx = dots[i].x - dots[j].x;
                const dy = dots[i].y - dots[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < MAX_DIST) {
                    const opacity = (1 - dist / MAX_DIST) * 0.08;
                    ctx.beginPath();
                    ctx.moveTo(dots[i].x, dots[i].y);
                    ctx.lineTo(dots[j].x, dots[j].y);
                    ctx.strokeStyle = `rgba(255,255,255,${opacity})`;
                    ctx.lineWidth = 0.6;
                    ctx.stroke();
                }
            }
        }
    }

    function hexToRGBA(hex, alpha) {
        const r = parseInt(hex.slice(1,3),16);
        const g = parseInt(hex.slice(3,5),16);
        const b = parseInt(hex.slice(5,7),16);
        return `rgba(${r},${g},${b},${alpha})`;
    }

    function loop() {
        ctx.clearRect(0, 0, W, H);
        drawConnections();
        dots.forEach(d => { d.update(); d.draw(); });
        requestAnimationFrame(loop);
    }

    init();
    loop();
})();
// ─────────────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const nameInput = document.getElementById('name');
    const charCounter = document.getElementById('char-counter');
    const boroSelect = document.getElementById('neighbourhood_group');
    const neighSelect = document.getElementById('neighbourhood');
    const form = document.getElementById('prediction-form');
    const btnSubmit = document.getElementById('btn-submit');
    const btnText = btnSubmit.querySelector('.btn-text');
    const btnLoader = btnSubmit.querySelector('.btn-loader');
    
    // Result Elements
    const priceDisplay = document.getElementById('predicted-price');
    const detailDistance = document.getElementById('detail-distance');
    const detailExtracted = document.getElementById('detail-extracted');
    const detailCoords = document.getElementById('detail-coords');
    
    // Keyword Badges
    const badges = {
        luxury: { el: document.getElementById('badge-luxury'), words: ['luxury', 'luxurious', 'penthouse', 'high-end', 'modernist', 'elegant'] },
        cozy: { el: document.getElementById('badge-cozy'), words: ['cozy', 'cosy', 'charming', 'sweet', 'warm', 'cute'] },
        studio: { el: document.getElementById('badge-studio'), words: ['studio', 'loft', '1-bedroom', '1br', 'efficiency'] },
        subway: { el: document.getElementById('badge-subway'), words: ['subway', 'train', 'metro', 'transit', 'bus', 'station'] }
    };

    let locationsMap = {};

    // 1. Fetch locations mapping from backend
    fetch('/api/locations')
        .then(response => response.json())
        .then(data => {
            locationsMap = data;
            
            // Populate Borough dropdown
            boroSelect.innerHTML = '<option value="" disabled selected>Select Borough</option>';
            Object.keys(locationsMap).sort().forEach(boro => {
                const option = document.createElement('option');
                option.value = boro;
                option.textContent = boro;
                boroSelect.appendChild(option);
            });
        })
        .catch(err => {
            console.error('Failed to load borough options:', err);
            boroSelect.innerHTML = '<option value="" disabled>Error loading Boroughs</option>';
        });

    // 2. Dynamic Neighbourhood Population on Borough Change
    boroSelect.addEventListener('change', () => {
        const selectedBoro = boroSelect.value;
        neighSelect.disabled = false;
        
        neighSelect.innerHTML = '<option value="" disabled selected>Select Neighbourhood</option>';
        if (locationsMap[selectedBoro]) {
            locationsMap[selectedBoro].forEach(neigh => {
                const option = document.createElement('option');
                option.value = neigh;
                option.textContent = neigh;
                neighSelect.appendChild(option);
            });
        }
    });

    // 3. Real-time Name Feature Flag Highlighting
    nameInput.addEventListener('input', () => {
        const text = nameInput.value;
        const textLower = text.toLowerCase();
        
        // Update character counter
        charCounter.textContent = text.length;
        
        // Highlight active badges
        Object.keys(badges).forEach(key => {
            const badge = badges[key];
            const isActive = badge.words.some(word => textLower.includes(word));
            if (isActive) {
                badge.el.classList.add('active');
            } else {
                badge.el.classList.remove('active');
            }
        });
    });

    // 4. Form Submission and Price Prediction
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Disable button & show loader
        btnSubmit.disabled = true;
        btnLoader.style.display = 'inline-block';
        btnText.textContent = 'Estimating...';
        
        // Collect form data
        const payload = {
            name: nameInput.value,
            neighbourhood_group: boroSelect.value,
            neighbourhood: neighSelect.value,
            room_type: document.getElementById('room_type').value,
            minimum_nights: parseInt(document.getElementById('minimum_nights').value, 10),
            number_of_reviews: parseInt(document.getElementById('number_of_reviews').value, 10),
            availability_365: parseInt(document.getElementById('availability_365').value, 10)
        };

        // Call backend API
        fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            // Restore button state
            btnSubmit.disabled = false;
            btnLoader.style.display = 'none';
            btnText.textContent = 'Estimate Price';

            if (data.success) {
                // Animate predicted price count-up
                animatePrice(data.prediction);

                // Populate details cards
                detailDistance.textContent = `${data.derived_features.distance_to_times_square_km} km`;
                
                // Show detected features list
                const activeFeatures = [];
                if (data.derived_features.is_luxury) activeFeatures.push('Luxury');
                if (data.derived_features.is_cozy) activeFeatures.push('Cozy');
                if (data.derived_features.is_studio) activeFeatures.push('Studio');
                if (data.derived_features.is_subway) activeFeatures.push('Subway');
                
                detailExtracted.textContent = activeFeatures.length > 0 ? activeFeatures.join(', ') : 'None detected';
                if (data.model_mode === 'fallback') {
                    detailExtracted.textContent += ' · Fallback estimate';
                }
                
                // Coordinates
                detailCoords.textContent = `${payload.neighbourhood_group} Centroid`;
            } else {
                const details = data.details ? `\n\nDetails: ${data.details}` : '';
                alert(`Error: ${data.error || 'Something went wrong.'}${details}`);
            }
        })
        .catch(err => {
            console.error('Prediction request failed:', err);
            btnSubmit.disabled = false;
            btnLoader.style.display = 'none';
            btnText.textContent = 'Estimate Price';
            alert('Server error. Make sure the backend Flask app is running.');
        });
    });

    // Helper: Price count-up animation
    function animatePrice(targetVal) {
        let currentVal = 0;
        const duration = 800; // ms
        const steps = 40;
        const stepTime = duration / steps;
        const stepVal = targetVal / steps;
        
        const timer = setInterval(() => {
            currentVal += stepVal;
            if (currentVal >= targetVal) {
                currentVal = targetVal;
                clearInterval(timer);
            }
            priceDisplay.textContent = Math.round(currentVal);
        }, stepTime);
    }
});
