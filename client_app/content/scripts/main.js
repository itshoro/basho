window.addEventListener("load", function() {
    const registerForm = this.document.querySelectorAll("form")[1];
});

function toggleRegisterForm() {
    const loginForm = document.querySelectorAll("form")[0].classList.toggle("hide");
    const registerForm = this.document.querySelectorAll("form")[1].classList.toggle("hide");
}

function login() {
    const loginForm = document.querySelectorAll("form")[0];

    let email = loginForm["email"].value;
    let password = loginForm["password"].value;
    let request = new XMLHttpRequest();
    request.open("POST", "/login", true);
    request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    request.onreadystatechange = function() {
        if (request.readyState == 4 && request.status == 200) {
            alert("I think you just logged in.")
        }
        else if (request.readyState == 4 && request.status >= 400) {
            createError("Your username or password is wrong.");
        }
    }
    request.send(`email=${email}&password=${password}`);
}

function register() {
    const registerForm = document.querySelectorAll("form")[1];

    let email = registerForm["email"].value;
    let password = registerForm["password"].value;

    if (password !== registerForm["passwordSafety"].value) {
        createError("Passwords don't match!");
        return;
    }

    let request = new XMLHttpRequest();
    request.open("POST", "/register", true);
    request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    request.onreadystatechange = function() {
        if (request.readyState == 4 && request.status == 200) {
            window.location.reload();
        }
        else if (request.readyState == 4 && request.status >= 400) {
            createError("A user with that name already exists.");
        }
    }
    request.send(`email=${email}&password=${password}`);
}


let showsError = false;
let error;
function createError(msg) {
    if (showsError) {
        error = document.querySelector("div.error");
        error.children[0].innerText = msg;

        return;
    }
    error = document.createElement("DIV");
    error.classList.add("error");

    let errorMsg = document.createElement("P");
    errorMsg.innerText = msg;
    error.appendChild(errorMsg);

    let closeSpan = document.createElement("SPAN");
    closeSpan.appendChild(document.createElement("SPAN"));
    closeSpan.appendChild(document.createElement("SPAN"));
    closeSpan.addEventListener("click", removeError);
    error.appendChild(closeSpan);

    let wrapper = document.querySelector(".login:not(.hide)")
    wrapper.insertBefore(error, wrapper.children[1]);
    showsError = true;
}

function removeError(){
    error.remove();
    showsError = false;
}