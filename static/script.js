document.addEventListener('DOMContentLoaded', () => {
    // ----------------------------------------------------
    // Tab Navigation
    // ----------------------------------------------------
    const navButtons = document.querySelectorAll('.nav-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');
            
            navButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(tab => tab.classList.remove('active'));

            button.classList.add('active');
            const targetTab = document.getElementById(tabId);
            if (targetTab) {
                targetTab.classList.add('active');
            }
        });
    });

    // ----------------------------------------------------
    // Input Data Binding (Slider <-> Number Inputs)
    // ----------------------------------------------------
    const sliders = document.querySelectorAll('.range-slider');
    sliders.forEach(slider => {
        const bindId = slider.getAttribute('data-bind');
        const numInput = document.getElementById(bindId);

        if (numInput) {
            // Slider changes -> update number input
            slider.addEventListener('input', (e) => {
                numInput.value = e.target.value;
            });

            // Number input changes -> update slider
            numInput.addEventListener('input', (e) => {
                let val = parseFloat(e.target.value);
                if (isNaN(val)) val = parseFloat(slider.min);
                if (val < parseFloat(slider.min)) val = parseFloat(slider.min);
                if (val > parseFloat(slider.max)) val = parseFloat(slider.max);
                slider.value = val;
            });
        }
    });

    // ----------------------------------------------------
    // Load Model Metrics & Feature Importance Chart
    // ----------------------------------------------------
    let importanceChart = null;
    let probabilityChart = null;

    async function loadMetrics() {
        try {
            const response = await fetch('/api/metrics');
            if (!response.ok) throw new Error('Failed to fetch metrics');
            const data = await response.json();

            // Populate Metrics
            // Random Forest
            document.getElementById('rf-accuracy').textContent = (data.random_forest.accuracy * 100).toFixed(1) + '%';
            document.getElementById('rf-precision').textContent = (data.random_forest.precision * 100).toFixed(1) + '%';
            document.getElementById('rf-recall').textContent = (data.random_forest.recall * 100).toFixed(1) + '%';
            document.getElementById('rf-f1').textContent = (data.random_forest.f1_score * 100).toFixed(1) + '%';

            // Decision Tree
            document.getElementById('dt-accuracy').textContent = (data.decision_tree.accuracy * 100).toFixed(1) + '%';
            document.getElementById('dt-precision').textContent = (data.decision_tree.precision * 100).toFixed(1) + '%';
            document.getElementById('dt-recall').textContent = (data.decision_tree.recall * 100).toFixed(1) + '%';
            document.getElementById('dt-f1').textContent = (data.decision_tree.f1_score * 100).toFixed(1) + '%';

            // Render Feature Importance Chart
            renderImportanceChart(data.feature_importances);

        } catch (error) {
            console.error('Error loading metrics:', error);
            // Default placeholder display in case backend isn't ready
        }
    }

    function renderImportanceChart(importances) {
        const ctx = document.getElementById('importance-chart').getContext('2d');
        
        // Map feature names to user-friendly titles
        const featureLabels = {
            'N': 'Nitrogen (N)',
            'P': 'Phosphorus (P)',
            'K': 'Potassium (K)',
            'temperature': 'Temperature',
            'humidity': 'Humidity',
            'ph': 'Soil pH',
            'rainfall': 'Rainfall'
        };

        const labels = importances.map(item => featureLabels[item.feature] || item.feature);
        const values = importances.map(item => item.importance * 100);

        if (importanceChart) {
            importanceChart.destroy();
        }

        importanceChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Feature Importance %',
                    data: values,
                    backgroundColor: 'rgba(16, 185, 129, 0.45)',
                    borderColor: 'rgba(16, 185, 129, 1)',
                    borderWidth: 1.5,
                    borderRadius: 6,
                    hoverBackgroundColor: 'rgba(52, 211, 153, 0.7)'
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Importance: ${context.parsed.x.toFixed(1)}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { color: 'rgba(255, 255, 255, 0.6)' }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: 'rgba(255, 255, 255, 0.85)', font: { family: 'Outfit', size: 12 } }
                    }
                }
            }
        });
    }

    // ----------------------------------------------------
    // Recommendation Form Submit
    // ----------------------------------------------------
    const form = document.getElementById('recommendation-form');
    const resultContainer = document.getElementById('result-container');
    const resultPlaceholder = resultContainer.querySelector('.result-placeholder');
    const resultContent = resultContainer.querySelector('.result-content');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Collect inputs
        const formData = new FormData(form);
        const payload = {};
        formData.forEach((value, key) => {
            payload[key] = parseFloat(value);
        });

        // Show loading/placeholder status
        resultPlaceholder.querySelector('h3').textContent = "Analyzing soil profile...";
        resultPlaceholder.querySelector('p').textContent = "Running Random Forest decision tree nodes prediction...";
        resultPlaceholder.classList.remove('hidden');
        resultContent.classList.add('hidden');

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Server error occurred');
            }

            const data = await response.json();
            displayRecommendation(data);

        } catch (error) {
            alert('Prediction error: ' + error.message);
            resultPlaceholder.querySelector('h3').textContent = "Awaiting Input parameters";
            resultPlaceholder.querySelector('p').textContent = "Fill out the soil profile and environmental parameters, then click the button to generate a recommendation.";
        }
    });

    function displayRecommendation(data) {
        resultPlaceholder.classList.add('hidden');
        resultContent.classList.remove('hidden');

        // Capitalize recommended crop name
        const cropName = data.prediction.charAt(0).toUpperCase() + data.prediction.slice(1);
        document.getElementById('recommended-crop-name').textContent = cropName;

        // Confidence progress ring
        const confPercent = Math.round(data.confidence * 100);
        document.getElementById('confidence-percentage').textContent = `${confPercent}%`;
        
        const circle = resultContent.querySelector('.progress-ring-bar');
        const radius = circle.r.baseVal.value;
        const circumference = radius * 2 * Math.PI;
        circle.style.strokeDasharray = `${circumference} ${circumference}`;
        
        // Progress animation offset
        const offset = circumference - (data.confidence * circumference);
        circle.style.strokeDashoffset = offset;

        // Justification text
        document.getElementById('crop-justification').textContent = getJustification(cropName, data.input);

        // Alternatives distribution chart
        renderProbabilityChart(data.recommendations);
    }

    function getJustification(crop, inputs) {
        const explanations = {
            'Rice': `Rice is recommended because it is a highly water-intensive crop requiring high humidity (${inputs.humidity.toFixed(0)}%) and heavy rainfall (${inputs.rainfall.toFixed(0)}mm). The soil nitrogen (${inputs.N}) and potassium (${inputs.K}) levels are also highly suitable.`,
            'Maize': `Maize (Corn) thrives well in warm temperatures (${inputs.temperature.toFixed(0)}°C) and moderate rainfall (${inputs.rainfall.toFixed(0)}mm). The soil profile is balanced with phosphorus (${inputs.P}) and potassium (${inputs.K}) suitable for corn cultivation.`,
            'Chickpea': `Chickpeas are dry-season pulse crops recommended for soils with lower nitrogen requirements (${inputs.N}) and moderate acidity (pH ${inputs.ph.toFixed(1)}). They need lower humidity (${inputs.humidity.toFixed(0)}%) and minimal rainfall.`,
            'Kidneybeans': `Kidney beans are recommended due to the moderate rainfall (${inputs.rainfall.toFixed(0)}mm) and slightly cooler temperature (${inputs.temperature.toFixed(0)}°C) requirements which perfectly align with your inputs.`,
            'Pigeonpeas': `Pigeon peas are drought-resistant legumes that tolerate lower rainfall (${inputs.rainfall.toFixed(0)}mm) and relatively high temperatures (${inputs.temperature.toFixed(0)}°C) in sandy-loam soils.`,
            'Mothbeans': `Moth beans require hot, dry climates. Your inputs of high temperature (${inputs.temperature.toFixed(0)}°C) and low rainfall (${inputs.rainfall.toFixed(0)}mm) represent ideal conditions for moth bean yields.`,
            'Mungbean': `Mung beans grow exceptionally well under warm conditions with higher atmospheric humidity (${inputs.humidity.toFixed(0)}%) and modest rainfall.`,
            'Blackgram': `Blackgram is a warm-weather pulse crop suited for areas with moderate rainfall (${inputs.rainfall.toFixed(0)}mm) and robust humidity.`,
            'Lentil': `Lentils require cool growing environments. The temperature of ${inputs.temperature.toFixed(0)}°C and lower rainfall inputs make it highly productive here.`,
            'Pomegranate': `Pomegranates prefer semi-arid conditions. Your temperate input along with lower moisture and humidity are optimal for growing quality pomegranates.`,
            'Banana': `Bananas require tropical, warm climates. Your inputs match the criteria perfectly: high temperature (${inputs.temperature.toFixed(0)}°C), very high humidity (${inputs.humidity.toFixed(0)}%), and substantial rainfall.`,
            'Mango': `Mango is a tropical fruit tree suited for warm environments with dry spells. The moderate rainfall and warm temperature inputs are perfect for fruit maturity.`,
            'Grapes': `Grapes require dry and warm weather during fruit ripening. The moderate humidity (${inputs.humidity.toFixed(0)}%) and rainfall are suitable for preventing vineyard fungal diseases.`,
            'Watermelon': `Watermelons need high heat, full sun, and moderate humidity. Your environmental inputs provide the necessary thermal environment for high sugar content in watermelons.`,
            'Muskmelon': `Muskmelons prefer warm temperatures and high humidity (${inputs.humidity.toFixed(0)}%) for development, aligning with the inputs provided.`,
            'Apple': `Apples require temperate/cooler climates. The cool temperature and moderate rain inputs prevent leaf-burn and supply the necessary chilling hours.`,
            'Orange': `Oranges grow best in subtropical conditions with warm weather and low-to-moderate humidity to prevent pest infestations.`,
            'Papaya': `Papaya is a fast-growing tropical fruit requiring warm weather, high relative humidity, and consistent soil moisture without waterlogging.`,
            'Coconut': `Coconut palms require tropical coastal climates. The high rainfall (${inputs.rainfall.toFixed(0)}mm) and high relative humidity (${inputs.humidity.toFixed(0)}%) are ideal for coconut crop health.`,
            'Cotton': `Cotton is a cash crop requiring high temperatures, moderate rainfall (${inputs.rainfall.toFixed(0)}mm), and good soil nitrogen content (${inputs.N}).`,
            'Jute': `Jute (the golden fiber) requires a hot and wet climate. Your inputs of high humidity (${inputs.humidity.toFixed(0)}%) and rainfall (${inputs.rainfall.toFixed(0)}mm) provide perfect swamp-like conditions for fiber retting.`,
            'Coffee': `Coffee plants require high elevation climates, warm temperatures, high humidity, and steady rainfall (${inputs.rainfall.toFixed(0)}mm) along with acidic soil profiles.`
        };

        return explanations[crop] || `This crop is recommended because the combination of environmental factors—N: ${inputs.N}, P: ${inputs.P}, K: ${inputs.K}, Temp: ${inputs.temperature.toFixed(1)}°C, Humidity: ${inputs.humidity.toFixed(1)}%, pH: ${inputs.ph.toFixed(1)}, and Rainfall: ${inputs.rainfall.toFixed(1)}mm—closely matches the historical profile for optimal growth of this variety.`;
    }

    function renderProbabilityChart(recommendations) {
        const ctx = document.getElementById('probabilities-chart').getContext('2d');
        
        // Sort recommendations and take top 5
        const sortedRecs = recommendations.slice(0, 5);
        const labels = sortedRecs.map(r => r.crop.charAt(0).toUpperCase() + r.crop.slice(1));
        const confidences = sortedRecs.map(r => r.confidence * 100);

        if (probabilityChart) {
            probabilityChart.destroy();
        }

        probabilityChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Confidence %',
                    data: confidences,
                    backgroundColor: [
                        'rgba(16, 185, 129, 0.85)',
                        'rgba(16, 185, 129, 0.45)',
                        'rgba(16, 185, 129, 0.3)',
                        'rgba(16, 185, 129, 0.2)',
                        'rgba(16, 185, 129, 0.1)'
                    ],
                    borderColor: 'rgba(16, 185, 129, 1)',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        ticks: { color: 'rgba(255, 255, 255, 0.8)', font: { family: 'Outfit', size: 11 } },
                        grid: { display: false }
                    },
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { color: 'rgba(255, 255, 255, 0.5)', font: { size: 9 } },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' }
                    }
                }
            }
        });
    }

    // Reset Button
    document.getElementById('reset-btn').addEventListener('click', () => {
        form.reset();
        // Update all sliders to default form values
        sliders.forEach(slider => {
            const bindId = slider.getAttribute('data-bind');
            const numInput = document.getElementById(bindId);
            if (numInput) {
                slider.value = numInput.value;
            }
        });
        // Reset Result Box
        resultPlaceholder.querySelector('h3').textContent = "Awaiting Input parameters";
        resultPlaceholder.querySelector('p').textContent = "Fill out the soil profile and environmental parameters, then click the button to generate a recommendation.";
        resultPlaceholder.classList.remove('hidden');
        resultContent.classList.add('hidden');
    });

    // ----------------------------------------------------
    // Crop Directory Init
    // ----------------------------------------------------
    const cropDirectoryGrid = document.getElementById('crop-directory-grid');
    const cropList = [
        { name: 'Rice', category: 'Grain', n: '80-100', p: '35-50', k: '35-45', temp: '20-27°C', hum: '80-85%', ph: '5.5-7.0', rain: '180-250mm' },
        { name: 'Maize', category: 'Grain', n: '70-90', p: '40-55', k: '15-25', temp: '18-27°C', hum: '55-70%', ph: '5.5-7.0', rain: '60-100mm' },
        { name: 'Chickpea', category: 'Pulse', n: '30-50', p: '55-70', k: '75-85', temp: '17-21°C', hum: '15-20%', ph: '5.5-8.5', rain: '65-95mm' },
        { name: 'Kidneybeans', category: 'Pulse', n: '10-30', p: '45-60', k: '15-25', temp: '15-25°C', hum: '50-60%', ph: '5.5-6.0', rain: '60-150mm' },
        { name: 'Pigeonpeas', category: 'Pulse', n: '10-30', p: '60-75', k: '15-25', temp: '25-35°C', hum: '40-65%', ph: '4.5-8.5', rain: '90-200mm' },
        { name: 'Mothbeans', category: 'Pulse', n: '10-30', p: '35-50', k: '15-25', temp: '25-35°C', hum: '40-65%', ph: '3.5-10.0', rain: '30-75mm' },
        { name: 'Mungbean', category: 'Pulse', n: '10-30', p: '35-50', k: '15-25', temp: '27-30°C', hum: '80-90%', ph: '6.2-7.2', rain: '35-60mm' },
        { name: 'Blackgram', category: 'Pulse', n: '35-55', p: '55-70', k: '15-25', temp: '25-35°C', hum: '60-70%', ph: '6.5-7.5', rain: '60-75mm' },
        { name: 'Lentil', category: 'Pulse', n: '10-30', p: '55-70', k: '15-25', temp: '18-30°C', hum: '60-70%', ph: '5.5-7.0', rain: '35-50mm' },
        { name: 'Pomegranate', category: 'Fruit', n: '10-30', p: '10-25', k: '35-45', temp: '18-25°C', hum: '85-90%', ph: '5.5-7.5', rain: '100-110mm' },
        { name: 'Banana', category: 'Fruit', n: '80-100', p: '70-90', k: '45-55', temp: '25-28°C', hum: '75-85%', ph: '5.5-6.5', rain: '90-110mm' },
        { name: 'Mango', category: 'Fruit', n: '20-40', p: '20-35', k: '25-35', temp: '27-35°C', hum: '45-55%', ph: '4.5-7.0', rain: '85-100mm' },
        { name: 'Grapes', category: 'Fruit', n: '20-40', p: '120-145', k: '195-205', temp: '25-40°C', hum: '80-85%', ph: '5.5-7.0', rain: '65-75mm' },
        { name: 'Watermelon', category: 'Fruit', n: '80-100', p: '5-25', k: '45-55', temp: '24-27°C', hum: '80-90%', ph: '6.0-6.8', rain: '40-60mm' },
        { name: 'Muskmelon', category: 'Fruit', n: '80-100', p: '5-25', k: '45-55', temp: '27-30°C', hum: '90-95%', ph: '6.0-6.8', rain: '20-30mm' },
        { name: 'Apple', category: 'Fruit', n: '0-20', p: '120-145', k: '195-205', temp: '21-24°C', hum: '90-95%', ph: '5.5-6.5', rain: '100-125mm' },
        { name: 'Orange', category: 'Fruit', n: '10-30', p: '5-25', k: '5-15', temp: '15-35°C', hum: '90-95%', ph: '6.0-8.0', rain: '100-120mm' },
        { name: 'Papaya', category: 'Fruit', n: '30-60', p: '45-70', k: '45-55', temp: '23-45°C', hum: '90-95%', ph: '6.5-7.0', rain: '150-250mm' },
        { name: 'Coconut', category: 'Fruit', n: '10-30', p: '5-25', k: '25-35', temp: '25-30°C', hum: '90-99%', ph: '5.5-6.5', rain: '150-230mm' },
        { name: 'Cotton', category: 'Cash Crop', n: '100-120', p: '35-50', k: '15-25', temp: '22-26°C', hum: '75-85%', ph: '5.8-8.0', rain: '60-80mm' },
        { name: 'Jute', category: 'Cash Crop', n: '70-90', p: '35-50', k: '35-45', temp: '23-27°C', hum: '70-90%', ph: '6.0-8.0', rain: '150-200mm' },
        { name: 'Coffee', category: 'Cash Crop', n: '80-100', p: '15-35', k: '25-35', temp: '23-28°C', hum: '50-65%', ph: '6.0-7.0', rain: '140-190mm' }
    ];

    function renderCropDirectory() {
        cropDirectoryGrid.innerHTML = '';
        cropList.forEach(crop => {
            const card = document.createElement('div');
            card.className = 'card glass crop-directory-card';
            
            // SVG Leaf Icon
            card.innerHTML = `
                <div class="crop-dir-header">
                    <div class="crop-avatar">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z"/>
                            <path d="M12 2V22" stroke-dasharray="2 2"/>
                            <path d="M12 6C9 9 9 15 12 18C15 15 15 9 12 6Z"/>
                        </svg>
                    </div>
                    <div>
                        <h3>${crop.name}</h3>
                        <span class="crop-tag">${crop.category}</span>
                    </div>
                </div>
                <div class="crop-requirements">
                    <div class="req-badge">N: <span>${crop.n}</span></div>
                    <div class="req-badge">P: <span>${crop.p}</span></div>
                    <div class="req-badge">K: <span>${crop.k}</span></div>
                    <div class="req-badge">Temp: <span>${crop.temp}</span></div>
                    <div class="req-badge">Hum: <span>${crop.hum}</span></div>
                    <div class="req-badge">pH: <span>${crop.ph}</span></div>
                    <div class="req-badge">Rain: <span>${crop.rain}</span></div>
                </div>
            `;
            cropDirectoryGrid.appendChild(card);
        });
    }

    // Initialize
    loadMetrics();
    renderCropDirectory();
});
