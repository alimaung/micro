/**
 * chart_manager.js - Chart management for microfilm control system
 * Handles chart initialization and updates
 */

// Create namespace for chart management functions
const ChartManager = {
    // Chart references
    charts: {},
    
    /**
     * Initialize all charts
     */
    initCharts: function() {
        if (typeof Chart !== 'undefined') {
            // Motor performance chart
            const motorsCtx = document.getElementById('motors-chart');
            if (motorsCtx) {
                this.charts.motorChart = new Chart(motorsCtx, {
                    type: 'line',
                    data: {
                        labels: ['1m ago', '50s', '40s', '30s', '20s', '10s', 'Now'],
                        datasets: [{
                            label: 'Shutter Motor (RPM)',
                            data: [0, 0, 180, 180, 0, 0, 180],
                            borderColor: 'rgba(90, 200, 250, 1)',
                            backgroundColor: 'rgba(90, 200, 250, 0.1)',
                            tension: 0.1,
                            borderWidth: 2,
                            fill: true,
                            stepped: false
                        }, {
                            label: 'Spool Motor (RPM)',
                            data: [80, 80, 0, 0, 80, 80, 0],
                            borderColor: 'rgba(255, 159, 10, 1)',
                            backgroundColor: 'rgba(255, 159, 10, 0.1)',
                            tension: 0.1,
                            borderWidth: 2,
                            fill: true,
                            stepped: false
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        aspectRatio: 1,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 220,
                                grid: {
                                    display: true,
                                    color: 'rgba(200, 200, 200, 0.1)'
                                }
                            },
                            x: {
                                grid: {
                                    display: false
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                position: 'top',
                                align: 'end',
                                labels: {
                                    boxWidth: 10,
                                    usePointStyle: true
                                }
                            }
                        }
                    }
                });
                
                // Update chart periodically
                setInterval(() => {
                    if (MachineControls.isMachineOn) {
                        const shutterData = this.charts.motorChart.data.datasets[0].data;
                        const spoolData = this.charts.motorChart.data.datasets[1].data;
                        
                        // Shift all data points to the left
                        shutterData.shift();
                        spoolData.shift();
                        
                        // Add new data points with rectangular pattern (either 0 or max value)
                        const shutterValue = Math.random() > 0.3 ? 180 : 0;
                        const spoolValue = Math.random() > 0.3 ? 60 : 0;
                        
                        shutterData.push(shutterValue);
                        spoolData.push(spoolValue);
                        
                        this.charts.motorChart.update('none');
                    }
                }, 5000);
            }
            
            // System temperature chart
            const tempCtx = document.getElementById('temperature-chart');
            if (tempCtx) {
                this.charts.tempChart = new Chart(tempCtx, {
                    type: 'line',
                    data: {
                        labels: ['1m ago', '50s', '40s', '30s', '20s', '10s', 'Now'],
                        datasets: [{
                            label: 'Temperature (°C)',
                            data: [36.5, 39.2, 37.8, 40.1, 38.0, 36.9, 39.5],
                            borderColor: 'rgba(255, 69, 58, 1)',
                            backgroundColor: 'rgba(255, 69, 58, 0.1)',
                            tension: 0.4,
                            borderWidth: 2,
                            fill: true
                        }, {
                            label: 'Optimal Range (°C)',
                            data: [37.5, 37.8, 38.2, 37.9, 38.1, 38.0, 37.7],
                            borderColor: 'rgba(48, 209, 88, 1)',
                            backgroundColor: 'rgba(48, 209, 88, 0.1)',
                            tension: 0.4,
                            borderWidth: 2,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        aspectRatio: 1,
                        scales: {
                            y: {
                                beginAtZero: false,
                                min: 35,
                                max: 42,
                                grid: {
                                    display: true,
                                    color: 'rgba(200, 200, 200, 0.1)'
                                }
                            },
                            x: {
                                grid: {
                                    display: false
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                position: 'top',
                                align: 'end',
                                labels: {
                                    boxWidth: 10,
                                    usePointStyle: true
                                }
                            }
                        }
                    }
                });
                
                // Update chart periodically
                setInterval(() => {
                    if (MachineControls.isMachineOn) {
                        const data = this.charts.tempChart.data.datasets[0].data;
                        const optimalData = this.charts.tempChart.data.datasets[1].data;
                        
                        // Shift all data points to the left
                        data.shift();
                        optimalData.shift();
                        
                        // Add new random data point with more variance
                        data.push(38 + (Math.random() * 3.5 - 1.75));
                        optimalData.push(38 + (Math.random() * 0.5 - 0.25));
                        
                        this.charts.tempChart.update('none');
                    }
                }, 5000);
            }
            // Developer temperature chart
            const devTempCtx = document.getElementById('developer-temp-chart');
            if (devTempCtx) {
                const hoursLabels = [];
                for (let i = 24; i >= 0; i--) {
                    hoursLabels.push(i === 0 ? 'Now' : `${i}h ago`);
                }
                
                this.charts.devTempChart = new Chart(devTempCtx, {
                    type: 'line',
                    data: {
                        labels: hoursLabels,
                        datasets: [{
                            label: 'Temperature (°C)',
                            data: Array.from({length: 25}, () => 37 + Math.random() * 2),
                            borderColor: 'rgba(48, 209, 88, 1)',
                            backgroundColor: 'rgba(48, 209, 88, 0.1)',
                            tension: 0.4,
                            borderWidth: 2,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        aspectRatio: 1.5,
                        scales: {
                            y: {
                                beginAtZero: false,
                                min: 35,
                                max: 40,
                                grid: {
                                    display: true,
                                    color: 'rgba(200, 200, 200, 0.1)'
                                }
                            },
                            x: {
                                grid: {
                                    display: false
                                },
                                ticks: {
                                    maxRotation: 0,
                                    autoSkip: true,
                                    maxTicksLimit: 8
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            }
                        }
                    }
                });
            }
        } else {
            console.warn('Chart.js not loaded. Charts disabled.');
        }
    },
    
    /**
     * Update machine gauge
     * @param {string} gaugeId - The ID of the gauge element
     * @param {number} value - The value to display
     * @param {number} min - Minimum scale value
     * @param {number} max - Maximum scale value
     * @param {string} unit - Unit to display
     * @param {Object} colorStops - Color stops for the gauge
     * @param {boolean} isPlaceholder - Whether this is a placeholder update
     */
    updateMachineGauge: function(gaugeId, value, min, max, unit, colorStops, isPlaceholder = false) {
        console.log(`Updating gauge ${gaugeId} with value ${value}`);
        
        // Get the value element
        const valueElement = document.getElementById(gaugeId);
        
        if (!valueElement) {
            console.warn(`Element with ID ${gaugeId} not found`);
            return;
        }
        
        // Get the fill element ID
        // If ID is something like 'motor0-speed-value', the fill ID should be 'motor0-speed-fill'
        let fillId;
        if (gaugeId.endsWith('-value')) {
            fillId = gaugeId.replace('-value', '-fill');
        } else {
            fillId = gaugeId + '-fill';
        }
        
        const fillElement = document.getElementById(fillId);
        
        if (!fillElement) {
            console.warn(`Fill element with ID ${fillId} not found for gauge ${gaugeId}`);
        }
        
        // Format the value display with units
        const displayValue = (isPlaceholder || value === null || value === undefined) 
            ? `N/A ${unit}` 
            : `${value} ${unit}`;
        
        // Update the displayed value
        valueElement.innerText = displayValue;
        
        // Add or remove placeholder styling
        if (isPlaceholder) {
            valueElement.classList.add('placeholder');
        } else {
            valueElement.classList.remove('placeholder');
        }
        
        // If we have access to a fill element, update it
        if (fillElement && !isPlaceholder && value !== null && value !== undefined) {
            // Calculate percentage for the progress bar
            let percentage = ((value - min) / (max - min)) * 100;
            percentage = Math.max(0, Math.min(100, percentage)); // Clamp between 0-100%
            
            console.log(`Setting ${fillId} width to ${percentage}%`);
            
            // Apply the percentage to the fill element
            fillElement.style.width = `${percentage}%`;
            
            // Apply color stops if provided
            if (colorStops) {
                // Find the color based on the percentage
                let color = '#5ac8fa'; // Default color
                
                for (const stop of colorStops) {
                    if (percentage <= stop.percentage) {
                        color = stop.color;
                        break;
                    }
                }
                
                fillElement.style.backgroundColor = color;
            }
        } else if (fillElement && isPlaceholder) {
            // Set width to 0 for placeholder
            fillElement.style.width = '0%';
        }
    },
    
    /**
     * Update position display
     * @param {string} elementId - The ID of the element to update
     * @param {number} position - The position value
     * @param {boolean} isPlaceholder - Whether this is a placeholder update
     */
    updatePositionDisplay: function(elementId, position, isPlaceholder = false) {
        console.log(`Updating position display ${elementId} with value ${position}`);
        const element = document.getElementById(elementId);
        if (!element) {
            console.warn(`Position display element with ID ${elementId} not found`);
            return;
        }
        
        // Update the text content
        element.innerText = isPlaceholder ? 'N/A' : position;
        
        // Add or remove placeholder styling
        if (isPlaceholder) {
            element.classList.add('placeholder');
        } else {
            element.classList.remove('placeholder');
        }
    },
    
    /**
     * Update motor state indicator
     * @param {string} elementId - The ID of the element to update
     * @param {string} state - The state to display
     */
    updateMotorStateIndicator: function(elementId, state) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        // Reset classes
        element.classList.remove('stopped', 'running-cw', 'running-ccw', 'error', 'disconnected');
        
        // Add appropriate class
        element.classList.add(state);
        
        // Update text
        let stateText = 'Stopped';
        let icon = '<i class="fas fa-stop-circle"></i>';
        
        switch (state) {
            case 'running-cw':
                stateText = 'Running CW';
                icon = '<i class="fas fa-arrow-circle-right fa-spin"></i>';
                break;
            case 'running-ccw':
                stateText = 'Running CCW';
                icon = '<i class="fas fa-arrow-circle-left fa-spin"></i>';
                break;
            case 'error':
                stateText = 'Error';
                icon = '<i class="fas fa-exclamation-circle"></i>';
                break;
            case 'disconnected':
                stateText = 'Disconnected';
                icon = '<i class="fas fa-unlink"></i>';
                break;
        }
        
        element.innerHTML = `${icon} ${stateText}`;
    }
}; 