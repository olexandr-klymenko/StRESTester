from copy import deepcopy
from pprint import pprint
from xml.etree import ElementTree as ET

from action_registry.registry import ActionsRegistry
from constants import REPEAT, CYCLES, RETURN

__all__ = ['Scenario']

MANDATORY_ATTRIBUTES = ['name']
OPTIONAL_ATTRIBUTES = [RETURN]


class Scenario:
    """
    Iterable container for stress test scenario steps
    """
    _registered_actions = ActionsRegistry.get_actions()
    _validated_steps = []

    def __init__(self, path: str):
        with open(path) as f:
            _root = ET.parse(f).getroot()
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
                    if ET.tostring(child) not in self._validated_steps:
                        self._validate_child(child)
                        self._validated_steps.append(ET.tostring(child))

                    new_root.append(child)

                else:
                    for cycle in range(int(child.attrib[CYCLES])):
                        _parse_root(deepcopy(child))
            return new_root

        return _parse_root()

    def _validate_child(self, child: ET.Element):
        """
        Validates scenario steps
        :param child:
        :return:
        """
        action_attributes = set(child.keys())
        mandatory_attributes = set(MANDATORY_ATTRIBUTES)
        optional_attributes = set(MANDATORY_ATTRIBUTES + OPTIONAL_ATTRIBUTES)

        try:
            assert child.tag in self._registered_actions, \
                'Scenario action "%s" not in action list %s' %\
                (child.tag, self._registered_actions)

            assert mandatory_attributes.issubset(action_attributes), \
                "Mandatory attributes missing in '%s'" %\
                str(mandatory_attributes - action_attributes)

            assert action_attributes.issubset(optional_attributes), \
                "There is at least one invalid attribute: '%s'" %\
                str(action_attributes - optional_attributes)

            nodes = [node.tag for node in child]
            mandatory_arguments = ActionsRegistry.get_action(child.tag).args
            if mandatory_arguments:

                assert set(mandatory_arguments).issubset(set(nodes)),\
                    "Mandatory arguments missing: %s" % \
                    str(set(mandatory_arguments) - set(nodes))

            assert len(nodes) == len(set(nodes)),\
                'There is duplicated arguments in action "%s: %s != %s"' %\
                (child.tag, list(nodes), list(set(nodes)))

        except AssertionError:
            pprint(ET.tostring(child).decode(), indent=4)
            raise
