// Initialize Charts
const temperatureCtx = document.getElementById('temperatureChart').getContext('2d');
const humidityCtx = document.getElementById('humidityChart').getContext('2d');

// Temperature Line Chart
const temperatureChart = new Chart(temperatureCtx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Temperature °C',
            data: [],
            borderColor: 'rgb(255, 99, 132)',
            tension: 0.1,
            fill: false
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: false
            }
        }
    }
});

// Metrics Gauge Chart
const humidityChart = new Chart(humidityCtx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Humidity QV2M',
            data: [],
            borderColor: 'rgb(54, 162, 235)',
            tension: 0.1,
            fill: false
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: false
            }
        }
    }
});

// Keep track of time series data
const maxDataPoints = 20;
const temperatureData = [];
const humidityData = [];

document.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }
});

const token = localStorage.getItem('token');
const socket = io("http://localhost:5000", {
    withCredentials: true,
    extraHeaders: {
        Authorization: `Bearer ${token}`
    }
});

const statusElement = document.getElementById('connection-status');

socket.on("connect", () => {
    console.log("Connected to WebSocket server");
    statusElement.className = 'alert alert-success';
    statusElement.textContent = 'Connected to server';
});

function checkThreshold(elementId, value, threshold) {
    const card = document.getElementById(`${elementId}-card`);
    if (value >= threshold) {
        card.classList.add('alert-threshold');
    } else {
        card.classList.remove('alert-threshold');
    }
}

socket.on("sensor_data", (res) => {
    try {
        console.log("Received Kafka message:", res);
        checkThresholds(res.data["Temperature"], res.data["Humidity"]);
        
        // Update temperature value
        const tempElement = document.getElementById('temperature');
        const humidityElement = document.getElementById('humidity');
        if (tempElement && humidityElement) {
            const temp = res.data["Temperature"];
            const humidity = res.data["Humidity"];
            tempElement.textContent = temp.toFixed(1);
            humidityElement.textContent = humidity.toFixed(1);
            checkThreshold('temperature', temp, TEMP_ALERT_THRESHOLD);
            checkThreshold('humidity', humidity, HUMIDITY_ALERT_THRESHOLD);

            // Update temperature chart
            const timestamp = new Date().toLocaleTimeString();
            temperatureData.push({ time: timestamp, temp: temp });
            
            // Keep only last maxDataPoints
            if (temperatureData.length > maxDataPoints) {
                temperatureData.shift();
            }

            temperatureChart.data.labels = temperatureData.map(data => data.time);
            temperatureChart.data.datasets[0].data = temperatureData.map(data => data.temp);
            temperatureChart.update();

            // Update humidity chart
            humidityData.push({ time: timestamp, humidity: humidity });
            if (humidityData.length > maxDataPoints) {
                humidityData.shift();
            }
            humidityChart.data.labels = humidityData.map(data => data.time);
            humidityChart.data.datasets[0].data = humidityData.map(data => data.humidity);
            humidityChart.update();
        }

    } catch(err) {
        console.error(err);
    }
});

function checkThresholds(temperature, humidity) {
    if (temperature > TEMP_ALERT_THRESHOLD) {
        console.log("Temperature is above threshold of ${TEMP_ALERT_THRESHOLD}°C!");
        let alertMessage = `Temperature (${temperature}°C) is above threshold of ${TEMP_ALERT_THRESHOLD}°C!\n`;
        showToast(alertMessage);
    }
    
    if (humidity > HUMIDITY_ALERT_THRESHOLD) {
        let alertMessage = `Humidity (${humidity}) is above threshold of ${HUMIDITY_ALERT_THRESHOLD}!`;
        showToast(alertMessage);
    }
};

const showToast = (message) => {
    let toastContainer = document.getElementById('toast-container');
    const toast = document.createElement('div');
        toast.className = 'toast';
        toast.role = 'alert';
        toast.ariaLive = 'assertive';
        toast.ariaAtomic = 'true';
    toast.innerHTML = `
        <div class="toast-header">
            <strong class="me-auto">Sensor Alert</strong>
            <small class="text-muted">${new Date().toLocaleTimeString()}</small>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                                </div>
                                <div class="toast-body">
            ${message}
        </div>`;
    toastContainer.insertBefore(toast, toastContainer.firstChild);
    const toastBootstrap = new bootstrap.Toast(toast);
    toastBootstrap.show();

    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
};

socket.on("disconnect", () => {
    console.log("Disconnected from WebSocket server");
    statusElement.className = 'alert alert-danger';
    statusElement.textContent = 'Disconnected from server';
});

async function logout() {
    try {
        const response = await fetch('http://localhost:5000/logout', {
            method: 'GET',
            credentials: 'include' 
        });
        
        if (response.ok) {
            localStorage.removeItem('token'); // Remove token from localStorage
            window.location.href = 'login.html';
        }
    } catch (error) {
        console.error('Logout error:', error);
    }
}