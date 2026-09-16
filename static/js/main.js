// Ganesh Mandal 2026 Interactive JavaScript Helper

document.addEventListener('DOMContentLoaded', function () {
    // Initialize Dashboard Charts if chart container exists
    const categoryChartCtx = document.getElementById('expenseCategoryChart');
    const paymentChartCtx = document.getElementById('paymentMethodChart');
    const trendChartCtx = document.getElementById('dailyTrendChart');

    if (categoryChartCtx && paymentChartCtx && trendChartCtx) {
        fetch('/api/dashboard-charts')
            .then(res => res.json())
            .then(data => {
                // 1. Expense Categories Doughnut Chart
                new Chart(categoryChartCtx, {
                    type: 'doughnut',
                    data: {
                        labels: data.categories.labels,
                        datasets: [{
                            data: data.categories.data,
                            backgroundColor: [
                                '#E65100', '#FF8F00', '#FFC107', '#2E7D32',
                                '#1565C0', '#6A1B9A', '#AD1457', '#00838F', '#424242'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { position: 'bottom' }
                        }
                    }
                });

                // 2. Payment Method Distribution Pie Chart
                new Chart(paymentChartCtx, {
                    type: 'pie',
                    data: {
                        labels: data.payment_methods.labels,
                        datasets: [{
                            data: data.payment_methods.data,
                            backgroundColor: ['#2E7D32', '#1565C0', '#E65100']
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { position: 'bottom' }
                        }
                    }
                });

                // 3. Daily Trends Line Chart
                new Chart(trendChartCtx, {
                    type: 'line',
                    data: {
                        labels: data.daily_trends.dates,
                        datasets: [
                            {
                                label: 'जमा (Income)',
                                data: data.daily_trends.income,
                                borderColor: '#2E7D32',
                                backgroundColor: 'rgba(46, 125, 50, 0.1)',
                                fill: true,
                                tension: 0.3
                            },
                            {
                                label: 'खर्च (Expenses)',
                                data: data.daily_trends.expenses,
                                borderColor: '#C62828',
                                backgroundColor: 'rgba(198, 40, 40, 0.1)',
                                fill: true,
                                tension: 0.3
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: { beginAtZero: true }
                        }
                    }
                });
            })
            .catch(err => console.error("Chart loading error:", err));
    }
});

function printReceipt() {
    window.print();
}
