function register() {
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;

    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email, password }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert('Registration successful. Please log in.');
            window.location.href = '/login';
        }
    })
    .catch(error => console.error('Error:', error));
}

function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            window.location.href = data.redirect;
        }
    })
    .catch(error => console.error('Error:', error));
}

function logout() {
    fetch('/logout')
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        window.location.href = '/';
    })
    .catch(error => console.error('Error:', error));
}
