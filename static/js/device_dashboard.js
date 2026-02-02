class DeviceDashboard {
    constructor() {
        this.currentDevice = null;
        this.currentPeriod = '24h';
        this.currentDeviceType = null;
        this.charts = {};
        this.initialize();
    }
    
    initialize() {
        this.bindEvents();
        this.updateDeviceGrid();
    }
    
    bindEvents() {
        document.addEventListener('click', (e) => {
            const deviceCard = e.target.closest('.device-card');
            if (deviceCard) {
                this.selectDevice(
                    deviceCard.dataset.deviceId,
                    deviceCard.dataset.deviceType,
                    deviceCard.dataset.deviceName
                );
            }
            
            const periodBtn = e.target.closest('.time-period-btn');
            if (periodBtn) {
                this.selectPeriod(periodBtn.dataset.period);
            }
        });
    }
    
    selectDevice(deviceId, deviceType, deviceName) {
        if (this.currentDevice === deviceId) return;
        
        this.currentDevice = deviceId;
        this.currentDeviceType = parseInt(deviceType);
        this.updateDeviceGrid();
        
        document.getElementById('no-device-selected').style.display = 'none';
        document.getElementById('dashboard-content').style.display = 'block';
        document.getElementById('selected-device-name').textContent = deviceName;
        
        this.showLoading();
        this.loadDeviceData();
    }
    
    selectPeriod(period) {
        if (this.currentPeriod === period) return;
        
        this.currentPeriod = period;
        document.querySelectorAll('.time-period-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.period === period);
        });
        
        if (this.currentDevice) {
            this.showLoading();
            this.loadDeviceData();
        }
    }
    
    updateDeviceGrid() {
        document.querySelectorAll('.device-card').forEach(card => {
            card.classList.toggle('active', card.dataset.deviceId === this.currentDevice);
        });
    }
    
    async loadDeviceData() {
        try {
            const response = await fetch(`/api/device-chart-data/${this.currentDevice}/?period=${this.currentPeriod}`);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Erro ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.hideLoading();
            
            if (data.error) {
                this.showError(data.error);
                return;
            }
            
            this.updatePeriodSummary();
            this.renderStats(data.stats);
            this.renderConsumptionSummary(data.consumption_summary);
            this.renderCharts(data.charts);
            
        } catch (error) {
            console.error('Erro ao carregar dados:', error);
            this.hideLoading();
            this.showError(`Erro ao carregar dados: ${error.message}`);
        }
    }
    
    updatePeriodSummary() {
        const periodText = {
            '24h': 'Últimas 24 horas',
            '7d': 'Últimos 7 dias', 
            '30d': 'Últimos 30 dias'
        }[this.currentPeriod];
        
        document.getElementById('period-summary-text').textContent = periodText;
    }
    getFriendlyName(dataType) {
        if (dataType.includes('Volume')) return 'Vazão';
        if (dataType.includes('Ampere') || dataType.includes('Gás')) return 'Corrente';
        return dataType;
    }
    
    renderStats(stats) {
        const statsGrid = document.getElementById('stats-grid');
        if (!stats || Object.keys(stats).length === 0) {
            statsGrid.innerHTML = '<div class="empty-state">Nenhuma estatística disponível</div>';
            return;
        }
        
        const statsHTML = Object.entries(stats).map(([dataType, data]) => {
            const unit = this.getUnitForDataType(dataType);
            const colorClass = this.getColorClassForDataType(dataType);
            const comparison = data.trend !== undefined ? data.trend : 0;
            const displayName = this.getFriendlyName(dataType);
            
            return `
                <div class="stat-card ${colorClass}-stat">
                    <div class="stat-value">
                        ${this.formatNumber(data.current, dataType)}
                        <span class="stat-unit">${unit}</span>
                    </div>
                    <div class="stat-label">${displayName} Atual</div>
                    ${comparison !== 0 ? `
                        <div class="stat-comparison ${comparison > 0 ? 'comparison-up' : 'comparison-down'}">
                            ${comparison > 0 ? '↑' : '↓'} ${Math.abs(comparison).toFixed(1)}%
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');
        
        statsGrid.innerHTML = statsHTML;
    }
    
    renderConsumptionSummary(summary) {
        const summaryContainer = document.getElementById('consumption-summary');
        if (!summary || Object.keys(summary).length === 0) {
            summaryContainer.innerHTML = '<div class="empty-state">Nenhum dado de consumo disponível</div>';
            return;
        }
        
        const summaryHTML = Object.entries(summary).map(([dataType, data]) => {
            if (dataType.includes('Ampere') || dataType.includes('Corrente')) {
                return '';
            }

            const unit = this.getUnitForDataType(dataType);
            const displayName = this.getFriendlyName(dataType);

            return `
                <div class="summary-card">
                    <div class="summary-title">Consumo Total (${displayName})</div>
                    <div class="summary-value">
                        ${this.formatNumber(data.total, dataType)}
                        <span class="stat-unit">${unit}</span>
                    </div>
                    ${data.kwh_equivalent ? `
                        <div class="summary-detail">
                            Equivalente: ${data.kwh_equivalent.toFixed(2)} kWh
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');
        
        summaryContainer.innerHTML = summaryHTML;
    }
    
    renderCharts(chartData) {
        const chartsGrid = document.getElementById('charts-grid');
        
        if (!chartData || Object.keys(chartData).length === 0) {
            chartsGrid.innerHTML = '<div class="empty-state">Nenhum gráfico disponível</div>';
            return;
        }
        
        chartsGrid.innerHTML = '';
        
        Object.entries(chartData).forEach(([dataType, data], index) => {
            const chartId = `chart-${Date.now()}-${index}`;
            const colorClass = this.getColorClassForDataType(dataType);
            const unit = this.getUnitForDataType(dataType);
            const displayName = this.getFriendlyName(dataType);
            
            const chartHTML = `
                <div class="chart-container">
                    <div class="chart-header">
                        <div class="chart-title">
                            <i class="icon-${colorClass}"></i>
                            ${displayName}
                        </div>
                        <div class="chart-period">${this.getPeriodLabel()}</div>
                    </div>
                    <div class="chart-canvas-container">
                        <canvas id="${chartId}"></canvas>
                    </div>
                </div>
            `;
            
            chartsGrid.innerHTML += chartHTML;

            requestAnimationFrame(() => {
                this.createChart(chartId, dataType, data, unit);
            });
        });
    }
    
    createChart(canvasId, dataType, data, unit) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const colors = this.getColorsForDataType(dataType);
        const displayName = this.getFriendlyName(dataType);
        
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }
        
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: `${displayName} (${unit})`,
                    data: data.values,
                    borderColor: colors.border,
                    backgroundColor: colors.background,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointBackgroundColor: colors.border,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 3,
                    pointHoverBorderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            font: {
                                size: 14,
                                family: "'Segoe UI', sans-serif"
                            },
                            color: '#2c3e50',
                            padding: 20
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(44, 62, 80, 0.95)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        titleFont: {
                            size: 13,
                            family: "'Segoe UI', sans-serif"
                        },
                        bodyFont: {
                            size: 13,
                            family: "'Segoe UI', sans-serif"
                        },
                        padding: 12,
                        cornerRadius: 8,
                        callbacks: {
                            label: (context) => {
                                const value = context.parsed.y;
                                return `${displayName}: ${this.formatNumber(value, dataType)} ${unit}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            font: {
                                size: 12,
                                family: "'Segoe UI', sans-serif"
                            },
                            color: '#7f8c8d',
                            maxRotation: 45,
                            minRotation: 45
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            font: {
                                size: 12,
                                family: "'Segoe UI', sans-serif"
                            },
                            color: '#7f8c8d',
                            callback: (value) => {
                                return this.formatNumber(value, dataType);
                            }
                        },
                        title: {
                            display: true,
                            text: unit,
                            color: '#7f8c8d',
                            font: {
                                size: 12,
                                family: "'Segoe UI', sans-serif",
                                weight: 'bold'
                            }
                        }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeOutQuart'
                }
            }
        });
        
        this.charts[canvasId] = chart;
    }
    
    getPeriodLabel() {
        return {
            '24h': 'Últimas 24 horas',
            '7d': 'Últimos 7 dias',
            '30d': 'Últimos 30 dias'
        }[this.currentPeriod];
    }
    
    getColorClassForDataType(dataType) {
        if (dataType.includes('Volume') || dataType.includes('Água')) return 'water';
        if (dataType.includes('kWh') || dataType.includes('Energia')) return 'energy';
        if (dataType.includes('Ampere') || dataType.includes('Gás') || dataType.includes('Corrente')) return 'gas';
        return 'water';
    }
    
    getColorsForDataType(dataType) {
        if (dataType.includes('Volume') || dataType.includes('Água')) {
            return {
                border: 'rgba(52, 152, 219, 1)',
                background: 'rgba(52, 152, 219, 0.1)'
            };
        } else if (dataType.includes('kWh') || dataType.includes('Energia')) {
            return {
                border: 'rgba(243, 156, 18, 1)',
                background: 'rgba(243, 156, 18, 0.1)'
            };
        } else {
            return {
                border: 'rgba(231, 76, 60, 1)',
                background: 'rgba(231, 76, 60, 0.1)'
            };
        }
    }
    
    getUnitForDataType(dataType) {
        const units = {
            'Volume (L)': 'L',
            'kWh': 'kWh',
            'Ampere': 'A',
            'Volume Água': 'L',
            'Consumo Energia': 'kWh',
            'Corrente': 'A'
        };
        return units[dataType] || '';
    }
    
    formatNumber(value, dataType) {
        if (value === null || value === undefined) return '0';
        
        if (dataType.includes('kWh') || dataType === 'Consumo Energia') {
            return value.toLocaleString('pt-BR', { minimumFractionDigits: 3, maximumFractionDigits: 3 });
        } else if (dataType.includes('Ampere') || dataType === 'Corrente') {
            return value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        } else {
            return value.toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
        }
    }
    
    showLoading() {
        document.getElementById('loading-container').style.display = 'flex';
        document.getElementById('dashboard-content').style.display = 'none';
    }
    
    hideLoading() {
        document.getElementById('loading-container').style.display = 'none';
        document.getElementById('dashboard-content').style.display = 'block';
    }
    
    showError(message) {
        const errorEl = document.getElementById('error-message');
        errorEl.textContent = message;
        errorEl.style.display = 'block';
        
        setTimeout(() => {
            errorEl.style.display = 'none';
        }, 5000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.deviceDashboard = new DeviceDashboard();
});