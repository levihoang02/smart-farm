// Initialize Charts
const temperatureCtx = document.getElementById('temperatureChart').getContext('2d');
const metricsCtx = document.getElementById('metricsChart').getContext('2d');

// Temperature Line Chart
const temperatureChart = new Chart(temperatureCtx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Temperature °C',
            data: [],
            borderColor: 'rgb(75, 192, 192)',
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
const metricsChart = new Chart(metricsCtx, {
    type: 'doughnut',
    data: {
        labels: ['Temperature', 'Humidity'],
        datasets: [{
            data: [0, 0, 0],
            backgroundColor: [
                'rgb(255, 99, 132)',
                'rgb(54, 162, 235)',
                'rgb(255, 205, 86)'
            ]
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        circumference: 180,
        rotation: -90,
        plugins: {
            legend: {
                position: 'bottom'
            }
        }
    }
});

// Keep track of time series data
const maxDataPoints = 20;
const timeSeriesData = [];

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
        
        // Update temperature value
        const tempElement = document.getElementById('temperature');
        if (tempElement && res.data["Temperature"]) {
            const temp = res.data["Temperature"];
            tempElement.textContent = temp.toFixed(1);

            // Update temperature chart
            const timestamp = new Date().toLocaleTimeString();
            timeSeriesData.push({ time: timestamp, temp: temp });
            
            // Keep only last maxDataPoints
            if (timeSeriesData.length > maxDataPoints) {
                timeSeriesData.shift();
            }

            temperatureChart.data.labels = timeSeriesData.map(data => data.time);
            temperatureChart.data.datasets[0].data = timeSeriesData.map(data => data.temp);
            temperatureChart.update();

            // Update metrics chart
            metricsChart.data.datasets[0].data = [
                temp,
                res.data["Humidity"] || 0,
                res.data["Pressure"] || 0
            ];
            metricsChart.update();
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
