// ===================== Variables =====================
let chart = null;
let fetchedData = [];

// Define the url and payload
const url = "https://database-data-function.azurewebsites.net/api/HttpTriggerDatabaseData?code=v6sTtPNIQ0Hy5_x8jJEwe8OwlKnj7JP0Dv-7sdNp_u7YAzFuIx7j0Q==";

const payload = {
    remotedatabase: {
        server: "server-okmc.database.windows.net",
        username: "user-okmc",
        password: "abcd123!",
        database: "bd-okmc",
        table: "mesures",
    },
    columns: ["temperature", "pourcentage_ouverture_porte", "distance_porte", "heure"],
    connectionString: "HostName=internetobjetshub2.azure-devices.net;DeviceId=collecte_temp;SharedAccessKey=p2vT0Ua6gFOWxkw/LemxakFo3j4bhblm1w8/ppxBBQQ=",
};

let yearDate;
let startDate;
let endDate;
let alertElement = document.getElementById('alert');
// ===================== Variables =====================

// ===================== Fetch Data =====================
async function fetchData() {
    try {
        let alertIcon = document.getElementById('alertIcon');

        // Get the values here to reflect any changes made after the script has been loaded
        yearDate = document.getElementById('year').value;
        startDate = document.getElementById('startDate').value;
        endDate = document.getElementById('endDate').value;

        alertElement.innerText = "Récupération des données...";
        alertElement.style.color = '#007bff';
        alertIcon.className = 'loader';

        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.error) {
            alertElement.innerText = "Une erreur s'est produite lors de la récupération des données.";
            alertElement.style.color = 'red';
            alertIcon.className = 'fas fa-times-circle'; // display error icon
            return;
        }

        fetchedData = data;
        alertElement.innerText = "Les données ont été récupérées avec succès.";
        alertElement.style.color = 'green';
        alertIcon.className = 'fas fa-check-circle'; // display success icon

    } catch (error) {
        alertElement.innerText = "Une erreur s'est produite lors de la récupération des données.";
        alertElement.style.color = 'red';
        alertIcon.className = 'fas fa-times-circle'; // display error icon
    }
}
// ===================== Fetch Data =====================

// ===================== Process Data =====================
function processData() {
    if (!fetchedData || fetchedData.length == 0) {
        alertElement.innerText = "Les données récupérées sont vides.";
        alertElement.style.color = 'red';
        alertIcon.className = 'fas fa-times-circle'; // display error icon
        return;
    }

    yearDate = document.getElementById('year').value;
    startDate = document.getElementById('startDate').value;
    endDate = document.getElementById('endDate').value;

    let filteredData;
    let displayFormat = 'YYYY-MM-DD';

    // If only year is provided
    if (yearDate && !startDate && !endDate) {
        const startOfYear = moment(`${yearDate}-01-01`).format('YYYY-MM-DD');
        const endOfYear = moment(`${yearDate}-12-31`).format('YYYY-MM-DD');
        
        filteredData = fetchedData.filter(item => {
            const itemDate = moment(item[3]).format('YYYY-MM-DD');
            return moment(itemDate).isSameOrAfter(startOfYear) && moment(itemDate).isSameOrBefore(endOfYear);
        });    

    } 
    // If start and end dates are provided
    else if (!yearDate && startDate && endDate) {
        const formattedStartDate = moment(startDate).format('YYYY-MM-DD');
        const formattedEndDate = moment(endDate).format('YYYY-MM-DD');
        
        filteredData = fetchedData.filter(item => {
            const itemDate = moment(item[3]).format('YYYY-MM-DD');
            return moment(itemDate).isSameOrAfter(formattedStartDate) && moment(itemDate).isSameOrBefore(formattedEndDate);
        }); 

    } else {
        alertElement.innerText = "Veuillez fournir une année ou une date de départ et de fin.";
        alertElement.style.color = 'red';
        alertIcon.className = 'fas fa-times-circle'; // display error icon
        return;
    }

    if (filteredData.length == 0) {
        alertElement.innerText = "Aucune donnée n'est disponible pour les dates sélectionnées.";
        alertElement.style.color = 'red';
        alertIcon.className = 'fas fa-times-circle'; // display error icon
        return;
    }

    // Group the data by date and get the max value for each group
    let groupedData = {};
    filteredData.forEach(item => {
        const date = moment(item[3]).format(displayFormat);
        if (!groupedData[date]) {
            groupedData[date] = item;
        } else {
            groupedData[date] = groupedData[date].map((value, index) => {
                return index < 3 && value < item[index] ? item[index] : value;
            });
        }
    });

    const labels = Object.keys(groupedData).sort();
    const temperatureData = labels.map(label => groupedData[label][0]);
    const pourcentageData = labels.map(label => groupedData[label][1]);
    const distanceData = labels.map(label => groupedData[label][2]);

    const chartData = {
        labels: labels,
        datasets: [
            {
                label: "Temperature",
                data: temperatureData,
                backgroundColor: "rgba(0, 123, 255, 0.5)",
                borderColor: "rgba(0, 123, 255, 1)",
                borderWidth: 1,
                tension: 0.4,  // Smooth curve
                pointRadius: 0
            },
            {
                label: "Pourcentage",
                data: pourcentageData,
                backgroundColor: "rgba(255, 0, 0, 0.5)",
                borderColor: "rgba(255, 0, 0, 1)",
                borderWidth: 1,
                tension: 0.4, // Smooth curve
                pointRadius: 0
            },
            {
                label: "Distance",
                data: distanceData,
                backgroundColor: "rgba(0, 255, 0, 0.5)",
                borderColor: "rgba(0, 255, 0, 1)",
                borderWidth: 1,
                tension: 0.4, // Smooth curve
                pointRadius: 0
            },
        ],
    };

    const ctx = document.getElementById("myChart").getContext("2d");
    if (chart !== null) {
        chart.destroy();
    }
    chart = new Chart(ctx, {
        type: "line",
        data: chartData,
        options: {
            responsive: true,
            scales: {
                x: {
                    type: "time",
                    time: {
                        parser: "YYYY-MM-DD",
                        tooltipFormat: "YYYY-MM-DD",
                        unit: "day",
                        displayFormats: {
                            day: displayFormat,
                        },
                    },
                },
                y: {
                    beginAtZero: true,
                    suggestedMax: 100,
                },
            },
        },
    });

    alertElement.innerText = "Les données ont été mises à jour avec succès.";
    alertElement.style.color = 'green';
    alertIcon.className = 'fas fa-check-circle'; // display success icon

}
// ===================== Process Data =====================

function clearDates(){
    startDate = document.getElementById('startDate').value = '';
    endDate = document.getElementById('endDate').value = '';
}