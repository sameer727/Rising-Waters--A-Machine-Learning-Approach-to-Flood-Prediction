document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('prediction-form');
  if (!form) return;

  const state = document.getElementById('State');
  const annualRainfall = document.getElementById('Annual_Rainfall');
  const cloudCover = document.getElementById('Cloud_Cover');
  const seasonalRainfall = document.getElementById('Seasonal_Rainfall');
  const temperature = document.getElementById('Temperature');
  const humidity = document.getElementById('Humidity');
  const riverWaterLevel = document.getElementById('River_Water_Level');
  const drainageCapacity = document.getElementById('Drainage_Capacity');
  const waterFlow = document.getElementById('Water_Flow');
  const reservoirLevel = document.getElementById('Reservoir_Level');
  const soilMoisture = document.getElementById('Soil_Moisture');

  // Input elements and validation configurations
  const inputs = [
    {
      element: state,
      errorId: 'state-error',
      isNumeric: false,
      validate: (val) => {
        if (!val || val.trim() === '') return 'Please select a state.';
        return '';
      }
    },
    {
      element: annualRainfall,
      errorId: 'annual-rainfall-error',
      isNumeric: true,
      validate: (val) => {
        if (isNaN(val)) return 'Must be a valid number.';
        if (val <= 0) return 'Annual rainfall must be greater than 0.';
        if (val < 400 || val > 6000) return 'Please enter a value in the range of 400 to 6000 mm.';
        return '';
      }
    },
    {
      element: cloudCover,
      errorId: 'cloud-cover-error',
      isNumeric: true,
      validate: (val) => {
        if (isNaN(val)) return 'Must be a valid number.';
        if (val < 0 || val > 100) return 'Cloud cover must be between 0 and 100%.';
        return '';
      }
    },
    {
      element: seasonalRainfall,
      errorId: 'seasonal-rainfall-error',
      isNumeric: true,
      validate: (val) => {
        if (isNaN(val)) return 'Must be a valid number.';
        if (val < 0) return 'Seasonal rainfall cannot be negative.';
        const annualVal = parseFloat(annualRainfall.value);
        if (!isNaN(annualVal) && val > annualVal) {
          return 'Seasonal rainfall cannot exceed annual rainfall.';
        }
        return '';
      }
    },
    {
      element: temperature,
      errorId: 'temperature-error',
      isNumeric: true,
      validate: (val) => {
        if (isNaN(val)) return 'Must be a valid number.';
        if (val < -10 || val > 60) return 'Temperature must be between -10 and 60 °C.';
        return '';
      }
    },
    {
      element: humidity,
      errorId: 'humidity-error',
      isNumeric: true,
      validate: (val) => {
        if (isNaN(val)) return 'Must be a valid number.';
        if (val < 0 || val > 100) return 'Humidity must be between 0 and 100%.';
        return '';
      }
    },
    {
      element: riverWaterLevel,
      errorId: 'river-water-level-error',
      isNumeric: true,
      validate: (val) => {
        if (isNaN(val)) return 'Must be a valid number.';
        if (val < 0 || val > 30) return 'River water level must be between 0 and 30 m.';
        return '';
      }
    },
    {
      element: drainageCapacity,
      errorId: 'drainage-capacity-error',
      isNumeric: true,
      validate: (val) => {
        if (isNaN(val)) return 'Must be a valid number.';
        if (val < 0 || val > 100) return 'Drainage capacity must be between 0 and 100%.';
        return '';
      }
    },
    {
      element: waterFlow,
      errorId: 'water-flow-error',
      isNumeric: true,
      validate: (val) => {
        if (isNaN(val)) return 'Must be a valid number.';
        if (val < 0 || val > 5000) return 'Water flow must be between 0 and 5000 cumecs.';
        return '';
      }
    },
    {
      element: reservoirLevel,
      errorId: 'reservoir-level-error',
      isNumeric: true,
      validate: (val) => {
        if (isNaN(val)) return 'Must be a valid number.';
        if (val < 0 || val > 100) return 'Reservoir level must be between 0 and 100%.';
        return '';
      }
    },
    {
      element: soilMoisture,
      errorId: 'soil-moisture-error',
      isNumeric: true,
      validate: (val) => {
        if (isNaN(val)) return 'Must be a valid number.';
        if (val < 0 || val > 100) return 'Soil moisture must be between 0 and 100%.';
        return '';
      }
    }
  ];

  // Live validation on input change/select
  inputs.forEach(inputObj => {
    if (inputObj.element) {
      const eventType = inputObj.element.tagName === 'SELECT' ? 'change' : 'input';
      inputObj.element.addEventListener(eventType, () => {
        validateField(inputObj);
      });
    }
  });

  // Submit validation & AJAX submission
  form.addEventListener('submit', async (e) => {
    e.preventDefault(); // Always prevent default form submission

    let isValid = true;
    inputs.forEach(inputObj => {
      const errorMsg = validateField(inputObj);
      if (errorMsg) {
        isValid = false;
      }
    });

    if (!isValid) {
      // Add shake animation to card
      const card = document.querySelector('.form-section-card');
      if (card) {
        card.style.animation = 'none';
        setTimeout(() => {
          card.style.animation = 'shake 0.5s ease-in-out';
        }, 10);
      }
      return;
    }

    // Capture submit button and show loading state
    const btnSubmit = document.getElementById('btn-submit-predict');
    const originalText = btnSubmit ? btnSubmit.textContent : 'Execute Analysis';
    if (btnSubmit) {
      btnSubmit.textContent = 'Running Model Inferences...';
      btnSubmit.disabled = true;
    }

    try {
      // Package values in a JSON payload
      const payload = {
        State: state.value || 'Custom Region',
        Annual_Rainfall: parseFloat(annualRainfall.value),
        Seasonal_Rainfall: parseFloat(seasonalRainfall.value),
        Cloud_Cover: parseFloat(cloudCover.value),
        Humidity: parseFloat(humidity.value),
        Temperature: parseFloat(temperature.value),
        River_Water_Level: parseFloat(riverWaterLevel.value),
        Drainage_Capacity: parseFloat(drainageCapacity.value),
        Water_Flow: parseFloat(waterFlow.value),
        Reservoir_Level: parseFloat(reservoirLevel.value),
        Soil_Moisture: parseFloat(soilMoisture.value)
      };

      const res = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (data && data.success) {
        // Update Result Panel elements
        const resultSidebar = document.getElementById('result-sidebar');
        const statusWrapper = document.getElementById('result-status-wrapper');
        const statusText = document.getElementById('result-status-text');
        const metricsDiv = document.getElementById('result-metrics');
        const probValEl = document.getElementById('metric-prob-val');
        const barFill = document.getElementById('probability-bar-fill');
        const confidenceEl = document.getElementById('metric-confidence');
        const modelEl = document.getElementById('metric-model');
        const explanationEl = document.getElementById('explanation-text');
        const mitigationBox = document.getElementById('mitigation-plan-box');
        const mitigationTitle = document.getElementById('mitigation-title');
        const mitigationList = document.getElementById('mitigation-list');

        // Apply theme classes based on prediction outcome
        statusWrapper.classList.remove('idle', 'warning', 'safe-state');
        if (data.prediction === 1) {
          statusWrapper.classList.add('warning');
          statusText.textContent = `CRITICAL WARNING: FLOOD RISK DETECTED (${data.probability}%)`;
        } else {
          statusWrapper.classList.add('safe-state');
          statusText.textContent = `STABLE CONDITIONS: LOW RISK (${data.probability}%)`;
        }

        // Make metric details visible
        metricsDiv.style.display = 'block';
        probValEl.textContent = `${data.probability}%`;
        barFill.style.width = `${data.probability}%`;
        confidenceEl.textContent = data.confidence;
        modelEl.textContent = data.model_name || 'XGBoost';
        explanationEl.textContent = data.explanation;

        // Update Mitigation & Evacuation Guidelines dynamically
        if (mitigationBox && mitigationTitle && mitigationList) {
          mitigationBox.style.display = 'block';
          mitigationList.innerHTML = '';
          
          if (data.prediction === 1) {
            mitigationTitle.textContent = '🚨 Emergency Evacuation & Mitigation Plan';
            mitigationTitle.style.color = '#f87171'; // soft red
            
            mitigationList.innerHTML = `
              <li><strong>Evacuation Plan:</strong> Move immediately to pre-planned high ground or community shelters. Avoid low-lying areas.</li>
              <li><strong>Telemetry Alerts:</strong> Keep emergency radios/phones active. Continuous heavy rain forecast indicates increasing hazard severity.</li>
              <li><strong>Utility Safety:</strong> Turn off main electrical breakers and gas valves before leaving.</li>
              <li><strong>Emergency Kit:</strong> Grab your survival kit (water, dry food, medical supplies, documents, flashlight).</li>
            `;
          } else {
            mitigationTitle.textContent = '🛡️ General Preparedness & Safety Guidelines';
            mitigationTitle.style.color = '#34d399'; // soft green
            
            mitigationList.innerHTML = `
              <li><strong>Routine Monitoring:</strong> Continue checking local river levels and weather telemetry.</li>
              <li><strong>Clear Drains:</strong> Keep municipal/property storm drains free of debris to ensure maximum runoff capacity.</li>
              <li><strong>Safety Drills:</strong> Review evacuation routes with team members or household residents.</li>
            `;
          }
        }

        // Save run to local prediction history list
        saveToHistory({
          state: state.value || 'Custom Region',
          probability: data.probability,
          prediction: data.prediction,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          inputs: payload
        });

        // Scroll to results panel on small screens
        if (window.innerWidth <= 992) {
          resultSidebar.scrollIntoView({ behavior: 'smooth' });
        }
      } else {
        alert(data.error || 'Server prediction error.');
      }
    } catch (err) {
      console.error(err);
      alert('Network error connecting to prediction API.');
    } finally {
      if (btnSubmit) {
        btnSubmit.textContent = originalText;
        btnSubmit.disabled = false;
      }
    }
  });

  // Local storage history functions
  const saveToHistory = (item) => {
    let history = [];
    try {
      history = JSON.parse(localStorage.getItem('flood_history') || '[]');
    } catch (e) {
      history = [];
    }
    // Add to front, limit to 8
    history.unshift(item);
    if (history.length > 8) history.pop();
    localStorage.setItem('flood_history', JSON.stringify(history));
    renderHistory();
  };

  const renderHistory = () => {
    const emptyEl = document.getElementById('history-empty');
    const listEl = document.getElementById('history-list');
    if (!listEl) return;

    let history = [];
    try {
      history = JSON.parse(localStorage.getItem('flood_history') || '[]');
    } catch (e) {
      history = [];
    }

    if (history.length === 0) {
      emptyEl.style.display = 'block';
      listEl.style.display = 'none';
      return;
    }

    emptyEl.style.display = 'none';
    listEl.style.display = 'flex';
    listEl.innerHTML = '';

    history.forEach((item, index) => {
      const li = document.createElement('li');
      li.className = 'history-item';
      
      const badgeClass = item.prediction === 1 ? 'badge-danger' : 'badge-success';
      const badgeText = item.prediction === 1 ? 'Flood' : 'Safe';

      li.innerHTML = `
        <div class="history-info">
          <span class="history-state">${item.state}</span>
          <span class="history-meta">Prob: ${item.probability}% • ${item.timestamp}</span>
        </div>
        <span class="badge ${badgeClass}">${badgeText}</span>
      `;

      // Set click listener to restore this history run's inputs to form!
      li.addEventListener('click', () => {
        state.value = item.inputs.State || item.state;
        annualRainfall.value = item.inputs.Annual_Rainfall;
        seasonalRainfall.value = item.inputs.Seasonal_Rainfall;
        cloudCover.value = item.inputs.Cloud_Cover;
        humidity.value = item.inputs.Humidity;
        temperature.value = item.inputs.Temperature;
        riverWaterLevel.value = item.inputs.River_Water_Level;
        drainageCapacity.value = item.inputs.Drainage_Capacity;
        waterFlow.value = item.inputs.Water_Flow;
        reservoirLevel.value = item.inputs.Reservoir_Level;
        soilMoisture.value = item.inputs.Soil_Moisture;

        // Clear error markings
        inputs.forEach(inputObj => clearError(inputObj.element, document.getElementById(inputObj.errorId)));
        
        // Visual indicator on form
        const formCard = document.querySelector('.form-section-card');
        if (formCard) {
          formCard.style.boxShadow = '0 0 20px rgba(59, 130, 246, 0.4)';
          setTimeout(() => {
            formCard.style.boxShadow = 'var(--shadow)';
          }, 600);
        }
      });

      listEl.appendChild(li);
    });
  };

  // Render initial history on load
  renderHistory();

  function validateField(inputObj) {
    if (!inputObj.element) return '';
    const rawVal = inputObj.element.value;
    const errorEl = document.getElementById(inputObj.errorId);
    
    if (rawVal.trim() === '') {
      showError(inputObj.element, errorEl, 'This field is required.');
      return 'This field is required.';
    }

    const valToValidate = inputObj.isNumeric ? parseFloat(rawVal) : rawVal;
    const errorMsg = inputObj.validate(valToValidate);
    
    if (errorMsg) {
      showError(inputObj.element, errorEl, errorMsg);
      return errorMsg;
    } else {
      clearError(inputObj.element, errorEl);
      return '';
    }
  }

  function showError(inputEl, errorEl, msg) {
    inputEl.style.borderColor = 'var(--accent-neon-red)';
    inputEl.style.boxShadow = '0 0 5px rgba(239, 68, 68, 0.3)';
    if (errorEl) {
      errorEl.textContent = msg;
      errorEl.style.display = 'block';
    }
  }

  function clearError(inputEl, errorEl) {
    inputEl.style.borderColor = 'var(--glass-border)';
    inputEl.style.boxShadow = 'none';
    if (errorEl) {
      errorEl.style.display = 'none';
    }
  }

  // Location Auto-Detection
  const btnLocation = document.getElementById('btn-detect-location');
  const statusEl = document.getElementById('location-status');

  if (btnLocation) {
    let mapInstance = null;
    let markerInstance = null;

    // Create beautiful custom animated HTML sonar marker
    const sonarIcon = L.divIcon({
      className: 'sonar-marker',
      html: `
        <div class="sonar-wrapper">
          <div class="sonar-core"></div>
          <div class="sonar-ring sonar-ring-1"></div>
          <div class="sonar-ring sonar-ring-2"></div>
          <div class="sonar-ring sonar-ring-3"></div>
        </div>
      `,
      iconSize: [40, 40],
      iconAnchor: [20, 20]
    });

    const initMap = (lat, lon, placeMarker = true) => {
      const mapContainer = document.getElementById('map-container');
      if (mapContainer) {
        mapContainer.style.display = 'block';
      }

      if (!mapInstance) {
        // Initialize Map centered broad-range over India
        mapInstance = L.map('map').setView([lat, lon], 5);

        // Load CartoDB Dark Matter tiles
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
          maxZoom: 20
        }).addTo(mapInstance);

        // Prevent grey tiles by recalculating size after any map movement/flyTo ends
        mapInstance.on('moveend', () => {
          mapInstance.invalidateSize();
        });

        // Add custom Heatmap Toggle Control to map
        const HeatmapControl = L.Control.extend({
          options: { position: 'topright' },
          onAdd: function() {
            const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-custom-control');
            container.style.backgroundColor = 'rgba(17, 24, 39, 0.9)';
            container.style.border = '1px solid var(--glass-border)';
            container.style.borderRadius = '8px';
            container.style.padding = '2px';
            container.style.cursor = 'pointer';
            
            const button = L.DomUtil.create('button', 'heatmap-toggle-btn', container);
            button.innerHTML = '🔥 Toggle Heatmap';
            button.style.background = 'none';
            button.style.border = 'none';
            button.style.color = '#fff';
            button.style.fontFamily = 'inherit';
            button.style.fontSize = '11px';
            button.style.fontWeight = 'bold';
            button.style.padding = '4px 8px';
            button.style.cursor = 'pointer';

            L.DomEvent.on(container, 'click', function(e) {
              L.DomEvent.stopPropagation(e);
              toggleStateHeatmap();
            });

            return container;
          }
        });
        new HeatmapControl().addTo(mapInstance);

        // Bind click event to map to drop pin and analyze coordinates
        mapInstance.on('click', async (e) => {
          const clickLat = e.latlng.lat;
          const clickLon = e.latlng.lng;

          btnLocation.classList.add('loading');
          btnLocation.disabled = true;
          statusEl.textContent = 'Analyzing dropped pin coordinates...';
          statusEl.className = 'location-status';

          // Place/Move the marker
          if (markerInstance) {
            markerInstance.setLatLng([clickLat, clickLon]);
          } else {
            markerInstance = L.marker([clickLat, clickLon], { icon: sonarIcon }).addTo(mapInstance);
          }

          // Fly into clicked location
          mapInstance.flyTo([clickLat, clickLon], 8, {
            animate: true,
            duration: 1.5
          });

          await getClimateData(clickLat, clickLon);
        });
      }

      if (placeMarker) {
        // Smoothly fly into the resolved coordinates
        setTimeout(() => {
          mapInstance.flyTo([lat, lon], 8, {
            animate: true,
            duration: 2.2
          });
        }, 100);

        // Remove existing marker if it exists
        if (markerInstance) {
          mapInstance.removeLayer(markerInstance);
        }

        // Place Leaflet marker
        markerInstance = L.marker([lat, lon], { icon: sonarIcon }).addTo(mapInstance)
          .bindPopup('<b>Climate Station Active</b><br>Continuous telemetry monitoring.');
      }

      // Update map layout to prevent grey/unloaded tile issues
      setTimeout(() => {
        mapInstance.invalidateSize();
      }, 200);
    };

    // Coordinate centroids of supported states to map the closest detected coordinates
    const findClosestState = (lat, lon) => {
      const centroids = {
        'Andhra Pradesh': { lat: 15.9, lon: 79.7 },
        'Arunachal Pradesh': { lat: 28.0, lon: 94.7 },
        'Assam': { lat: 26.2, lon: 92.5 },
        'Bihar': { lat: 25.8, lon: 85.5 },
        'Chhattisgarh': { lat: 21.2, lon: 81.6 },
        'Delhi': { lat: 28.6, lon: 77.2 },
        'Goa': { lat: 15.3, lon: 74.0 },
        'Gujarat': { lat: 22.3, lon: 72.0 },
        'Haryana': { lat: 29.0, lon: 76.0 },
        'Himachal Pradesh': { lat: 32.0, lon: 77.2 },
        'Jammu & Kashmir': { lat: 33.5, lon: 75.0 },
        'Jharkhand': { lat: 23.6, lon: 85.3 },
        'Karnataka': { lat: 15.0, lon: 75.7 },
        'Kerala': { lat: 10.5, lon: 76.5 },
        'Madhya Pradesh': { lat: 23.5, lon: 78.5 },
        'Maharashtra': { lat: 19.5, lon: 75.5 },
        'Manipur': { lat: 24.6, lon: 93.9 },
        'Meghalaya': { lat: 25.5, lon: 91.2 },
        'Mizoram': { lat: 23.3, lon: 92.8 },
        'Nagaland': { lat: 26.1, lon: 94.5 },
        'Odisha': { lat: 20.5, lon: 84.5 },
        'Punjab': { lat: 31.0, lon: 75.5 },
        'Rajasthan': { lat: 26.5, lon: 73.8 },
        'Sikkim': { lat: 27.5, lon: 88.5 },
        'Tamil Nadu': { lat: 11.0, lon: 78.5 },
        'Telangana': { lat: 18.1, lon: 79.0 },
        'Tripura': { lat: 23.8, lon: 91.2 },
        'Uttar Pradesh': { lat: 27.0, lon: 80.5 },
        'Uttarakhand': { lat: 30.1, lon: 79.0 },
        'West Bengal': { lat: 23.0, lon: 88.0 }
      };

      let closestState = 'Maharashtra'; // Default fallback
      let minDistance = Infinity;

      for (const [stateName, coords] of Object.entries(centroids)) {
        const dist = Math.hypot(lat - coords.lat, lon - coords.lon);
        if (dist < minDistance) {
          minDistance = dist;
          closestState = stateName;
        }
      }
      return closestState;
    };

    const selectEl = document.getElementById('State');
    const supportedStates = selectEl ? Array.from(selectEl.options).map(opt => opt.value).filter(val => val !== '') : [];

    const normalizeStateName = (name) => {
      if (!name) return null;
      let clean = name.toLowerCase().replace(/[^a-z0-9]/g, '');
      
      if (clean.includes('delhi')) return 'Delhi';
      if (clean.includes('jammu') || clean.includes('kashmir')) return 'Jammu & Kashmir';
      if (clean.includes('orissa') || clean.includes('odisha')) return 'Odisha';
      
      const match = supportedStates.find(s => {
        let sClean = s.toLowerCase().replace(/[^a-z0-9]/g, '');
        return clean.includes(sClean) || sClean.includes(clean);
      });
      return match || null;
    };

    let chartInstance = null;

    const renderPrecipitationChart = (monthlyData) => {
      const canvasEl = document.getElementById('precipitation-chart');
      if (!canvasEl) return;
      const ctx = canvasEl.getContext('2d');
      const chartContainer = document.getElementById('chart-container');
      if (chartContainer) chartContainer.style.display = 'block';
      
      if (chartInstance) {
        chartInstance.destroy();
      }
      
      chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
          datasets: [{
            label: 'Monthly Rainfall (mm)',
            data: monthlyData.map(val => Math.round(val)),
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.15)',
            borderWidth: 2.5,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#60a5fa',
            pointRadius: 4,
            pointHoverRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: 'rgba(17, 24, 39, 0.95)',
              titleColor: '#fff',
              bodyColor: '#fff',
              borderColor: 'rgba(255, 255, 255, 0.1)',
              borderWidth: 1,
              padding: 10,
              displayColors: false,
              callbacks: {
                label: (context) => ` Precipitation: ${context.parsed.y} mm`
              }
            }
          },
          scales: {
            x: {
              grid: { color: 'rgba(255, 255, 255, 0.05)' },
              ticks: { color: '#9ca3af', font: { size: 10, family: 'inherit' } }
            },
            y: {
              grid: { color: 'rgba(255, 255, 255, 0.05)' },
              ticks: { color: '#9ca3af', font: { size: 10, family: 'inherit' } },
              beginAtZero: true
            }
          }
        }
      });
    };

    // State baseline annual rainfall (proxy for vulnerability styling)
    const stateVulnerability = {
      'Andhra Pradesh': 950,
      'Arunachal Pradesh': 2800,
      'Assam': 2800,
      'Bihar': 1200,
      'Chhattisgarh': 1300,
      'Delhi': 700,
      'Goa': 2900,
      'Gujarat': 700,
      'Haryana': 600,
      'Himachal Pradesh': 1250,
      'Jammu & Kashmir': 800,
      'Jharkhand': 1200,
      'Karnataka': 1200,
      'Kerala': 3000,
      'Madhya Pradesh': 1000,
      'Maharashtra': 1500,
      'Manipur': 1800,
      'Meghalaya': 3500,
      'Mizoram': 2400,
      'Nagaland': 2000,
      'Odisha': 1450,
      'Punjab': 650,
      'Rajasthan': 400,
      'Sikkim': 2700,
      'Tamil Nadu': 950,
      'Telangana': 900,
      'Tripura': 2200,
      'Uttar Pradesh': 950,
      'Uttarakhand': 1500,
      'West Bengal': 1750
    };

    const getHeatmapColor = (rainfall) => {
      if (!rainfall) return 'rgba(255, 255, 255, 0.1)';
      return rainfall > 2500 ? '#991b1b' :  // Extreme risk (dark red)
             rainfall > 1700 ? '#ea580c' :  // High risk (orange)
             rainfall > 1100 ? '#d97706' :  // Moderate risk (amber)
             rainfall > 700  ? '#84cc16' :  // Low-Moderate risk (lime)
                               '#10b981';   // Low risk (emerald)
    };

    let geoJsonLayer = null;
    let heatmapActive = false;
    let legendControl = null;

    const showLegend = () => {
      if (legendControl) return;
      
      legendControl = L.control({ position: 'bottomright' });
      legendControl.onAdd = function() {
        const div = L.DomUtil.create('div', 'info legend');
        div.style.background = 'rgba(17, 24, 39, 0.95)';
        div.style.border = '1px solid var(--glass-border)';
        div.style.borderRadius = '8px';
        div.style.padding = '8px 12px';
        div.style.color = '#fff';
        div.style.fontFamily = 'inherit';
        div.style.fontSize = '10px';
        div.style.lineHeight = '18px';
        div.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.5)';
        
        const grades = [0, 700, 1100, 1700, 2500];
        const labels = ['Low Risk', 'Mod-Low', 'Moderate', 'High', 'Extreme'];
        
        div.innerHTML = '<b style="font-size: 11px;">Flood Vulnerability Index</b><br>';
        for (let i = 0; i < grades.length; i++) {
          const color = getHeatmapColor(grades[i] + 1);
          div.innerHTML += `<i style="background: ${color}; width: 12px; height: 12px; float: left; margin-right: 8px; margin-top: 3px; border-radius: 2px;"></i> ${labels[i]} (${grades[i] === 0 ? '<700mm' : grades[i] + 'mm+'})<br>`;
        }
        return div;
      };
      legendControl.addTo(mapInstance);
    };

    const hideLegend = () => {
      if (legendControl) {
        mapInstance.removeControl(legendControl);
        legendControl = null;
      }
    };

    const toggleStateHeatmap = async () => {
      heatmapActive = !heatmapActive;
      const btn = document.querySelector('.heatmap-toggle-btn');
      if (btn) {
        btn.innerHTML = heatmapActive ? '❄️ Hide Heatmap' : '🔥 Toggle Heatmap';
        btn.style.color = heatmapActive ? '#3b82f6' : '#fff';
      }

      if (heatmapActive) {
        statusEl.textContent = 'Loading Indian state vulnerability boundaries...';
        statusEl.className = 'location-status success';
        
        try {
          if (!geoJsonLayer) {
            const geoRes = await fetch('https://raw.githubusercontent.com/civictech-India/INDIA-GEO-JSON-Datasets/main/india_states.json');
            const geoData = await geoRes.json();
            
            geoJsonLayer = L.geoJSON(geoData, {
              style: (feature) => {
                const rawName = feature.properties.NAME_1;
                const normalized = normalizeStateName(rawName);
                const rainfall = stateVulnerability[normalized];
                return {
                  fillColor: getHeatmapColor(rainfall),
                  weight: 1.5,
                  opacity: 1,
                  color: 'rgba(255, 255, 255, 0.15)',
                  fillOpacity: 0.45
                };
              },
              onEachFeature: (feature, layer) => {
                const rawName = feature.properties.NAME_1;
                const normalized = normalizeStateName(rawName) || rawName;
                const rainfall = stateVulnerability[normalized] || 'N/A';
                const riskLevel = rainfall > 2500 ? 'Extreme Vulnerability' :
                                  rainfall > 1700 ? 'High Vulnerability' :
                                  rainfall > 1100 ? 'Moderate Vulnerability' :
                                                    'Low Vulnerability';
                layer.bindTooltip(`<b>${normalized}</b><br>Baseline Rainfall: ${rainfall}mm<br>Status: ${riskLevel}`, {
                  sticky: true,
                  className: 'map-tooltip'
                });
                
                layer.on({
                  mouseover: (e) => {
                    const l = e.target;
                    l.setStyle({
                      fillOpacity: 0.65,
                      weight: 2,
                      color: '#ffffff'
                    });
                  },
                  mouseout: (e) => {
                    geoJsonLayer.resetStyle(e.target);
                  },
                  click: (e) => {
                    const center = e.target.getBounds().getCenter();
                    getClimateData(center.lat, center.lng);
                  }
                });
              }
            });
          }
          
          geoJsonLayer.addTo(mapInstance);
          showLegend();
          statusEl.textContent = 'State flood-risk boundaries overlay active.';
        } catch (err) {
          console.error('GeoJSON loading error:', err);
          statusEl.textContent = 'Failed to load boundary overlays.';
          statusEl.className = 'location-status error';
          heatmapActive = false;
          if (btn) {
            btn.innerHTML = '🔥 Toggle Heatmap';
            btn.style.color = '#fff';
          }
        }
      } else {
        if (geoJsonLayer) {
          mapInstance.removeLayer(geoJsonLayer);
        }
        hideLegend();
        statusEl.textContent = 'State flood-risk boundaries overlay deactivated.';
      }
    };

    const getClimateData = async (lat, lon) => {
      try {
        let resolvedState = null;
        try {
          const geoUrl = `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=en`;
          const geoRes = await fetch(geoUrl);
          const geoData = await geoRes.json();
          if (geoData && geoData.principalSubdivision) {
            resolvedState = normalizeStateName(geoData.principalSubdivision);
          }
        } catch (apiErr) {
          console.warn('Reverse geocoding API failed, trying offline centroid match.', apiErr);
        }

        if (!resolvedState) {
          resolvedState = findClosestState(lat, lon);
        }

        statusEl.textContent = `Location resolved (${lat.toFixed(4)}, ${lon.toFixed(4)}) as ${resolvedState}. Fetching weather...`;
        
        // 1. Fetch current weather parameters (Forecast API)
        const forecastUrl = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,cloud_cover`;
        const forecastRes = await fetch(forecastUrl);
        const forecastData = await forecastRes.json();

        // 2. Fetch historical rainfall (Archive API for 30 years to capture long-term baseline)
        const today = new Date();
        const yesterday = new Date(today);
        yesterday.setDate(today.getDate() - 2); // 2 days ago to ensure complete archive availability
        const endStr = yesterday.toISOString().split('T')[0];
        const startStr = '1996-01-01';

        statusEl.textContent = `Fetching 30-year precipitation archives (1996 to ${today.getFullYear()})...`;
        const archiveUrl = `https://archive-api.open-meteo.com/v1/archive?latitude=${lat}&longitude=${lon}&start_date=${startStr}&end_date=${endStr}&daily=precipitation_sum&timezone=auto`;
        const archiveRes = await fetch(archiveUrl);
        const archiveData = await archiveRes.json();

        // Extract Current Weather Features
        const currTemp = forecastData.current.temperature_2m;
        const currHumidity = forecastData.current.relative_humidity_2m;
        const currCloudCover = forecastData.current.cloud_cover;

        // Extract Historical Rainfall Features
        const dailyRain = archiveData.daily.precipitation_sum;
        const dates = archiveData.daily.time;

        let totalRainSum = 0;
        let totalSeasonalSum = 0;
        const monthlySums = new Array(12).fill(0);

        for (let i = 0; i < dailyRain.length; i++) {
          const rain = dailyRain[i] || 0;
          totalRainSum += rain;

          // Check if date falls in Southwest Monsoon (June 1st to September 30th)
          const dateStr = dates[i]; // Format "YYYY-MM-DD"
          const monthIndex = parseInt(dateStr.substring(5, 7), 10) - 1;
          if (monthIndex >= 0 && monthIndex < 12) {
            monthlySums[monthIndex] += rain;
          }

          const monthStr = dateStr.substring(5, 7);
          if (monthStr >= '06' && monthStr <= '09') {
            totalSeasonalSum += rain;
          }
        }

        const numYears = dailyRain.length / 365.25;
        const avgAnnualRainfall = totalRainSum / numYears;
        const avgSeasonalRainfall = totalSeasonalSum / numYears;
        const avgMonthlyPrecipitation = monthlySums.map(sum => sum / numYears);

        // Realistic estimations for hydrometeorological features
        const clampVal = (v, min, max) => Math.min(Math.max(v, min), max);
        
        // River Water Level (meters): higher monsoon/seasonal rainfall -> higher stage height
        const avgRiverWaterLevel = clampVal(2.5 + (avgSeasonalRainfall / 280) + Math.random() * 1.5, 0.5, 18.0);
        
        // Drainage Capacity (%): general regional estimate based on annual rainfall (highly wet regions may have overloaded drains)
        const avgDrainageCapacity = clampVal(75 - (avgAnnualRainfall / 70) - Math.random() * 10, 15, 95);
        
        // Water Flow (cumecs): correlated with seasonal rain intensity and river height
        const avgWaterFlow = clampVal((avgSeasonalRainfall / 4) + (avgRiverWaterLevel * 25) + Math.random() * 50, 10, 1500);
        
        // Reservoir Level (%): correlated with annual rainfall baselines
        const avgReservoirLevel = clampVal(35 + (avgAnnualRainfall / 50) + Math.random() * 15, 10, 100);
        
        // Soil Moisture (%): highly correlated with humidity and cloud cover
        const avgSoilMoisture = clampVal((currHumidity * 0.5) + (currCloudCover * 0.3) + (avgSeasonalRainfall / 60) + Math.random() * 10, 5, 100);

        // Update chart title dynamically to reflect the 30-year span
        const titleEl = document.getElementById('chart-title-text');
        if (titleEl) {
          titleEl.textContent = `30-Year Average Monthly Precipitation Trend (1996 - ${today.getFullYear()}) (mm)`;
        }

        // Render the monthly precipitation trend chart
        renderPrecipitationChart(avgMonthlyPrecipitation);

        // Autofill the form inputs
        state.value = resolvedState;

        annualRainfall.value = Math.round(avgAnnualRainfall);
        cloudCover.value = Math.round(currCloudCover);
        seasonalRainfall.value = Math.round(avgSeasonalRainfall);
        temperature.value = currTemp.toFixed(1);
        humidity.value = Math.round(currHumidity);
        riverWaterLevel.value = avgRiverWaterLevel.toFixed(2);
        drainageCapacity.value = Math.round(avgDrainageCapacity);
        waterFlow.value = Math.round(avgWaterFlow);
        reservoirLevel.value = Math.round(avgReservoirLevel);
        soilMoisture.value = Math.round(avgSoilMoisture);

        // Trigger visual validation clear
        inputs.forEach(inputObj => clearError(inputObj.element, document.getElementById(inputObj.errorId)));

        // Initialize Map
        initMap(lat, lon);

        statusEl.textContent = `Climate data successfully loaded for ${resolvedState} (Lat: ${lat.toFixed(4)}, Lon: ${lon.toFixed(4)})`;
        statusEl.className = 'location-status success';
      } catch (err) {
        console.error(err);
        statusEl.textContent = 'Error connecting to weather services. Please fill details manually.';
        statusEl.className = 'location-status error';
      } finally {
        btnLocation.classList.remove('loading');
        btnLocation.disabled = false;
      }
    };

    const fallbackToIP = async () => {
      statusEl.textContent = 'GPS blocked or slow. Falling back to IP-based location...';
      try {
        const res = await fetch('https://freeipapi.com/api/json');
        const data = await res.json();
        if (data && data.latitude && data.longitude) {
          await getClimateData(data.latitude, data.longitude);
        } else {
          throw new Error('IP location service returned invalid format.');
        }
      } catch (err) {
        console.error(err);
        statusEl.textContent = 'Could not resolve location via GPS or IP. Please fill manually.';
        statusEl.className = 'location-status error';
        btnLocation.classList.remove('loading');
        btnLocation.disabled = false;
      }
    };

    btnLocation.addEventListener('click', () => {
      btnLocation.classList.add('loading');
      btnLocation.disabled = true;
      statusEl.textContent = 'Requesting location...';
      statusEl.className = 'location-status';

      if (!navigator.geolocation) {
        fallbackToIP();
      } else {
        navigator.geolocation.getCurrentPosition(
          async (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            await getClimateData(lat, lon);
          },
          async (error) => {
            console.warn('Browser GPS access failed/denied. Trying IP fallback.', error);
            await fallbackToIP();
          },
          { enableHighAccuracy: false, timeout: 3000 }
        );
      }
    });

    // Initialize map immediately on page load centered broad-range over India
    initMap(20.5937, 78.9629, false);
  }
});

// CSS shake and pulsing-zone keyframes dynamically added
const styleSheet = document.createElement('style');
styleSheet.type = 'text/css';
styleSheet.innerText = `
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
    20%, 40%, 60%, 80% { transform: translateX(5px); }
  }
  @keyframes pulse-circle {
    0% {
      fill-opacity: 0.1;
      stroke-width: 1;
    }
    50% {
      fill-opacity: 0.35;
      stroke-width: 3;
    }
    100% {
      fill-opacity: 0.1;
      stroke-width: 1;
    }
  }
  .pulsing-zone {
    animation: pulse-circle 2s infinite ease-in-out;
  }
`;
document.head.appendChild(styleSheet);
