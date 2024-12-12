// Initialize Charts
const temperatureCtx = document.getElementById('temperatureChart').getContext('2d');
const humidityCtx = document.getElementById('humidityChart').getContext('2d');
const TEMP_ALERT_THRESHOLD = 20;
const HUMIDITY_ALERT_THRESHOLD = 30;

function checkThresholds(temperature, humidity) {
    let alertMessage = '';
    
    if (temperature > TEMP_ALERT_THRESHOLD) {
        alertMessage += `Temperature (${temperature}°C) is above threshold of ${TEMP_ALERT_THRESHOLD}°C!\n`;
    }
    
    if (humidity > HUMIDITY_ALERT_THRESHOLD) {
        alertMessage += `Humidity (${humidity}) is above threshold of ${HUMIDITY_ALERT_THRESHOLD}!`;
    }
    
    if (alertMessage) {
        const existingModal = bootstrap.Modal.getInstance(document.getElementById('alertModal'));
        if (existingModal) {
            existingModal.hide();
        }
        document.getElementById('alertModalBody').textContent = alertMessage;
        const alertModal = new bootstrap.Modal(document.getElementById('alertModal'));
        alertModal.show();
    }
}

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

const socket = io("http://localhost:5000");
const statusElement = document.getElementById('connection-status');

socket.on("connect", () => {
    console.log("Connected to WebSocket server");
    statusElement.className = 'alert alert-success';
    statusElement.textContent = 'Connected to server';
});

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

socket.on("disconnect", () => {
    console.log("Disconnected from WebSocket server");
    statusElement.className = 'alert alert-danger';
    statusElement.textContent = 'Disconnected from server';
});

socket.on("test", (data) => {
  console.log("Test message received:", data);
});
