from PIL import Image, ImageDraw, ImageFont
import xml.etree.ElementTree as ET
import difflib
import os
import requests
import logging
import os
from bs4 import BeautifulSoup


# set the logging level (e.g. DEBUG, INFO, WARNING, ERROR)
logging.basicConfig(level=logging.INFO)

"""
Prende un file in formato PNG e lo colora completamente di
un colore specifico in rgb.
Colore di default è bianco
"""


def coloraPNG(img, new_r=255, new_g=255, new_b=255):
    img = img.convert("RGBA")
    pixels = img.load()
    for i in range(img.width):
        for j in range(img.height):
            r, g, b, a = pixels[i, j]
            # set the color of the pixel
            pixels[i, j] = (new_r, new_g, new_b, a)
    return img


"""
Restituisce le coordinate precise per centrare su asse x e y
"""

def align_center_x():
    pass

def align_center_y():
    pass


"""
Dato un font di partenza (main_font) e un testo, indica qual è la dimensione ideale
per rispettare i vincoli di larghezza max_width
"""


def getIdealFont(image, main_font, testo, size, max_width):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(main_font, size)
    w = draw.textlength(testo, font)

    while w > max_width:
        font = ImageFont.truetype(main_font, font.size - 1)
        w = draw.textlength(testo, font)

    return font


"""

"""


"""
presa una foto fa il resize rispettando il vincolo di larghezza
"""


def diagonal_resize(foto, new_width, new_height=0):
    wSquadra, hSquadra = foto.size

    if new_height == 0:
        new_height = int(new_width * hSquadra / wSquadra)
    else:
        new_width = int(new_height * wSquadra / hSquadra)

    return foto.resize((new_width, new_height)), new_width, new_height


"""
data una parola, viene restituita quella più vicina tra le disponibili in elenco
"""


def matchWord(s, arr):
    print("ee")
    print(s)
    print("gg")
    arr = [x.lower() for x in arr]
    s = s.lower()

    match = difflib.get_close_matches(s, arr, n=1, cutoff=0.3)
    if match:
        return match[0]
    else:
        logging.INFO("Non ho trovato")
        raise Exception("Non ho trovato una squadra")


"""
Recupera la lista delle squadre di cui si hanno le grafiche
"""


def getTeams(path):
    if ".txt" in path:
        f = open(path)
        f = f.readlines()
        f = [s.strip() for s in f]
        print(f)
        return f
    return list(map(lambda elem: elem.replace('.png', ''), os.listdir(path)))



def getTemplateText(template,s):
    if os.environ['ENV'] == 'testing':
        template = "../" + template

    tree = ET.parse(template)
    example = tree.find(s)

    if example is None:
        return []

    example = example.text.split("\n")

    s = ""

    for el in example:
        s += el.strip() + "\n"

    return s

def getTemplateGuide(template):
    return getTemplateText(template,"GUIDA")


def getTemplateAttribute(template,attribute):
    if os.environ['ENV'] == 'testing':
        template = "../" + template

    tree = ET.parse(template)
    root = tree.getroot()
    return root.attrib[attribute] if attribute in root.attrib else False



def getHockeyItalianoClassificaTable(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('td', string=' CLASSIFICA UFFICIALE').parent.parent
    return table


def createHockeyItalianoClassificaList(table):
    rows = table.find_all('tr')
    classifica = []

    for i in range(2, len(rows)):
        classifica.append(rows[i].find_all('td')[1].text + "," + rows[i].find_all('td')[2].text)

    return classifica


def getAbsolutePath(relative_path):
    absolute_path = os.path.abspath(os.path.join(os.getcwd(), relative_path))
    return absolute_path


