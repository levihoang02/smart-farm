
let audio = null;

const playAlertSound = () => {
    if (audio) {
        audio.pause(); // Stop any currently playing sound
        audio.currentTime = 0; // Reset playback to the start
    }
    audio = new Audio('../utils/alert.wav'); // Replace with your audio file
    audio.play();
};

const stopAlertSound = () => {
    if (audio) {
        audio.pause(); // Stop the sound
        audio.currentTime = 0; // Reset to the start
    }
};

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
        playAlertSound();
    } else {
        card.classList.remove('alert-threshold');
        // stopAlertSound();
    }
}

socket.on("sensor_data", (res) => {
    try {
        console.log("Received Kafka message:", res);
        checkThresholds(res.data["Temperature"], res.data["Humidity"]);
        let TEMP_ALERT_THRESHOLD = localStorage.getItem('temperature');
        let HUMIDITY_ALERT_THRESHOLD = localStorage.getItem('humidity')
        // Update temperature value
        const tempElement = document.getElementById('temperature');
        const humidityElement = document.getElementById('humidity');
        if (tempElement && humidityElement) {
            const temp = res.data["Temperature"];
            const humidity = res.data["Humidity"];
            checkThreshold('temperature', temp, TEMP_ALERT_THRESHOLD);
            checkThreshold('humidity', humidity, HUMIDITY_ALERT_THRESHOLD);
            }
        } catch(err) {
            console.error(err);
        }});

function checkThresholds(temperature, humidity) {
    console.log("Checking...")
    let TEMP_ALERT_THRESHOLD = localStorage.getItem('temperature');
    let HUMIDITY_ALERT_THRESHOLD = localStorage.getItem('humidity');
    if(temperature > TEMP_ALERT_THRESHOLD || humidity > HUMIDITY_ALERT_THRESHOLD) {
        playAlertSound();
    }
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

function downloadCSV(date, temp, humid) {
    // Create CSV header
    let csvContent = "TIME,T2M,QV2M\n";
    
    // Create timestamps with 1-hour gaps
    const startDate = new Date(date); // Assuming 'date' is your start date
    const timestamps = [];
    
    // Generate timestamps for each data point
    for (let i = 0; i < temp.length; i++) {
        const currentDate = new Date(startDate);
        currentDate.setHours(startDate.getHours() + i); // Add i hours to start date
        timestamps.push(currentDate);
    }
    
    // Combine timestamps with temperature and humidity data
    for (let i = 0; i < temp.length; i++) {
        const date = timestamps[i];
        const row = [
            `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:00`,  // YYYY-MM-DD HH:00
            temp[i],    // T2M
            humid[i]    // QV2M
        ].join(',');
        csvContent += row + "\n";
    }

    // Create blob and download link
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    
    // Create object URL
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", `sensor_data_${new Date().toISOString()}.csv`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

async function download(date) {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('http://localhost:5000/data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            credentials: 'include', 
            body: JSON.stringify({ date })
        });
        
        if (!response.ok) {
            throw new Error('Request failed');
        }

        const data = await response.json();
        downloadCSV(date, data.temp, data.humid);
    } catch (error) {
        console.error('Download error:', error);
    }
};

document.getElementById('download-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const date = document.getElementById('date').value;

    await download(date);
});