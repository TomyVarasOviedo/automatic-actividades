import time
import json
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime


class Actividades:
    def __init__(self, id, nombre, fecha, cupos, link, credito):
        self.id = id
        self.nombre = nombre
        self.fecha = fecha
        self.cupos = cupos
        self.link = link
        self.credito = credito

    def __str__(self):
        return f"""<div>
                    <h2>ID:{self.id}: {self.nombre}</h2>
                    <ul>
                        <li><strong>Fecha:</strong> {self.fecha}</li>
                        <li><strong>Cupos:</strong> {self.cupos}</li>
                        <li><strong>Creditos:</strong> {self.credito} Creditos</li>
                        <li><strong>Link:</strong> <a href="{self.link}"> {self.link}</a></li>
                    </ul>
                </div>"""


def inciar_sesion() -> dict:
    # Configurar sesión persistente
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "refer": "https://conectate.ub.edu.ar/UB/ActividadesExtracurriculares/InscripcionActividadesExtracurriculares.aspx",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    # 1. Obtener página de login y extraer campos ocultos
    login_url = "https://conectate.ub.edu.ar/Login.aspx?ReturnUrl=%2fUB%2fActividadesExtracurriculares%2fInscripcionActividadesExtracurriculares.aspx"
    response = session.get(login_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extraer campos obligatorios de .NET
    viewstate = soup.find("input", {"id": "__VIEWSTATE"})["value"]
    event_validation = soup.find("input", {"id": "__EVENTVALIDATION"})["value"]
    viewstate_generator = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})["value"]

    # 2. Datos del formulario (reemplaza con tus credenciales)
    payload = {
        "__VIEWSTATE": viewstate,
        "__EVENTVALIDATION": event_validation,
        "__VIEWSTATEGENERATOR": viewstate_generator,
        "__EVENTTARGET": "",  # Campo adicional requerido
        "__EVENTARGUMENT": "",
        "ctl00$mainContent$lvLoginUser$ucLoginUser$lcLoginUser$UserName": "tomas.varas",  # Campo de usuario
        "ctl00$mainContent$lvLoginUser$ucLoginUser$lcLoginUser$Password": "*UB030623",  # Campo de contraseña
        "ctl00$mainContent$lvLoginUser$ucLoginUser$lcLoginUser$LoginButton": "Ingresar",  # Botón de submit
    }

    # 3. Enviar POST de autenticación
    response_post = session.post(
        login_url,
        data=payload,
        headers=headers,
        allow_redirects=True,  # Importante para seguir redirecciones
    )
    # 4. Verificar si el login fue exitoso
    if "InscripcionActividadesExtracurriculares.aspx" in response_post.url:
        print("¡Login exitoso! ✅")

        api_url = "https://conectate.ub.edu.ar/UB/ActividadesExtracurriculares/InscripcionActividadesExtracurriculares.aspx/ListarActividadesExtracurriculares"
        headersAPI = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Origin": "https://conectate.ub.edu.ar",
            "Content-Type": "application/json",
            "Referer": "https://conectate.ub.edu.ar/UB/ActividadesExtracurriculares/InscripcionActividadesExtracurriculares.aspx",
            "X-Requested-With": "XMLHttpRequest",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "sec-Ch-Ua-Platform": "Linux",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Content-Length": "31",
        }
        payload = {"People_Code_Id": "P000179046"}

        response = session.post(api_url, headers=headersAPI, json=payload)
        if response.status_code == 200:
            datos = response.text
            # datos = datos.replace("/", "")
            # datos = datos.replace("\\", "")
            datos = json.loads(datos)
            datos = json.loads(datos["d"])
            return datos
        else:
            print(
                f"Error al obtener la respuesta: {response.status_code} -> {response.text}"
            )

    else:
        print("Error de autenticación ❌")
        print("Posibles causas: Credenciales incorrectas o cambios en el formulario")


def indentificar_actividades(data: list) -> list:
    actividades = []
    if len(data) <= 0:
        print("No se encontraron actividades")
        exit
    for actividad in data:
        fecha = re.split(r"[(,)]+", actividad["Fecha"])[1]
        fecha = datetime.fromtimestamp(int(fecha[:-3])).strftime("%d/%m/%Y %H:%M:%S")
        if actividad["CupoDisponible"] == 0:
            continue
        if (
            actividad["HabilitadoInscripcion"] == False
            or actividad["Cancelado"]
            or actividad["Cerrada"]
        ):
            continue
        actividades.append(
            Actividades(
                actividad["Id"],
                actividad["Nombre"],
                fecha,
                actividad["CupoDisponible"],
                actividad["Lugar"],
                actividad["Credito"],
            )
        )
    actividades.sort(key=lambda x: x.fecha)

    return actividades


def run():
    data = inciar_sesion()["ActividadesExtracurriculares"]
    return indentificar_actividades(data)


if __name__ == "__main__":
    print(run())
