window.addEventListener("load", function() {
    const registerForm = this.document.querySelectorAll("form")[1];
    formParent = document.getElementsByClassName("login_wrapper")[0];
});

function toggleRegisterForm() {
    const loginForm = document.querySelectorAll("form")[0].classList.toggle("hide");
    const registerForm = this.document.querySelectorAll("form")[1].classList.toggle("hide");
}

function login() {
    const loginForm = document.querySelectorAll("form")[0];

    let email = loginForm["email"].value;
    let password = loginForm["password"].value;

    createPostHttpRequest("/login", `email=${email}&password=${password}`,
        () => {
            window.location.reload();
        }, 
        (obj) => {
            createError(obj.responseText);
    });
}

function createPostHttpRequest(url, urlEncodedParameters, onSuccessCallback, onErrorCallback) {
    let request = new XMLHttpRequest();
    request.open("POST", url, true);
    request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

    request.onreadystatechange = function() {
        if (request.readyState == 4 && request.status == 200) {
            onSuccessCallback(request);
        }
        else if (request.readyState >= 3 && request.status >= 400) {
            onErrorCallback(request);
        }
    }

    request.send(urlEncodedParameters);
}

function register() {
    const registerForm = document.querySelectorAll("form")[1];

    let email = registerForm["email"].value;
    let password = registerForm["password"].value;

    if (password !== registerForm["passwordSafety"].value) {
        createError("Passwords don't match!");
        return;
    }

    createPostHttpRequest("/register", `email=${email}&password=${password}`,
    () => {
        window.location.reload();
    }, 
    (obj) => {
        createError(obj.responseText);
    });
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

let formParent;
let formState = 0;
function toggleForm() {
    for (child of formParent.children) {
        child.remove()
    }
    formState = (formState + 1) % 2;
    createPostHttpRequest("/toggleForm", `formState=${formState}`, (obj) => {
        formParent.insertAdjacentHTML("afterbegin", obj.responseText);
    }, (obj) => {
        console.log(obj.responseText);
    })
}