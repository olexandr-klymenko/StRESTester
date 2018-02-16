from unittest import TestCase
from xml.etree import ElementTree as ET
from multiprocessing import Queue

from src.constants import ITERATIONS_NUMBER, WORKERS_NUMBER
from src.player import StressTestPlayer
from src.scenario import Scenario

cfg = {
    "urls": {
        "api": "http://127.0.0.1:8080",
        "auth": "http://127.0.0.1:8000"
    },
    "iterations_number": 1,
    "workers_number": 1,
}

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


class TestPlayer(TestCase):
    def test_scenario(self):
        xml_root = ET.fromstring(test_scenario_src)
        scenario = Scenario(xml_root)()
        test_player = StressTestPlayer(config=cfg,
                                       scenario=scenario,
                                       test_user='test_user_1',
                                       progress_queue=Queue())
        coros_collection = test_player.collect_coros()

        self.assertEqual(len(list(coros_collection)), cfg[ITERATIONS_NUMBER])
