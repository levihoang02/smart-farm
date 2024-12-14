// Function to show status message




function showMessage(message, isError = false) {
    const statusDiv = document.getElementById('statusMessage');
    statusDiv.textContent = message;
    statusDiv.className = `status-message ${isError ? 'error' : 'success'}`;
    setTimeout(() => {
        statusDiv.textContent = '';
        statusDiv.className = 'status-message';
    }, 3000);
}

// Function to fetch all thresholds
async function getThresholds() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('http://localhost:5000/threshold', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            credentials: 'include'
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            data.thresholds.forEach(threshold => {
                localStorage.setItem(threshold.sensor, threshold.value);
                const input = document.querySelector(`input[data-sensor="${threshold.sensor}"]`);
                if (input) {
                    input.value = threshold.value;
                }
            });
        } else {
            showMessage('Failed to fetch thresholds: ' + data.message, true);
        }
    } catch (error) {
        showMessage('Error fetching thresholds: ' + error.message, true);
    }
}

// Function to update threshold
async function updateThreshold(sensor, value) {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('http://localhost:5000/threshold/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            credentials: 'include',
            body: JSON.stringify({
                sensor: sensor,
                value: parseFloat(value)
            })
        });
        
        const data = await response.json();
        if (data.status === 'success') {
            localStorage.setItem(sensor, value);
            showMessage('Threshold updated successfully');
        } else {
            showMessage('Failed to update threshold: ' + data.message, true);
        }
    } catch (error) {
        showMessage('Error updating threshold: ' + error.message, true);
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Load initial thresholds
    getThresholds();

    // Add event listeners to threshold inputs
    const thresholdInputs = document.querySelectorAll('.threshold-input');
    thresholdInputs.forEach(input => {
        input.addEventListener('change', (e) => {
            const sensor = e.target.dataset.sensor;
            const value = e.target.value;
            if (value === '' || isNaN(value)) {
                showMessage('Please enter a valid number', true);
                return;
            }
            updateThreshold(sensor, value);
        });
    });
});

function logout() {
    const token = localStorage.getItem('token');
    fetch('http://localhost:5000/logout', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            localStorage.removeItem('token'); // Remove token on logout
            window.location.href = 'login.html';
        }
    });
}