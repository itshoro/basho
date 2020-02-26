let queryDensityDataTime = 2000; // 2 Seconds
let queryDevicesDelta = 15000; // 5 Seconds

window.addEventListener("load", () => {
    setInterval(() => {
        getDevices();
    }, queryDevicesDelta)
    getDevices();
});


let devices;
function getDevices() {
    createPostHttpRequest("getDevices", `owner=${getCookie("user_id")}`, (obj) => {
        if (showsError)
            removeError();
            
        let newDevices = JSON.parse(obj.responseText);

        if (devices) {
            let filtered = newDevices.filter(val => val in devices.map(dev => dev["token"]));
            buildDevices(filtered);
        }
        else {
            buildDevices(newDevices);
        }

        devices = newDevices;
        listenForDevices(devices);
    }, (obj) => {
        createError("Database is unreachable. Retrying..")

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

        deviceNode.appendChild(heading);
        deviceNode.appendChild(value);
        document.getElementById("wrapper").appendChild(deviceNode);
    }
}

function readableDate(date) {
    var delta = Math.round((new Date() - Date.parse(date)) / 1000);
    
    var minute = 60,
        hour = minute * 60,
        day = hour * 24,
        week = day * 7;

    let fuzzy;
    
    if (delta < 30) {
        fuzzy = 'just then.';
    } else if (delta < minute) {
        fuzzy = delta + ' seconds ago.';
    } else if (delta < 2 * minute) {
        fuzzy = 'a minute ago.'
    } else if (delta < hour) {
        fuzzy = Math.floor(delta / minute) + ' minutes ago.';
    } else if (Math.floor(delta / hour) == 1) {
        fuzzy = '1 hour ago.'
    } else if (delta < day) {
        fuzzy = Math.floor(delta / hour) + ' hours ago.';
    } else if (delta < day * 2) {
        fuzzy = 'yesterday';
    }
    return fuzzy;
}

let intervals = [];
function listenForDevices(devs) {
    // Clear intervals
    while(intervals.length > 0) {
        let i = intervals.pop()
        console.log("(Info) Clearing interval with id " + i);
        window.clearInterval(i);
    }

    for(let device of devs) {
        // console.log(`${device["title"]}(${device["token"]}) active: ${device["active"]}`);

        if (device["active"]) {
            console.log("(Info) Adding interval for " + device["title"]);
            intervals.push(setInterval(() => { receiveDeviceData(device["token"], device["title"]) }, queryDensityDataTime));
        }
        else {
            displayAsInactive(device);
        }
    }
}

function displayAsInactive(device) {
    let parent = document.getElementById(device["token"]);
    parent.children[0].textContent = `${device["title"]} (!) - Inactive since ${readableDate(device["timestamp"])}`;
    parent.children[0].style.color = "red";
    parent.children[parent.children.length - 1].textContent = `Density: ${device["density"]}`;

}

function receiveDeviceData(deviceId, title) {
    // console.log(`Update device(${deviceId})`);
    createPostHttpRequest("receiveData", `device=${deviceId}`, (obj) => {
        let dev = JSON.parse(obj.responseText);
        let parent = document.getElementById(deviceId);
        parent.children[0].textContent = `${title}`;
        parent.children[0].style.color = "black";
        parent.children[parent.children.length - 1].textContent = "Density: " + dev["density"];

        return;
    }, (obj) => {});
}