import json
import requests

# Define the payload
payload = {
    "remotedatabase": {
        "server": "server-okmc.database.windows.net",
        "username": "user-okmc",
        "password": "abcd123!",
        "database": "bd-okmc",
        "table": "mesures"
    },
    "columns": ["temperature", "pourcentage_ouverture_porte", "distance_porte", "heure"],
    "connectionString": "HostName=internetobjetshub2.azure-devices.net;DeviceId=collecte_temp;SharedAccessKey=p2vT0Ua6gFOWxkw/LemxakFo3j4bhblm1w8/ppxBBQQ="
}

# Define the URL
url = "https://database-data-function.azurewebsites.net/api/HttpTriggerDatabaseData?code=v6sTtPNIQ0Hy5_x8jJEwe8OwlKnj7JP0Dv-7sdNp_u7YAzFuIx7j0Q=="

# Make the POST request and get the response
response = requests.post(url, json=payload)

# Check the status code
if response.status_code == 200:
    # If the request was successful, print the data
    print(response.json())
else:
    # If the request failed, print the status code
    print(f"Request failed with status code {response.status_code}")
