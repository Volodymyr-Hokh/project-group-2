async function sendJWT(url, token) {

    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + token,
        }
    });

    document.body.innerHTML = await response.text();
}

window.onload = function () {
    const token = localStorage.getItem('token');
    sendJWT(location.href, token);
}
