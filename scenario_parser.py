from xml.etree import ElementTree as ET
from copy import deepcopy

from constants import REPEAT, CYCLES


def get_parsed_scenario_root(scenario_path) -> ET.Element:
    with open(scenario_path) as f:
        _root = ET.parse(f).getroot()

    def parse_root(root, new_root=None) -> ET.Element:
        for child in root:
            if child.tag != REPEAT:
                if new_root is None:
                    new_root = ET.Element('scenario')
                new_root.append(child)
            else:
                for cycle in range(int(child.attrib[CYCLES])):
                    parse_root(deepcopy(child), new_root)
        return new_root

    return parse_root(deepcopy(_root))
