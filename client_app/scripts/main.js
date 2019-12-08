window.addEventListener("load", function() {
    const loginForm = document.querySelector("form");
});

function login() {
    let request = new XMLHttpRequest();
    request.onreadystatechange = function() {
        if (request.readyState == 4 && request.status == 200) {
            passwordDate = preparePassword(loginForm["password"].value);
        }
    };

    request.open("POST", "127.0.0.1");
    request.send();
}

function register() {
    let request = new XMLHttpRequest();
    request.onreadystatechange = function() {
        if (request.readyState == 4 && request.status == 200) {

        }
    };

    request.open("GET", "127.0.0.1");
    request.send();
}

function preparePassword() {
    
}