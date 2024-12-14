

async function login(username, password) {
    try {
        const response = await fetch('http://localhost:5000/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include', 
            body: JSON.stringify({ username, password })
        });
        
        if (!response.ok) {
            throw new Error('Login failed');
        }

        const data = await response.json();
        if(data.token) {
            localStorage.setItem('token', data.token);
            window.location.href = 'dashboard.html';
        }
    } catch (error) {
        console.error('Login error:', error);
    }
};

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('errorMessage');

    await login(username, password);
}); 