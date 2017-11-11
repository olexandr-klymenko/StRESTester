from copy import deepcopy
from pprint import pprint
from xml.etree import ElementTree as ET
from typing import List, Callable
from collections import defaultdict

from action_registry.registry import ActionsRegistry
from constants import *
from utils import skipped_actions

__all__ = ['Scenario']

MANDATORY_ATTRIBUTES = [NAME]
OPTIONAL_ATTRIBUTES = [RETURN, IGNORE_ERRORS, SKIP_METRIC]


def validate_child(child: ET.Element, registered_actions: List):
    """
    Validates scenario steps

    :param child:
    :param registered_actions:
    :return:
    """
    action_attributes = set(child.keys())
    mandatory_attributes = set(MANDATORY_ATTRIBUTES)
    optional_attributes = set(MANDATORY_ATTRIBUTES + OPTIONAL_ATTRIBUTES)

    try:
        if child.tag not in registered_actions:
            raise Exception('Scenario action "%s" not in action list %s' %
                            (child.tag, registered_actions))

        if not mandatory_attributes.issubset(action_attributes):
            raise Exception("Mandatory attributes missing in '%s'" %
                            str(mandatory_attributes - action_attributes))

        if not action_attributes.issubset(optional_attributes):
            raise Exception("There is at least one invalid attribute: '%s'" %
                            str(action_attributes - optional_attributes))

        nodes = [node.tag for node in child]
        mandatory_arguments = ActionsRegistry.get_action(child.tag).args
        if mandatory_arguments:

            if not set(mandatory_arguments).issubset(set(nodes)):
                raise Exception("Mandatory arguments missing: %s" %
                                str(set(mandatory_arguments) - set(nodes)))

        if len(nodes) != len(set(nodes)):
            raise Exception('There is duplicated arguments in action'
                            ' "%s: %s != %s"' %
                            (child.tag, list(nodes), list(set(nodes))))

    except AssertionError:
        pprint(ET.tostring(child).decode(), indent=4)
        raise


class Scenario:
    """
    Iterable container for stress test scenario steps
    """
    _registered_actions = ActionsRegistry.get_actions()
    _validated_steps = []
    rest_actions_info = defaultdict(int)

    def __init__(self, path: str,
                 validator: Callable = validate_child
                 ):
        with open(path) as f:
            _root = ET.parse(f).getroot()
        self._validator = validator
        self._root = self._parse(_root)

    def __call__(self, *args, **kwargs) -> ET.Element:
        return self._root

    def __len__(self):
        return len(self._root)

    def __iter__(self):
        for el in self._root:
            yield el

    def _parse(self, raw_root: ET.Element) -> ET.Element:
        """
        Unpack loops into plain xml root of scenario
        :param raw_root:
        :return:
        """
        new_root = ET.Element('scenario')

        def _parse_root(root: ET.Element=raw_root) -> ET.Element:
            nonlocal new_root

            for child in root:
                if child.tag != REPEAT:
                    if bool(child.attrib.get(SKIP_METRIC)):
                        skipped_actions.add(child.attrib[NAME])
                    if ET.tostring(child) not in self._validated_steps:
                        self._validator(child, self._registered_actions)
                        self._validated_steps.append(ET.tostring(child))

                    new_root.append(child)
                    if child.tag == REST:
                        self.rest_actions_info[child.attrib[NAME]] += 1

                else:
                    for cycle in range(int(child.attrib[CYCLES])):
                        _parse_root(deepcopy(child))
            return new_root

        return _parse_root()
