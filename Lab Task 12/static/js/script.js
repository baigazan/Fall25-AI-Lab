// ========================================
// THEME MANAGEMENT
// ========================================

// Initialize theme from localStorage or default to light
const initializeTheme = () => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
};

// Update theme icon based on current theme
const updateThemeIcon = (theme) => {
    const themeIcon = document.getElementById('themeIcon');
    if (theme === 'dark') {
        themeIcon.classList.remove('bi-moon-fill');
        themeIcon.classList.add('bi-sun-fill');
    } else {
        themeIcon.classList.remove('bi-sun-fill');
        themeIcon.classList.add('bi-moon-fill');
    }
};

// Toggle theme
const toggleTheme = () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
    
    // Update chart if it exists
    if (salaryChart) {
        updateChartTheme(newTheme);
    }
};

// ========================================
// CHART MANAGEMENT
// ========================================

let salaryChart = null;

// Create salary comparison chart
const createSalaryChart = (predictedSalary, avgSalary) => {
    const ctx = document.getElementById('salaryChart').getContext('2d');
    const theme = document.documentElement.getAttribute('data-theme');
    const textColor = theme === 'dark' ? '#e6edf3' : '#212529';
    const gridColor = theme === 'dark' ? '#30363d' : '#dee2e6';
    
    // Destroy existing chart if it exists
    if (salaryChart) {
        salaryChart.destroy();
    }
    
    salaryChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Your Predicted Salary', 'Average Salary'],
            datasets: [{
                label: 'Salary ($)',
                data: [predictedSalary, avgSalary],
                backgroundColor: [
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(118, 75, 162, 0.8)'
                ],
                borderColor: [
                    'rgba(102, 126, 234, 1)',
                    'rgba(118, 75, 162, 1)'
                ],
                borderWidth: 2,
                borderRadius: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Salary Comparison',
                    color: textColor,
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: {
                        bottom: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: {
                        size: 14
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        label: function(context) {
                            return '$' + context.parsed.y.toLocaleString('en-US', {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                            });
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: textColor,
                        callback: function(value) {
                            return '$' + value.toLocaleString('en-US');
                        }
                    },
                    grid: {
                        color: gridColor
                    }
                },
                x: {
                    ticks: {
                        color: textColor
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
};

// Update chart theme
const updateChartTheme = (theme) => {
    if (salaryChart) {
        const textColor = theme === 'dark' ? '#e6edf3' : '#212529';
        const gridColor = theme === 'dark' ? '#30363d' : '#dee2e6';
        
        salaryChart.options.plugins.title.color = textColor;
        salaryChart.options.scales.y.ticks.color = textColor;
        salaryChart.options.scales.x.ticks.color = textColor;
        salaryChart.options.scales.y.grid.color = gridColor;
        
        salaryChart.update();
    }
};

// ========================================
// ALERT MANAGEMENT
// ========================================

// Show alert message
const showAlert = (message, type = 'danger') => {
    const alertContainer = document.getElementById('alertContainer');
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        <i class="bi bi-${type === 'danger' ? 'exclamation-triangle-fill' : 'check-circle-fill'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.innerHTML = '';
    alertContainer.appendChild(alertDiv);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentElement) {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 150);
        }
    }, 5000);
};

// ========================================
// FORM HANDLING
// ========================================

// Handle form submission
const handleFormSubmit = async (e) => {
    e.preventDefault();
    
    // Get form values
    const experience = parseFloat(document.getElementById('experience').value);
    const age = parseFloat(document.getElementById('age').value);
    const gender = document.querySelector('input[name="gender"]:checked').value;
    const jobTitle = document.getElementById('jobTitle').value;
    const education = document.getElementById('education').value;
    
    // Validate inputs
    if (isNaN(experience) || isNaN(age)) {
        showAlert('Please enter valid numeric values for experience and age.', 'danger');
        return;
    }
    
    if (experience < 0 || experience > 50) {
        showAlert('Experience years must be between 0 and 50.', 'danger');
        return;
    }
    
    if (age < 18 || age > 100) {
        showAlert('Age must be between 18 and 100.', 'danger');
        return;
    }
    
    if (!jobTitle) {
        showAlert('Please select a job title.', 'danger');
        return;
    }
    
    if (!education) {
        showAlert('Please select an education level.', 'danger');
        return;
    }
    
    // Show loading state
    const submitBtn = document.querySelector('.predict-btn');
    const buttonText = submitBtn.querySelector('.button-text');
    const spinner = submitBtn.querySelector('.spinner-border');
    
    submitBtn.classList.add('loading');
    submitBtn.disabled = true;
    buttonText.classList.add('d-none');
    spinner.classList.remove('d-none');
    
    // Hide previous results
    document.getElementById('resultsSection').classList.add('d-none');
    document.getElementById('alertContainer').innerHTML = '';
    
    try {
        // Make API request
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                experience_years: experience,
                age: age,
                gender: gender,
                job_title: jobTitle,
                education_level: education
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Display results
            displayResults(data);
            showAlert('Prediction successful! 🎉', 'success');
        } else {
            // Show error message
            showAlert(data.error || 'An error occurred during prediction.', 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('Failed to connect to the server. Please try again.', 'danger');
    } finally {
        // Reset button state
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
        buttonText.classList.remove('d-none');
        spinner.classList.add('d-none');
    }
};

// ========================================
// RESULTS DISPLAY
// ========================================

// Display prediction results
const displayResults = (data) => {
    // Update predicted salary
    document.getElementById('predictedSalary').textContent = 
        '$' + data.predicted_salary.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    
    // Update percentile
    document.getElementById('percentile').textContent = data.percentile;
    
    // Update input summary
    document.getElementById('displayExperience').textContent = 
        data.input_data.experience_years + ' years';
    document.getElementById('displayAge').textContent = data.input_data.age;
    document.getElementById('displayGender').textContent = data.input_data.gender;
    document.getElementById('displayJobTitle').textContent = data.input_data.job_title;
    document.getElementById('displayEducation').textContent = data.input_data.education_level;
    
    // Update progress bar
    const progressBar = document.getElementById('salaryProgress');
    const progressText = progressBar.querySelector('.progress-text');
    progressBar.style.width = data.percentile + '%';
    progressBar.setAttribute('aria-valuenow', data.percentile);
    progressText.textContent = data.percentile + '%';
    
    // Create/update chart
    createSalaryChart(data.predicted_salary, data.average_salary);
    
    // Show results section with animation
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.classList.remove('d-none');
    
    // Smooth scroll to results
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
};

// ========================================
// EVENT LISTENERS
// ========================================

// Load job titles from file
const loadJobTitles = async () => {
    try {
        const response = await fetch('/static/job_titles.txt');
        const text = await response.text();
        const jobTitles = text.trim().split('\n');
        
        const datalist = document.getElementById('jobTitlesList');
        jobTitles.forEach(title => {
            const option = document.createElement('option');
            option.value = title;
            datalist.appendChild(option);
        });
        
        console.log(`Loaded ${jobTitles.length} job titles`);
    } catch (error) {
        console.error('Error loading job titles:', error);
    }
};

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    // Initialize theme
    initializeTheme();
    
    // Load job titles
    loadJobTitles();
    
    // Theme toggle button
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);
    
    // Form submission
    document.getElementById('predictionForm').addEventListener('submit', handleFormSubmit);
    
    // Input validation - prevent negative values
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('input', (e) => {
            if (e.target.value < 0) {
                e.target.value = 0;
            }
        });
    });
    
    // Add smooth transitions to form elements
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(control => {
        control.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.01)';
        });
        
        control.addEventListener('blur', function() {
            this.parentElement.style.transform = 'scale(1)';
        });
    });
});

// ========================================
// UTILITY FUNCTIONS
// ========================================

// Format currency
const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount);
};

// Validate number in range
const validateRange = (value, min, max) => {
    return value >= min && value <= max;
};

// ========================================
// KEYBOARD SHORTCUTS
// ========================================

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter to submit form
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        document.getElementById('predictionForm').dispatchEvent(new Event('submit'));
    }
    
    // Ctrl/Cmd + D to toggle theme
    if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault();
        toggleTheme();
    }
});
