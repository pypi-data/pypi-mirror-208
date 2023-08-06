from PIL import Image, ImageDraw, ImageFont
import clubscore.utils as u
import os

class TEXT:

    """
    image: immagine di background di riferimento
    test: testo da scrivere
    font_path: font di riferimento  da utilizzare (fornire path)
    x,y : coordinate
    size: size di partenza o size da applicare nel font
    color: colore da utilizzare nel testo
    """

    def __init__(self, image, testo, font_path, x, y, size, color, centerX=True, centerY=True, perimeter_fill = -1):
        self.image = image
        self.testo = testo
        self.font_path = font_path
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.centerX = centerX
        self.centerY = centerY
        self.perimeter_fill = perimeter_fill

    """
    inserisce il testo in maniera agnostica, non sa nulla se non le coordinate, e la dimensione del font
    """

    def inserisci(self, relative_x = 0, relative_y = 0):
        if 'ENV' in os.environ and os.environ['ENV'] == 'testing':
            self.font_path = "../" + self.font_path

        font = ImageFont.truetype(self.font_path, self.size)
        draw = ImageDraw.Draw(self.image)

        if self.centerX:
            w = int(draw.textlength(self.testo, font)/2)
        else:
            w = 0

        if self.centerY:
            h = int(font.getbbox(self.testo)[3]/2)
        else:
            h = 0

        if self.perimeter_fill == -1:
            draw.text((int(self.x + relative_x-w), int(self.y + relative_y-h)), self.testo, font=font, fill=self.color)

        else:


            total_text_width, total_text_height = draw.textsize(self.testo, font=font)
            width_difference = self.perimeter_fill - total_text_width
            gap_width = int(width_difference / (len(self.testo) - 1))
            xpos = self.x
            ypos = self.y
            for letter in self.testo:
                draw.text((xpos, ypos), letter, self.color, font=font)
                letter_width, letter_height = draw.textsize(letter, font=font)
                xpos += letter_width + gap_width

    """
    costruttore a partire da dizionario XML dell'oggetto
    """
    @staticmethod
    def initiate(image, root, dict, lines):

        if "testo" in dict:
            if "*" in dict["testo"]:

                testo = lines.pop(0).strip()

                if "match_word" in dict:
                    print(dict["match_word"])
                    testo = u.matchWord(testo, u.getTeamsFromTXT(dict["match_word"]))

                if "upper" in dict and "True" in dict["upper"]:
                    testo = testo.upper()

                dict["testo"] = dict["testo"].replace("*", testo)

            final_text = dict["testo"]

        elif "concatenation" in dict:

            for i in range(len(lines)):
                repl = "{%s}" % str(i)
                if repl in dict["concatenation"]:
                    testo = lines[i].strip()

                    if "match_word" in dict:
                        print(dict["match_word"])
                        testo = u.matchWord(testo, u.getTeamsFromTXT(dict["match_word"]))

                    if "upper" in dict and "True" in dict["upper"]:
                        testo = testo.upper()

                    dict["concatenation"] = dict["concatenation"].replace(repl, testo)


            final_text = dict["concatenation"]



        x = 0 if root.tag == "MAIN_CONTAINER" else int(root.attrib["x"])
        y = 0 if root.tag == "MAIN_CONTAINER" else int(root.attrib["y"])



        perimeter_fill = -1 if "perimeter_fill" not in dict else int(dict["perimeter_fill"])


        centerX = True if "centerX" not in dict or dict["centerX"] is "True" else False
        centerY = True if "centerY" not in dict or dict["centerY"] is "True" else False

        return TEXT(image, final_text, dict["font"], x + int(dict["x"]), y + int(dict["y"]), int(dict["size"]),dict["color"], centerX, centerY,perimeter_fill)