import argparse
import time 
import json 
import datetime 
import threading
from fastapi import FastAPI, HTTPException
import uvicorn
import csv 
from decoder import DecoderPage
from mail import Mail
from requestsApi import UpdateUrlRequest

TIME_REFRESH = 10
app = FastAPI()

data = {
    "url":"https://www.mercadolibre.com.ar/consola-portatil-steam-deck-oled-512gb-valve-color-negro/p/MLA36688277#polycard_client=search-nordic&searchVariation=MLA36688277&wid=MLA1894736448&position=2&search_layout=stack&type=product&tracking_id=51673604-68b5-4600-9b04-c8046230677d&sid=search",
    "mode":"mercado",
    "running":True,
}

data_lock = threading.Lock()

def actividades_extracuriculares():
    mail = Mail("Actividades Extracuriculares de la semana", "tomas.varas@comunidad.ub.edu.ar")
    #while True:
    with data_lock:
        if not data["running"]:
            exit
        try:
            decoder = DecoderPage('', 'actividades')
            #time.sleep(TIME_REFRESH*17280)
            actividades = decoder.get_actividadesExtracurriculares()
            mensaje = """
                        <header style="width: 100%;border: 2px solid #5bb3cf;background-color: #333; color: white; padding: 0px; text-align: center;">
                            <div class="container">
                                <h1>Actividades Extracurriculares disponibles</h1>
                            </div>
                        </header> 
                    """
            if len(actividades) > 0:
                for actividad in actividades:
                    mensaje += f"{actividad}\n"
            else:
                mensaje += """
                        <hr>
                        <div class="container">
                            <h2>No hay actividades extracurriculares disponibles en este momento.</h2>
                        </div>
                        <hr>
                    """

            mensaje += """
                        <footer style="width: 100%;border: 2px solid #5bb3cf;background-color: #333; color: white; padding: 0px; text-align: center;">
                            <div class="container">
                                <p>© 2023 Tomas Varas. All rights reserved.</p>
                            </div> 
                        </footer>
                      """

            mail.set_mensaje(mensaje)
            mail.mensaje_automatico()

        except Exception as e:
            print(f"ERROR => {e}") 

def scrapper_worker():
    mail = Mail("Steam Deck mercado libre", "tomasvarasoviedo@gmail.com")
    while True:
        with data_lock:
            if not data["running"]:
                break
            url = data["url"]
            try:
                print(url)
                decoder = DecoderPage(url, data["mode"]) 
                decoder.fetch_content()
                elements = decoder.scrape_by_tag("span", "andes-money-amount__fraction")
                precio = elements[0].text
                precio = precio.replace(".","")
                with open('registro.csv', 'a') as c:
                    csvwrite = csv.writer(c)
                    csvwrite.writerows([[datetime.datetime.now(), float(precio)]])

                if float(precio) < 800000:
                    mail.set_mensaje(f"Actualmente el producto se encuentra en un valor: {elements[0].text}")
                    mail.mensaje_automatico()
            except Exception as e:
                print(f"Error en {url} ==> {e}")
        time.sleep(TIME_REFRESH)

#scraper_thread = threading.Thread(target=scrapper_worker)
#scraper_thread.daemon = True
#scraper_thread.start()


#ENDPOINTS
@app.get("/status")
def get_scrapper_status():
    with data_lock:
        return {
            "url": data["url"],
            "modo": data["mode"],
            "status" : "Corriendo..." if data["running"] else "Error"
        }
@app.post("/update/scrapper")
def updateUrlScrapper(request: UpdateUrlRequest):
    with data_lock:
            data["url"] = request.url
    return {"message": f"Url actualizada => {request.url}"}

@app.post("/stop")
def stopScrapper():
    with data_lock:
        data["running"] = False 
    return {"message": "Scrapper detenido"}

@app.post("/start")
def startScrapper():
    with data_lock:
        data["running"] = True
    return {"message":"Scrapper Encendido"}

@app.get("/statistics")
def verCSVEstadisticas():
    data = {}
    with open('registro.csv', encoding="utf-8") as c:
        reader = csv.DictReader(c)
        for row in reader:
            data[row['fecha']] = row['precio']

    return json.dumps(data)

if __name__ == "__main__":
    actividades_thread = threading.Thread(target=actividades_extracuriculares)
    actividades_thread.daemon = True
    actividades_thread.start() 

