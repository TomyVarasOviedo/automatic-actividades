import yagmail
import json

config = ""
with open('config.json') as j:
    config = json.load(j)



class Mail():
    """Clase para enviar mails a un destinatario
    :param mensaje -> String
    :param asunto -> String
    :param destinatario -> String"""
    def __init__(self, mensaje:str, asunto:str, destinatario:str): 
        self.mensaje = mensaje 
        self.asunto = asunto
        self.destinatario = destinatario
    
    """Clase para construir mail sin mensaje fijado
    :param asunto -> String
    :param destinatario -> String
    """
    def __init__(self, asunto:str, destinatario):
        self.asunto = asunto
        self.destinatario = destinatario

    def set_params(self,mensaje:str,asunto:str,destinatario):
        """
        Metodo para actualizar los parametros de la Clase
        :param asunto -> String
        :param mensaje -> String
        :param destinatario -> String
        """
        self.asunto = asunto
        self.mensaje = mensaje
        self.destinatario = destinatario

    def set_mensaje(self, mensaje:str):
        self.mensaje = mensaje

    def mensaje_automatico(self):
        yag = yagmail.SMTP(user=config['user'], password=config['password'])
        try:
            yag.send(
                to=self.destinatario,
                subject=self.asunto,
                contents=f"{self.mensaje}"
            )
        except Exception as e:
            print(f"Error al enviar mensaje ==>{e}") 

if __name__ == "__main__":
    mail =  Mail("Hola como estas", "prueba", "tomasvarasoviedo@gmail.com")
    mail.mensaje_automatico()
