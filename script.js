// ===================== Variables =====================
const get_post_url = "https://post-get-function.azurewebsites.net/api/HttpTriggerPostGet?code=LE986-5gmHqILUL_p-DQ1SXhbDatNS_E5Pp-QPj5YtYGAzFuVc0AHw==";
const seconds = 1;

const outputTemperature = document.getElementById('output-temperature');
const outputDistance = document.getElementById('output-distance');
const outputDoorPct = document.getElementById('output-door-pct');
const inputPct = document.getElementById('input-pourcentage');
const progressBar = document.getElementById('progress-bar');
const outputAlert = document.getElementById('ouput-alert');
// ===================== Variables =====================


// ===================== Interface =====================
function updateInterface() {
    setInterval(() => {
        fetch(get_post_url)
            .then(response => {
                if (response.status !== 200) {
                    throw new Error(`Error: Received status code ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data && Object.keys(data).length > 0) {
                    outputTemperature.textContent = data.temperature;
                    if (data.distance_porte !== null) {
                        outputDistance.textContent = data.distance_porte.toFixed(2);
                    }

                    outputDoorPct.textContent = data.pourcentage_ouverture_porte;
                    progressBar.style.height = data.pourcentage_ouverture_porte + '%';

                    outputAlert.textContent = data.alert;
                }
            })
            .catch(error => {
                console.error(error);
            });
    }, seconds * 1000);
}

updateInterface();
// ===================== Interface =====================


// ===================== Open - Close =====================
function action_post(is_open_action) {
    // Check if is_open_action is defined
    if (typeof is_open_action === 'undefined') {
        console.error('Error: is_open_action is not defined');
        return;
    }

    // Check if inputPct.value is valid
    let inputValue = Number(inputPct.value);
    if (!inputValue || inputValue <= 0) {
        console.error('Error: Invalid input percentage value');
        return;
    }

    let postData = {
        is_open: is_open_action,
        pourcentage_input: inputPct.value
    };

    fetch(get_post_url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'origin': 'http://127.0.0.1:5500' // replace this with the correct origin
        },
        body: JSON.stringify(postData)
    })
        .then(response => {
            if (response.status !== 200) {
                throw new Error(`Error: Received status code ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Handle response data here
            console.log(data);
        })
        .catch(error => {
            console.error(error);
        });
}
// ===================== Open - Close =====================


// ===================== Input =====================
function percentageFilter(e) {
    let value = e.target.value;

    if (value < 0 || value > 100) {
        e.target.value = '';
    } else if (!Number.isInteger(Number(value))) {
        e.target.value = '';
    }
}

inputPct.addEventListener('input', percentageFilter);
// ===================== Input =====================