import unittest
from PIL import Image
import clubscore.utils as u
import clubscore.objects.CONTAINER as CONTAINER
from parameterized import parameterized
import os
import json
import importlib


class TestImageTransparency(unittest.TestCase):

    @parameterized.expand([(team) for team in u.getTeams("../teams")])
    def test_transparency_mask__(self, team):
        os.environ['ENV'] = 'testing'

        template = "templates/test/main.xml"

        image = CONTAINER.CONTAINER.create_image_from_template(template, [team])

        self.assertTrue(True)
        os.environ.pop('ENV', None)


class TestTemplate(unittest.TestCase):
    @parameterized.expand([key for key in json.load(open('../commands/elite.json', 'r')).keys()])
    def test_single_message_template(self, template_name):
        os.environ['ENV'] = 'testing'

        template = f"/templates/{template_name}/main.xml"

        l = u.getTemplateText(template,"EXAMPLE").split("\n")

        image = CONTAINER.CONTAINER.create_image_from_template(template,l)

        image.save(f"out/{template_name}.png")
        self.assertTrue(True)
        os.environ.pop('ENV', None)

    @parameterized.expand([key for key in json.load(open('../commands/singleapi.json', 'r')).keys()])
    def test_single_message_template(self, template_name):
        os.environ['ENV'] = 'testing'

        template = f"/templates/{template_name}/main.xml"

        function_name = u.getTemplateText(template, "API").strip()
        params = u.getTemplateText(template, "PARAMETERS").strip().split("\n")

        module_name = "clubscore.API"
        module = importlib.import_module(module_name)
        function = getattr(module, function_name)

        l = function(*params)

        image = CONTAINER.CONTAINER.create_image_from_template(template,l)

        image.save(f"out/{template_name}.png")
        self.assertTrue(True)

        os.environ.pop('ENV', None)


if __name__ == '__main__':
    unittest.main()