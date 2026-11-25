from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()
API_KEY_AEMET = os.getenv("API_KEY_AEMET")

BASE_URL = "https://opendata.aemet.es/opendata/api"
NOMBRE_ESTACION = "MADRID, CIUDAD UNIVERSITARIA"


def consultar_aemet(url):
    """Llama a la API pasando la api_key como query string y descarga los datos del enlace 'datos'."""
    # 1) Primera llamada: la API devuelve un "sobre" con estado, descripción y el enlace "datos".
    res = requests.get(url, params={"api_key": API_KEY_AEMET}, timeout=30)
    res.raise_for_status()
    sobre = res.json()
    if sobre.get("estado") != 200:
        raise RuntimeError(f"AEMET respondió {sobre.get('estado')}: {sobre.get('descripcion')}")

    # 2) Segunda llamada: seguir el enlace "datos" para obtener el contenido real.
    res_datos = requests.get(sobre["datos"], timeout=30)
    res_datos.raise_for_status()
    res_datos.encoding = "ISO-8859-15"  # AEMET sirve los datos en esta codificación
    return res_datos.json()


# Inventario de estaciones: buscar el indicativo (idema) de Ciudad Universitaria.
estaciones = consultar_aemet(
    f"{BASE_URL}/valores/climatologicos/inventarioestaciones/todasestaciones"
)
idema = next(e["indicativo"] for e in estaciones if e["nombre"] == NOMBRE_ESTACION)
print(f"Indicativo de {NOMBRE_ESTACION}: {idema}")


# Climatología diaria de octubre de 2019 en esa estación.
fechaIniStr = "2019-10-01T00:00:00UTC"
fechaFinStr = "2019-10-30T23:59:59UTC"
climatologia = consultar_aemet(
    f"{BASE_URL}/valores/climatologicos/diarios/datos/fechaini/{fechaIniStr}/fechafin/{fechaFinStr}/estacion/{idema}"
)

print(json.dumps(climatologia, indent=4, ensure_ascii=False))
