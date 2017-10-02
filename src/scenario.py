from copy import deepcopy
from xml.etree import ElementTree as ET

from action_registry.registry import ActionsRegistry
from constants import REPEAT, CYCLES, RETURN


__all__ = ['Scenario']


MANDATORY_ATTRIBUTES = ['name']
AVAILABLE_ATTRIBUTES = [RETURN]


class Scenario:
    _registered_actions = ActionsRegistry.get_actions()

    def __init__(self, path: str):
        self._path = path
        self._root = self._parse()

    def __call__(self, *args, **kwargs) -> ET.Element:
        return self._root

    def __len__(self):
        return len(self._root)

    def __iter__(self):
        for el in self._root:
            yield el

    def _parse(self) -> ET.Element:
        with open(self._path) as f:
            _root = ET.parse(f).getroot()

        def _parse_root(root: ET.Element, new_root=None) -> ET.Element:

            for child in root:
                if child.tag != REPEAT:
                    self._validate_child(child)
                    if new_root is None:
                        new_root = ET.Element('scenario')
                    new_root.append(child)
                else:
                    for cycle in range(int(child.attrib[CYCLES])):
                        _parse_root(deepcopy(child), new_root)
            return new_root

        return _parse_root(deepcopy(_root))

    def _validate_child(self, child: ET.Element):
        assert child.tag in self._registered_actions, \
            'Scenario action "%s" not in action list %s' % (child.tag, self._registered_actions)

        assert MANDATORY_ATTRIBUTES in child.keys(), 'Mandatory attributes missing'

        assert child.keys() in MANDATORY_ATTRIBUTES + AVAILABLE_ATTRIBUTES

        nodes = [node.tag for node in child]
        assert len(nodes) == len(set(nodes)), 'There is duplicated arguments in action "%s: %s != %s"'\
                                              % (child.tag, list(nodes), list(set(nodes)))
