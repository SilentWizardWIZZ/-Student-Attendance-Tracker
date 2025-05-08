// Dashboard charts configuration
function initDashboardCharts(dates, presentCounts, absentCounts) {
    // Attendance trend chart
    const trendCtx = document.getElementById('attendanceTrendChart');
    if (trendCtx) {
        // Format dates for display (MM-DD)
        const displayDates = dates.map(date => {
            const dateParts = date.split('-');
            return `${dateParts[1]}-${dateParts[2]}`;
        });
        
        // Only show the last 10 days for better readability
        const daysToShow = 10;
        const lastDates = displayDates.slice(-daysToShow);
        const lastPresentCounts = presentCounts.slice(-daysToShow);
        const lastAbsentCounts = absentCounts.slice(-daysToShow);
        
        new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: lastDates,
                datasets: [
                    {
                        label: 'Present',
                        data: lastPresentCounts,
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.2)',
                        tension: 0.1,
                        fill: true
                    },
                    {
                        label: 'Absent',
                        data: lastAbsentCounts,
                        borderColor: '#dc3545',
                        backgroundColor: 'rgba(220, 53, 69, 0.2)',
                        tension: 0.1,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Attendance Trend (Last 10 Days)'
                    }
                }
            }
        });
    }
    
    // Current day attendance summary chart
    const summaryCtx = document.getElementById('attendanceSummaryChart');
    if (summaryCtx) {
        // Get the last day values
        const presentToday = presentCounts[presentCounts.length - 1] || 0;
        const absentToday = absentCounts[absentCounts.length - 1] || 0;
        
        new Chart(summaryCtx, {
            type: 'doughnut',
            data: {
                labels: ['Present', 'Absent'],
                datasets: [{
                    data: [presentToday, absentToday],
                    backgroundColor: [
                        'rgba(40, 167, 69, 0.8)',
                        'rgba(220, 53, 69, 0.8)'
                    ],
                    borderColor: [
                        'rgba(40, 167, 69, 1)',
                        'rgba(220, 53, 69, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Today\'s Attendance'
                    }
                }
            }
        });
    }
}

// Reports page chart
function initReportsChart(students) {
    const reportsChartCtx = document.getElementById('reportsChart');
    if (reportsChartCtx && students && students.length > 0) {
        const studentNames = students.map(student => `${student.first_name} ${student.last_name}`);
        const attendancePercentages = students.map(student => student.attendance_percentage);
        
        new Chart(reportsChartCtx, {
            type: 'bar',
            data: {
                labels: studentNames,
                datasets: [{
                    label: 'Attendance %',
                    data: attendancePercentages,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Attendance Percentage'
                        }
                    },
                    x: {
                        ticks: {
                            autoSkip: false,
                            maxRotation: 90,
                            minRotation: 45
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Monthly Attendance Percentage by Student'
                    }
                }
            }
        });
    }
}