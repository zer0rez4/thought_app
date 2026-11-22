const API_URL = 'http://127.0.0.1:8000';


function getAuthHeaders() {
    const token = localStorage.getItem('access_token');

    const headers = {
        'Content-Type': 'application/json'
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
}


async function registerUser(name, email, password) {
    const response = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            email: email,
            password: password,
            name: name
        })
    });

    return response;
}

async function resendEmailVerification(email) {
    const response = await fetch(`${API_URL}/auth/resend-verification`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            email: email
        })
    });

    if (!response.ok) {
        const responseData = await response.json();
        const error = new Error(responseData.detail || 'Registration failed');
        error.status = response.status;
        throw error;
    }

    return response;
}

async function loginUser(email, password) {
    const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            email: email,
            password: password
        })
    });
    
    return response;
}

export { 
    registerUser, resendEmailVerification,
    loginUser 
 }; 