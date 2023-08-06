from PIL import Image
from io import BytesIO
from clubscore import utils as u
import os


class IMG:

    """
    image: immagine di background di riferimento
    foto: nome del file da recuperare (eventuale)
    x,y : coordinate
    width: larghezza immagine
    """
    def __init__(self, image, foto, x, y, width, centerX=True, centerY=True):
        self.image = image
        self.foto = foto
        self.x = x
        self.y = y
        self.width = width
        self.centerX = centerX
        self.centerY = centerY

    """
    inserisce la foto dentro l'image di riferimento, prima imposta la dimensione
    Restituisce l'altezza della foto
    """
    def inserisci(self, relative_x = 0, relative_y = 0):

        if type(self.foto) is str:
            foto = Image.open(self.foto)
        else:
            foto = Image.open(BytesIO(self.foto)).convert("RGBA")


        png, w, h = u.diagonal_resize(foto, self.width)

        if self.centerX:
            w = int(w/2)
        else:
            w = 0

        if self.centerY:
            h = int(h/2)
        else:
            h = 0

        self.image.paste(png, (int(self.x + relative_x-w), int(self.y + relative_y-h)), png)

        return h

    """
    costruttore a partire da dizionario XML dell'oggetto
    """
    @staticmethod
    def initiate(image, root, dict, lines):

        if "+" in dict["foto"]:
            dict["foto"] = lines.pop(0).strip()

        else:

            if 'ENV' in os.environ and os.environ['ENV'] == 'testing':
                dict["foto"] = "../" + dict["foto"]

            if "*" in dict["foto"]:
                testo = lines.pop(0).strip()


                path = dict["foto"].split("/*")[0]



                testo = u.matchWord(testo, u.getTeams(path))

                #dict["foto"] = dict["foto"].replace("*", testo)
                dict["foto"] = f"{path}/{testo}.png"




        x = 0 if root.tag == "MAIN_CONTAINER" else int(root.attrib["x"])
        y = 0 if root.tag == "MAIN_CONTAINER" else int(root.attrib["y"])



        centerX = True if "centerX" not in dict or dict["centerX"] is "True" else False
        centerY = True if "centerY" not in dict or dict["centerY"] is "True" else False

        width = int(root.attrib["width"]) if "width" not in dict else int(dict["width"])

        return IMG(image, dict["foto"], x + int(dict["x"]), y + int(dict["y"]), width, centerX, centerY)