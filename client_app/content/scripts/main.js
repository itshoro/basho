window.addEventListener("load", function() {
    const registerForm = this.document.querySelectorAll("form")[1];
    formParent = document.getElementsByClassName("login_wrapper")[0];
});

function login() {
    const loginForm = document.querySelectorAll("form")[0];

    let email = loginForm["email"].value;
    let password = loginForm["password"].value;

    createPostHttpRequest("/login", `email=${email}&password=${password}`,
        () => {
            window.location.reload();
        }, 
        (obj) => {
            if (obj.status === 500) {
                createError("It seems, that we can't reach our authentication servers.\nPlease try again later.");
                return;
            }
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
    const registerForm = document.querySelectorAll("form")[0];

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
        if (obj.status === 500) {
            createError("It seems, that we can't reach our authentication servers.\nPlease try again later.");
            return;
        }
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

    let wrapper = document.querySelector(".login:not(.hide)") || document.body;
    wrapper.insertBefore(error, wrapper.children[1]);
    showsError = true;
}

function removeError(){
    if (showsError) {
        error.remove();
    }
    showsError = false;
}

let formParent;
let formState = 0;
function toggleForm() {
    removeError();
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

function createDeviceDataNode(deviceName, value, error = false) {
    let container = document.createElement("p");
    container.textContent = `Device ${deviceName}: ${value}`;

    if (error) {
        container.textContent = `Device currently unavailable.`;
        container.style.color = "red";
    }
    return container;
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
        c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
        }
    }
    return "";
}