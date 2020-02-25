window.addEventListener("load", () => {
    getDevices();
});


function getDevices() {
    createPostHttpRequest("getDevices", `owner=${getCookie("user_id")}`, (obj) => {
        const devices = JSON.parse(obj.responseText);
        buildDevices(devices);
        listenForDevices(devices);
    }, (obj) => {
        console.error("Failed to receive devices.");
    });
}

function buildDevices(devs) {
    for (let device of devs) {
        let deviceNode = document.createElement("div");
        deviceNode.setAttribute("id", device["token"])

        let heading = document.createElement("h3");
        heading.textContent = device["title"];

        let value = document.createElement("p.value");
        value.textContent = "Density: " + device["density"];

        deviceNode.appendChild(heading);
        deviceNode.appendChild(value);
        document.getElementById("wrapper").appendChild(deviceNode);
    }
}

function listenForDevices(devs) {
    for(let device of devs) {
        setInterval(() => { receiveDeviceData(device["token"]) }, 2000);
    }
}

function receiveDeviceData(deviceId) {
    console.log(`Update device(${deviceId})`);
    createPostHttpRequest("receiveData", `device=${deviceId}`, (obj) => {
        let dev = JSON.parse(obj.responseText);
        let parent = document.getElementById(deviceId);
        parent.children[parent.children.length - 1].textContent = "Density: " + dev["density"];
        return;
    }, (obj) => {});
}