from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()
API_KEY_AEMET = os.getenv("API_KEY_AEMET")



res = requests.get(
    url = 'https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones',
    headers = {
        "api_key": API_KEY_AEMET
    }
)


idema = "3194U"
fechaIniStr = "2019-10-01T00:00:00UTC"
fechaFinStr = "2019-10-30T23:59:59UTC"
res = requests.get(
    url = f'https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{fechaIniStr}/fechafin/{fechaFinStr}/estacion/{idema}',
    headers = {
        "api_key": API_KEY_AEMET
    }
)  

print(json.dumps(res.json(), indent=4))