import requests
import mariadb

data = []
url = "https://remote-db-sync-function.azurewebsites.net/api/HttpTriggerRemoteSync2?code=lBgE4rXUGD2dQyg8jMFGQ3nxSMxfStlxwUEj_eoRSPxLAzFubC20Ng=="

payload = {
    "remotedatabase": {
        "server": "server-okmc.database.windows.net",
        "username": "user-okmc",
        "password": "abcd123!",
        "database": "bd-okmc",
        "table": "donnees_porte_serre"
    },
    "columns": ["temperature", "pourcentage_ouverture_porte", "distance_porte", "heure"],
    "connectionString": "HostName=internetobjetshub2.azure-devices.net;DeviceId=collecte_info_wafi;SharedAccessKey=+xpoTHfizmfE4EKBwmPIez8FVARoeY/KTlW2Y8fjIWw="
}

headers = {
    "Content-Type": "application/json"
}

cnx = mariadb.connect(
    user="root",
    password="abcd123!",
    host="localhost",
    port=3306,
    database="db_ot"
)

with cnx.cursor() as cursor:
    columns = ', '.join([f"DATE_FORMAT({column}, '%Y-%m-%d %H:%i:%s') as formatted_{column}" if column == 'heure' 
                         else column for column in payload['columns']])
    query = f"SELECT {columns} FROM {payload['remotedatabase']['table']}"
    cursor.execute(query)
    results = cursor.fetchall()

    for result in results:
        data.append(list(result))

cnx.close()

payload['newData'] = data

try:
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Raise exception if response is not successful
    print(f"{response.status_code}: Request successful")
    print(response.content.decode('utf-8'))  # Print response content
except requests.exceptions.HTTPError as e:
    print(f"Request failed with status code {response.status_code}: {response.text}")
    print(e)
except Exception as e:
    print(f"An error occurred: {e}")