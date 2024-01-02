document.getElementById('loginForm').addEventListener('submit', function (event) {
    event.preventDefault();

    const formData = new FormData(event.target);

    fetch('/api/auth/login', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            console.log(data.json);
            const jwtToken = data.access_token;
            localStorage.setItem('token', jwtToken);
            window.location.href = '/';

        })
        .catch(error => {
            console.error('Error:', error);
        });
});