from unittest import TestCase
from xml.etree import ElementTree as ET

from src.scenario import Scenario, InvalidScenario

test_scenario_src = """<scenario>
    <repeat cycles="10">
    <rest name="Create User">
        <method>POST</method>
        <url>{{ api_url_1 }}/accounts/</url>
        <data>{"login": "{{ username }}", "password": "{{ password }}"}</data>
    </rest>
    </repeat>
    <rest name="Delete profile" skip_metric="True">
        <method>DELETE</method>
        <url>{{ api_url_2 }}/super/profiles/</url>
        <params>{"profile_id": "{{ profile_id }}", "user_id": "{{ user_id }}"}</params>
    </rest>
    </scenario>"""

invalid_test_scenario_src_1 = """<scenario>
    <res name="Create User">
        <method>POST</method>
        <url>{{ api_url_1 }}/accounts/</url>
        <data>{"login": "{{ username }}", "password": "{{ password }}"}</data>
    </res>
    </scenario>"""

invalid_test_scenario_src_2 = """<scenario>
    <rest>
        <method>POST</method>
        <url>{{ api_url_1 }}/accounts/</url>
        <data>{"login": "{{ username }}", "password": "{{ password }}"}</data>
    </rest>
    </scenario>"""

invalid_test_scenario_src_3 = """<scenario>
    <rest name="Create User" invalid_attribute="some value">
        <method>POST</method>
        <url>{{ api_url_1 }}/accounts/</url>
        <data>{"login": "{{ username }}", "password": "{{ password }}"}</data>
    </rest>
    </scenario>"""

invalid_test_scenario_src_4 = """<scenario>
    <rest name="Create User">
        <url>{{ api_url_1 }}/accounts/</url>
        <data>{"login": "{{ username }}", "password": "{{ password }}"}</data>
    </rest>
    </scenario>"""

invalid_test_scenario_src_5 = """<scenario>
    <rest name="Create User">
        <method>POST</method>
        <method>GET</method>
        <url>{{ api_url_1 }}/accounts/</url>
        <data>{"login": "{{ username }}", "password": "{{ password }}"}</data>
    </rest>
    </scenario>"""


class TestScenario(TestCase):
    def test_scenario(self):
        xml_root = ET.fromstring(test_scenario_src)
        test_scenario = Scenario(xml_root)()
        self.assertEqual(len(test_scenario), len(Scenario(test_scenario)))
        test_scenario_element = test_scenario[0]
        self.assertTrue(isinstance(test_scenario_element, ET.Element))

        self.assertTrue([el for _, el in enumerate(Scenario(xml_root))])

        with self.assertRaises(InvalidScenario):
            Scenario(ET.fromstring(invalid_test_scenario_src_1))

        with self.assertRaises(InvalidScenario):
            Scenario(ET.fromstring(invalid_test_scenario_src_2))

        with self.assertRaises(InvalidScenario):
            Scenario(ET.fromstring(invalid_test_scenario_src_3))

        with self.assertRaises(InvalidScenario):
            Scenario(ET.fromstring(invalid_test_scenario_src_4))

        with self.assertRaises(InvalidScenario):
            Scenario(ET.fromstring(invalid_test_scenario_src_5))
