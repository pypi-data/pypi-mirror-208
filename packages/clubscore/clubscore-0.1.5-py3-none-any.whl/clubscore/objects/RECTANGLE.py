from PIL import Image, ImageDraw, ImageFont

class RECTANGLE:
    """
    image: immagine di background di riferimento
    x,y : coordinate
    width: larghezza
    height: altezza
    color: colore da utilizzare nel testo
    """

    def __init__(self, image, x, y, width, height, color):
        self.image = image
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    """
    inserimento di un rettangolo
    """
    def inserisci(self, relative_x = 0, relative_y = 0):
        draw = ImageDraw.Draw(self.image)
        draw.rectangle([(self.x + relative_x, self.y + relative_y), (self.x + self.width + relative_x, self.y + self.height + relative_y)], fill=self.color)

    """
        costruttore a partire da dizionario XML dell'oggetto
    """
    @staticmethod
    def initiate(image, root, dict):
        x = 0 if root.tag == "MAIN_CONTAINER" else int(root.attrib["x"])
        y = 0 if root.tag == "MAIN_CONTAINER" else int(root.attrib["y"])

        return RECTANGLE(image, x + int(dict["x"]), y + int(dict["y"]), int(dict["width"]), int(dict["height"]),dict["color"])