from unittest import TestCase
from xml.etree import ElementTree as ET

from src.scenario import Scenario

test_scenario_src = """<scenario>
    <repeat cycles="10">
    <rest name="Create User">
        <method>POST</method>
        <url>{{ api_url_1 }}/accounts/</url>
        <data>{"login": "{{ username }}", "password": "{{ password }}"}</data>
    </rest>
    </repeat>
    </scenario>"""


class TestScenario(TestCase):

    def test_scenario(self):
        xml_root = ET.fromstring(test_scenario_src)
        test_scenario = Scenario(xml_root)()
        self.assertEqual(len(test_scenario), len(Scenario(test_scenario)))
        test_scenario_element = test_scenario[0]
        self.assertTrue(isinstance(test_scenario_element, ET.Element))
