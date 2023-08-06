import sys

from clubscore.objects.RECTANGLE import *
from clubscore.objects.IMG import *
from clubscore.objects.TEXT import *
import xml.etree.ElementTree as ET

class CONTAINER:
    """
    image: immagine di background di riferimento
    x,y : coordinate
    width: larghezza
    height: altezza
    elements: lista ordinata di elementi da inserire
    """
    def __init__(self, image, x, y, width, height, elements):
        self.image = image
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.elements = elements




    def inserisci(self, relative_x = 0, relative_y = 0):
        for el in self.elements:
            el.inserisci(self.x + relative_x, self.y + relative_y)


    """
    costruttore a partire da dizionario XML dell'oggetto
    """

    @staticmethod
    def initiate(image, root, dict, lines):

        if "requires_line" in dict:
            info_container = lines.pop(0).strip().split(",")


        x = 0 if root.tag == "MAIN_CONTAINER" else int(root.attrib["x"])
        y = 0 if root.tag == "MAIN_CONTAINER" else int(root.attrib["y"])

        width = 0 if "width" not in dict else int(root.attrib["width"])
        height = 0 if "height" not in dict else int(root.attrib["height"])

        elements = CONTAINER.interpretaTemplate(image, dict["ref"], info_container)

        return CONTAINER(image, x + int(dict["x"]), y + int(dict["y"]), width, height, elements)



    @staticmethod
    def initiateMultiple(image, root, el, lines):

        x = 0 if root.tag == "MAIN_CONTAINER" else int(root.attrib["x"])
        y = 0 if root.tag == "MAIN_CONTAINER" else int(root.attrib["y"])
        dict = el.attrib

        width = 0 if "width" not in dict else int(dict["width"])
        height = 0 if "height" not in dict else int(dict["height"])



        children = list(el)
        templates = {}


        for child in children:
            templates[int(child.attrib["inputs"])] = child.attrib["ref"]



        padding_x = 0 if "padding_x" not in dict else int(dict["padding_x"])
        padding_y = 0 if "padding_y" not in dict else int(dict["padding_y"])



        current_x = 0
        #todo FORMULA DA RIVEDERE
        current_y = int((height / (len(lines) + 1)) - height/7)


        #lista di container da restituire
        multiple_elements = []

        for line in lines:
            inputs = line.strip().split(",")
            template = templates[len(inputs)]
            #creo la lista di elementi del container che poi va posizionato
            elements = CONTAINER.interpretaTemplate(image, template, inputs)

            multiple_elements.append(CONTAINER(image, current_x, current_y, width, height, elements))

            current_x += int(u.getTemplateAttribute(template,"paddingX")) if u.getTemplateAttribute(template,"paddingX") else padding_x
            current_y += int(u.getTemplateAttribute(template,"paddingY")) if u.getTemplateAttribute(template,"paddingY") else padding_y

        return CONTAINER(image, x + int(dict["x"]), y + int(dict["y"]), width, height, multiple_elements)


    @staticmethod
    def interpretaTemplate(image, template, lines):
        if 'ENV' in os.environ and os.environ['ENV'] == 'testing':
            template = "../" + template


        tree = ET.parse(template)
        root = tree.getroot()
        children = list(root)

        x = 0 if root.tag == "MAIN_CONTAINER" else int(root.attrib["x"])
        y = 0 if root.tag == "MAIN_CONTAINER" else int(root.attrib["y"])

        width = 0 if "width" not in root.attrib else int(root.attrib["width"])
        height = 0 if "height" not in root.attrib else int(root.attrib["height"])

        elements = []

        for el in children:

            if el.tag == "IMG":
                elements.append(IMG.initiate(image, root, el.attrib, lines))
            elif el.tag == "TEXT":
                elements.append(TEXT.initiate(image, root, el.attrib,lines))
            elif el.tag == "RECTANGLE":
                elements.append(RECTANGLE.initiate(image, root, el.attrib))
            elif el.tag == "CONTAINER":
                elements.append(CONTAINER.initiate(image, root, el.attrib,lines))
            elif el.tag == "MULTIPLE":
                elements.append(CONTAINER.initiateMultiple(image, root, el,lines))
            elif el.tag == "COMBO":
                #lista di appoggio per combo
                info = lines.pop(0).strip().split(",") * len(list(el))
                for k in list(el):
                    elements.append(getattr(sys.modules[__name__], k.tag).initiate(image, root, k.attrib, info))
                #elements.append(CONTAINER.initiateMultiple(image, root, el,lines))



        main_container = CONTAINER(image, x, y, width, height, elements)

        if root.tag == "MAIN_CONTAINER":
            main_container.inserisci()
        else:
            return elements



    def create_image_from_template(template, l):
        width = int(u.getTemplateAttribute(template, "width"))
        height = int(u.getTemplateAttribute(template, "height"))

        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        CONTAINER.interpretaTemplate(image, template, l)

        return image
