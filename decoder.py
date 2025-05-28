from bs4 import BeautifulSoup
from pruebasConectate import Actividades
from pruebasConectate import run
import requests
import asyncio

class DecoderPage():
    """Decoder Page with BeatifulSoup for decoder code from th"""
    def __init__(self, url:str, mode:str):
        self.url = url
        self.mode = mode
        self.soup = None 

    def setUrl(url:str):
        self.url = url

    def setMode(mode:str):
        self.mode = mode

    def fetch_content(self):
        """
        Obtiene el contenido de la página web y lo parsea con BeautifulSoup.
        """
        if not self.url:
            raise ValueError("La URL no ha sido establecida.")
        
        # Hacer una solicitud HTTP y obtener el contenido de la página
        response = requests.get(self.url)
        self.soup = BeautifulSoup(response.content, 'html.parser')
    
    def scrape_by_tag(self, tag:str, tagClass = None):
        """
        Escrapea la página buscando una etiqueta específica.
        
        :param tag: La etiqueta HTML/XML que se desea buscar.
        :return: Una lista de elementos que coinciden con la etiqueta.
        """
        if not self.soup:
            raise ValueError("El contenido no ha sido cargado. Llama a fetch_content() primero.")
        
        if tagClass == None:
            elements = self.soup.find_all(f"{tag}")
        else:
            elements = self.soup.find_all(f"{tag}", {"class":f"{tagClass}"})
        return elements

    def get_actividadesExtracurriculares(self) -> list:
        if self.mode == 'actividades':
            actividades = run()

            return actividades
        else:
            raise ValueError("Modo erroneo")


if __name__ == "__main__":
    decoder = DecoderPage('https://google.com', 'mode')
    decoder.fetch_content()
    code = decoder.scrape_by_tag('span')
    for line in code:
        print(line)

