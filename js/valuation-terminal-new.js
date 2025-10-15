/**
 * VALUATION TERMINAL - Bloomberg-style Interface
 * Professional crane valuation with comprehensive analysis
 */

class ValuationTerminal {
    constructor() {
        this.currentMode = 'single';
        this.currentTab = 'overview';
        this.valuationData = {};
        this.bulkData = [];
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.charts = {};
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.updateTime();
        this.loadManufacturerModels();
        this.setupCharts();
        
        // Update time every second
        // // setInterval(// DISABLED to prevent flickering // () => this.updateTime(), 1000); // DISABLED to prevent flickering
    }

    setupEventListeners() {
        // Mode switching
        document.querySelectorAll('.mode-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchMode(e.target.closest('.mode-tab').dataset.mode);
            });
        });

        // Tab switching
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchTab(e.target.closest('.tab').dataset.tab);
            });
        });

        // Valuation form
        const valuationForm = document.getElementById('crane-valuation-form');
    if (valuationForm) {
            valuationForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.calculateValuation();
            });
    }
    
    // Manufacturer change
    const manufacturerSelect = document.getElementById('manufacturer');
    if (manufacturerSelect) {
            manufacturerSelect.addEventListener('change', (e) => {
                this.updateModelOptions(e.target.value);
            });
        }

        // Bulk file upload
        const bulkFile = document.getElementById('bulk-file');
        if (bulkFile) {
            bulkFile.addEventListener('change', (e) => {
                this.handleBulkUpload(e.target.files[0]);
            });
        }

        // Pagination
        document.getElementById('prev-page').addEventListener('click', () => {
            this.previousPage();
        });

        document.getElementById('next-page').addEventListener('click', () => {
            this.nextPage();
        });
    }

    updateTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', { 
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        
        document.getElementById('last-update').textContent = timeString;
    }

    switchMode(mode) {
        // Update mode tabs
        document.querySelectorAll('.mode-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-mode="${mode}"]`).classList.add('active');

        // Update mode content
        document.querySelectorAll('.valuation-mode').forEach(modeEl => {
            modeEl.classList.remove('active');
        });
        document.getElementById(`${mode}-valuation`).classList.add('active');

        this.currentMode = mode;
    }

    switchTab(tabName) {
        // Update tab appearance
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        this.currentTab = tabName;

        // Load tab-specific data
        if (tabName === 'analysis') {
            this.loadTrendChart();
        } else if (tabName === 'comparables') {
            this.loadComparablesData();
        }
    }

    loadManufacturerModels() {
    const models = {
            'Liebherr': [
                // Mobile All-Terrain Cranes
                'LTM 1025', 'LTM 1030-2.1', 'LTM 1040-2.1', 'LTM 1050-3.1', 'LTM 1060-3.1',
                'LTM 1070-4.2', 'LTM 1080-2', 'LTM 1090-4.2', 'LTM 1100-5.2', 'LTM 1110-5.1',
                'LTM 1120-4.1', 'LTM 1130-5.1', 'LTM 1160-5.2', 'LTM 1200-5.1', 'LTM 1220-5.2',
                'LTM 1230-5.1', 'LTM 1250-6.1', 'LTM 1300-6.2', 'LTM 1350-6.1', 'LTM 1400-7.1',
                'LTM 1450-8.1', 'LTM 1500-8.1', 'LTM 1650-8.1', 'LTM 1750-9.1', 'LTM 11200-9.1',
                // Mobile City Cranes
                'LTC 1045-3.1', 'LTC 1050-3.1',
                // Mobile Rough Terrain Cranes
                'LRT 1090-2.1', 'LRT 1100-2.1',
                // Mobile Telescopic Crawler Cranes
                'LTR 1040', 'LTR 1060', 'LTR 1100', 'LTR 1220',
                // Crawler Lattice Cranes
                'LR 1100', 'LR 1160', 'LR 1200', 'LR 1250', 'LR 1280', 'LR 1300.1 SX',
                'LR 1350/1', 'LR 1400/2', 'LR 1500', 'LR 1600/2', 'LR 1700-1.0', 'LR 1750/2',
                'LR 1800-1.0', 'LR 11350', 'LR 13000'
            ],
            'Grove': [
                // Mobile All-Terrain Cranes
                'GMK3050-2', 'GMK3060-2', 'GMK3060L-1', 'GMK4090-1', 'GMK4100L-1',
                'GMK4100L-2', 'GMK5150L-1', 'GMK5250L-1', 'GMK5250XL-1', 'GMK6300L-1',
                'GMK6400-1', 'GMK7550',
                // Mobile Rough Terrain Cranes
                'RT530E-2', 'RT540E', 'GRT655', 'GRT655L', 'GRT880', 'GRT8100', 'GRT8120', 'GRT9165',
                // Mobile Truck-Mounted Cranes
                'TMS500-2', 'TMS700E', 'TMS800E', 'TMS9000-2',
                // Mobile Telescopic Crawler Cranes
                'GHC30', 'GHC45', 'GHC55', 'GHC75', 'GHC85', 'GHC130'
            ],
            'Manitowoc': [
                // Crawler Lattice Cranes
                '3900', '4100W', '777', '888', '999', '14000', '16000', '18000', '21000', '2250',
                'MLC100-1', 'MLC150-1', 'MLC300', 'MLC650', '31000'
            ],
            'Tadano': [
                // Mobile Rough Terrain Cranes
                'GR-500XL', 'GR-550XL-3', 'GR-750XL-3', 'GR-800XL-4', 'GR-1000XL-4', 'GR-1200XL',
                // Mobile All-Terrain Cranes
                'ATF 70G-4', 'ATF 110G-5', 'ATF 130G-5', 'ATF 200G-5', 'ATF 220G-5',
                'AC 4.100L-1', 'AC 5.220-1', 'AC 7.450-1',
                // Crawler Lattice Cranes
                'CC 2800-1', 'CC 3800-1', 'CC 6800-1', 'CC 8800-1'
            ],
            'Sany': [
                // Mobile All-Terrain Cranes
                'SAC1200', 'SAC2200', 'SAC2500', 'SAC6000',
                // Mobile Rough Terrain Cranes
                'SRC900',
                // Mobile Truck-Mounted Cranes
                'STC750',
                // Crawler Lattice Cranes
                'SCC1000A', 'SCC1500D', 'SCC2500A', 'SCC4000A', 'SCC6500A', 'SCC8000A', 'SCC10000A'
            ],
            'Kobelco': [
                // Crawler Lattice Cranes
                'CK800G-2', 'CK850G-2', 'CK1000G-2', 'CK1200G-2', 'CK1600G-2', 'CK2000G-2',
                'CK2500G-2', 'CK3300G-2', 'CKE800G-2', 'CKE900G-2', 'CKE1100G-2', 'CKE1350G-2',
                'SL4500', 'SL6000'
            ],
            'American': [
                // Crawler Lattice Cranes
                'American 7250', 'American 7260', 'American 8470', 'American 9299', 'American 9310',
                'HC 50', 'HC 80', 'HC 110', 'HC 165', 'HC 230', 'HC 275', 'HC 285'
            ],
            'Link-Belt': [
                // Crawler Lattice Cranes
                '218 HSL', '238 HSL', '298 HSL', '348 Series 2',
                // Mobile Telescopic Crawler Cranes
                'TCC-1100', 'TCC-2500',
                // Mobile Rough Terrain Cranes
                'RTC-8090',
                // Mobile All-Terrain Cranes
                'ATC-3275'
            ],
            'Demag': [
                // Mobile All-Terrain Cranes
                'AC 100/4L', 'AC 700',
                // Crawler Lattice Cranes
                'CC 2800-1', 'CC 8800-1'
            ],
            'Terex': [
                // Mobile Rough Terrain Cranes
                'RT 780',
                // Mobile All-Terrain Cranes
                'AC 350/6',
                // Crawler Lattice Cranes
                'CC 2800-1'
            ],
            'XCMG': [
                // Crawler Lattice Cranes
                'XGC88000',
                // Mobile Truck-Mounted Cranes
                'XCT100',
                // Mobile All-Terrain Cranes
                'XCA300'
            ],
            'Zoomlion': [
                // Crawler Lattice Cranes
                'ZCC12500', 'ZCC3200NP'
            ],
            'HSC': [
                // Crawler Lattice Cranes
                'SCX1200A-3', 'SCX2800A-3'
            ],
            'Kato': [
                // Mobile Truck-Mounted Cranes
                'NK-250E',
                // Mobile Rough Terrain Cranes
                'KR-35H (MR-350)', 'SR-250R'
            ],
            'IHI': [
                // Crawler Lattice Cranes
                'CCH700', 'CCH2500'
            ]
        };

        this.manufacturerModels = models;
    }

    updateModelOptions(manufacturer) {
    const modelSelect = document.getElementById('model');
        if (!modelSelect) return;

        // Clear existing options
        modelSelect.innerHTML = '<option value="">Select Model</option>';

        if (this.manufacturerModels[manufacturer]) {
            this.manufacturerModels[manufacturer].forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        modelSelect.appendChild(option);
    });
}
    }

    async calculateValuation() {
        const form = document.getElementById('crane-valuation-form');
        if (!form) return;

        const formData = new FormData(form);
        
        const valuationData = {
            crane_make: formData.get('manufacturer'),
            crane_model: formData.get('model'),
            crane_year: parseInt(formData.get('year')),
            crane_hours: parseInt(formData.get('hours')),
            crane_condition: formData.get('condition') || 'good',
            boom_length: parseFloat(formData.get('boom_length')) || null,
            capacity: parseFloat(formData.get('capacity')),
            mileage: parseInt(formData.get('mileage')) || null,
            region: formData.get('region'),
            asking_price: formData.get('asking_price') || null
        };

        try {
            this.showLoading('Calculating valuation...');
    
    const response = await fetch('/api/v1/valuations', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('crane_auth_token') || ''}`
                },
                body: JSON.stringify(valuationData)
            });

            if (response.ok) {
                const result = await response.json();
                this.displayValuationResults(result);
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Valuation calculation failed');
            }
        } catch (error) {
            console.error('Error calculating valuation:', error);
            this.showError('Failed to calculate valuation. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    displayValuationResults(result) {
        // Update main results
        document.getElementById('estimated-value').textContent = this.formatCurrency(result.estimated_value);
        document.getElementById('confidence-score').textContent = `${Math.round(result.confidence_score)}%`;
        document.getElementById('deal-grade').textContent = result.deal_grade;
        
        // Update subtitles
        document.getElementById('market-comparison').textContent = `+2.3% vs market avg`;
        document.getElementById('confidence-level').textContent = result.confidence_level;
        document.getElementById('deal-recommendation').textContent = result.deal_recommendation;

        // Show results
        document.getElementById('valuation-results').style.display = 'block';
        document.getElementById('valuation-results').scrollIntoView({ behavior: 'smooth' });

        // Load charts
        this.loadManufacturerChart();
        this.loadCapacityChart();
        this.loadComparablesData();
    }

    loadManufacturerChart() {
        const container = document.getElementById('manufacturer-chart');
        if (!container) return;

        const data = [
            { manufacturer: 'Liebherr', value: 35 },
            { manufacturer: 'Grove', value: 25 },
            { manufacturer: 'Manitowoc', value: 20 },
            { manufacturer: 'Terex', value: 15 },
            { manufacturer: 'Others', value: 5 }
        ];

        const trace = {
            values: data.map(d => d.value),
            labels: data.map(d => d.manufacturer),
            type: 'pie',
            marker: {
                colors: ['#00ff85', '#00cc6a', '#00b359', '#00994d', '#008040']
            }
        };

        const layout = {
            title: 'Market Share by Manufacturer',
            paper_bgcolor: '#333',
            plot_bgcolor: '#333',
            font: { color: '#fff' },
            showlegend: true,
            legend: {
                x: 0.5,
                y: 0.5
            }
        };

        Plotly.newPlot(container, [trace], layout, { responsive: true });
    }

    loadCapacityChart() {
        const container = document.getElementById('capacity-chart');
        if (!container) return;

        const data = {
            x: ['0-30T', '30-100T', '100-200T', '200-300T', '300-500T', '>500T'],
            y: [15, 25, 35, 20, 15, 10],
            type: 'bar',
            marker: { color: '#00ff85' }
        };

        const layout = {
            title: 'Capacity Distribution',
            paper_bgcolor: '#333',
            plot_bgcolor: '#333',
            font: { color: '#fff' },
            xaxis: { color: '#ccc' },
            yaxis: { color: '#ccc' }
        };

        Plotly.newPlot(container, [data], layout, { responsive: true });
    }

    loadTrendChart() {
        const container = document.getElementById('trend-chart');
        if (!container) return;

        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const data1 = [1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3];
        const data2 = [1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2];

        const trace1 = {
            x: months,
            y: data1,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Market Index',
            line: { color: '#00ff85' }
        };

        const trace2 = {
            x: months,
            y: data2,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Equipment Index',
            line: { color: '#ffc107' }
        };

        const layout = {
            title: 'Valuation Trend Analysis',
            paper_bgcolor: '#333',
            plot_bgcolor: '#333',
            font: { color: '#fff' },
            xaxis: { color: '#ccc' },
            yaxis: { color: '#ccc' }
        };

        Plotly.newPlot(container, [trace1, trace2], layout, { responsive: true });
    }

    loadComparablesData() {
        const tbody = document.getElementById('comparables-tbody');
        if (!tbody) return;

        const comparables = [
            { equipment: 'LIEBHERR LTM1550-6.1', year: 2022, capacity: 350, hours: 1200, price: 2145000, pricePerTon: 6122, trend: '+2.3%', location: 'North America' },
            { equipment: 'GROVE GMK5250L', year: 2021, capacity: 250, hours: 1800, price: 1890000, pricePerTon: 7560, trend: '+1.8%', location: 'Europe' },
            { equipment: 'TADANO ATF400G-6', year: 2020, capacity: 400, hours: 2300, price: 2650000, pricePerTon: 6625, trend: '-0.5%', location: 'Asia Pacific' },
            { equipment: 'MANITOWOC MLC300', year: 2019, capacity: 300, hours: 2800, price: 1750000, pricePerTon: 5833, trend: '+3.1%', location: 'North America' }
        ];

        tbody.innerHTML = comparables.map(item => `
            <tr>
            <td>${item.equipment}</td>
            <td>${item.year}</td>
                <td>${item.capacity}T</td>
                <td>${item.hours.toLocaleString()}</td>
                <td>${this.formatCurrency(item.price)}</td>
                <td>${this.formatCurrency(item.pricePerTon)}</td>
                <td class="${item.trend.startsWith('+') ? 'positive' : 'negative'}">${item.trend}</td>
            <td>${item.location}</td>
            </tr>
        `).join('');
    }

    async handleBulkUpload(file) {
        if (!file) return;

        try {
            this.showLoading('Processing bulk upload...');

            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/v1/valuation/bulk', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                this.displayBulkResults(result);
    } else {
                throw new Error('Bulk processing failed');
            }
        } catch (error) {
            console.error('Error processing bulk upload:', error);
            this.showError('Failed to process bulk upload. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    displayBulkResults(result) {
        this.bulkData = result.data || [];
        this.currentPage = 1;
        
        document.getElementById('total-processed').textContent = result.processed_count || 0;
        document.getElementById('successful-valuations').textContent = result.successful_count || 0;
        document.getElementById('failed-valuations').textContent = result.failed_count || 0;
        
        document.getElementById('bulk-results').style.display = 'block';
        this.updateBulkTable();
        this.updatePagination();
    }

    updateBulkTable() {
        const tbody = document.getElementById('bulk-results-tbody');
        if (!tbody) return;

        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageData = this.bulkData.slice(startIndex, endIndex);

        tbody.innerHTML = pageData.map((item, index) => `
            <tr>
                <td>${item.equipment || 'N/A'}</td>
                <td>${item.year || 'N/A'}</td>
                <td>${item.capacity || 'N/A'}</td>
                <td>${item.hours || 'N/A'}</td>
                <td>${item.estimated_value ? this.formatCurrency(item.estimated_value) : 'N/A'}</td>
                <td>${item.confidence_score ? `${Math.round(item.confidence_score)}%` : 'N/A'}</td>
                <td>${item.deal_grade || 'N/A'}</td>
                <td>
                    <button class="btn-secondary" onclick="terminal.viewBulkDetails(${startIndex + index})">View</button>
                </td>
            </tr>
        `).join('');
    }

    updatePagination() {
        const totalPages = Math.ceil(this.bulkData.length / this.itemsPerPage);
        const startItem = (this.currentPage - 1) * this.itemsPerPage + 1;
        const endItem = Math.min(this.currentPage * this.itemsPerPage, this.bulkData.length);
        
        document.getElementById('pagination-info').textContent = 
            `Showing ${startItem}-${endItem} of ${this.bulkData.length} results`;
        
        document.getElementById('prev-page').disabled = this.currentPage === 1;
        document.getElementById('next-page').disabled = this.currentPage === totalPages;
        
        const pageNumbers = document.getElementById('page-numbers');
        pageNumbers.innerHTML = '';
        
        for (let i = 1; i <= totalPages; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.className = `page-number ${i === this.currentPage ? 'active' : ''}`;
            pageBtn.textContent = i;
            pageBtn.onclick = () => this.goToPage(i);
            pageNumbers.appendChild(pageBtn);
        }
    }

    goToPage(page) {
        this.currentPage = page;
        this.updateBulkTable();
        this.updatePagination();
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.goToPage(this.currentPage - 1);
        }
    }

    nextPage() {
        const totalPages = Math.ceil(this.bulkData.length / this.itemsPerPage);
        if (this.currentPage < totalPages) {
            this.goToPage(this.currentPage + 1);
        }
    }

    viewBulkDetails(index) {
        const item = this.bulkData[index];
        console.log('Viewing details for:', item);
        // Implement detailed view modal
    }

    setupCharts() {
        // Initialize Chart.js defaults
        Chart.defaults.color = '#fff';
        Chart.defaults.borderColor = '#333';
        Chart.defaults.backgroundColor = 'rgba(0, 255, 133, 0.1)';
    }

    formatCurrency(amount) {
        if (amount >= 1000000) {
            return `$${(amount / 1000000).toFixed(2)}M`;
        } else {
            return `$${amount.toLocaleString()}`;
        }
    }

    showLoading(message) {
        console.log('Loading:', message);
        // Implement loading indicator
    }

    hideLoading() {
        console.log('Loading complete');
        // Hide loading indicator
    }

    showError(message) {
        console.error('Error:', message);
        alert(message);
    }

    showSuccess(message) {
        console.log('Success:', message);
        alert(message);
    }
}

// Tool Functions
function openBuildNotes() {
    document.getElementById('build-notes-modal').style.display = 'block';
}

function openCalendar() {
    document.getElementById('calendar-modal').style.display = 'block';
}

function openUnitConverter() {
    document.getElementById('unit-converter-modal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function saveBuildNotes() {
    const notes = document.getElementById('build-notes-text').value;
    console.log('Saving build notes:', notes);
    closeModal('build-notes-modal');
}

function convertUnits() {
    const fromValue = parseFloat(document.getElementById('from-value').value);
    const fromUnit = document.getElementById('from-unit').value;
    const toUnit = document.getElementById('to-unit').value;
    
    if (!fromValue) return;
    
    // Conversion factors to tons
    const factors = {
        'tons': 1,
        'kg': 0.001,
        'lbs': 0.000453592
    };
    
    const tons = fromValue * factors[fromUnit];
    const result = tons / factors[toUnit];
    
    document.getElementById('to-value').value = result.toFixed(2);
}

function loadSampleData() {
    document.getElementById('manufacturer').value = 'Terex';
    document.getElementById('model').value = 'AC 500-2';
    document.getElementById('year').value = '2022';
    document.getElementById('capacity').value = '300';
    document.getElementById('hours').value = '3700';
    document.getElementById('mileage').value = '15000';
    document.getElementById('boomLength').value = '60';  // Sample boom length
    document.getElementById('condition').value = 'excellent';  // Sample condition
    document.getElementById('region').value = 'North America';
    document.getElementById('asking-price').value = '3,500,000';
    
    // Update model options
    terminal.updateModelOptions('Terex');
}

function exportResults(format) {
    console.log(`Exporting results as ${format}`);
    // Implement export functionality
}

// Initialize terminal when page loads
let terminal;
document.addEventListener('DOMContentLoaded', () => {
    terminal = new ValuationTerminal();
});