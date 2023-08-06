import unittest

from drb.core import DrbNode
from drb.drivers.file import DrbFileNode
from drb.nodes.logical_node import DrbLogicalNode

from drb.extractor import (
    ConstantExtractor,
    PythonExtractor,
    XQueryExtractor,
    parse_extractor,
    ScriptExtractor
)


def name_test(node: DrbNode):
    return node.name + '_with_script'


class TestParseExtractor(unittest.TestCase):
    def test_constant_extractor(self):
        node = DrbLogicalNode('test')

        data = {'constant': True}
        extractor = parse_extractor(data)
        self.assertIsNotNone(extractor)
        self.assertIsInstance(extractor, ConstantExtractor)
        self.assertEqual(data['constant'], extractor.extract(node))

        data = {'constant': 'foobar'}
        extractor = parse_extractor(data)
        self.assertIsNotNone(extractor)
        self.assertIsInstance(extractor, ConstantExtractor)
        self.assertEqual(data['constant'], extractor.extract(node))

        data = {'constant': 3}
        extractor = parse_extractor(data)
        self.assertIsNotNone(extractor)
        self.assertIsInstance(extractor, ConstantExtractor)
        self.assertEqual(data['constant'], extractor.extract(node))

        data = {'constant': 0.3}
        extractor = parse_extractor(data)
        self.assertIsNotNone(extractor)
        self.assertIsInstance(extractor, ConstantExtractor)
        self.assertEqual(data['constant'], extractor.extract(node))

    def test_python_extractor(self):
        node = DrbLogicalNode('foobar')
        node.add_attribute('attr1', 42)
        data = {'python': 'return node.get_attribute("attr1")'}
        extractor = parse_extractor(data)
        self.assertIsNotNone(extractor)
        self.assertIsInstance(extractor, PythonExtractor)
        self.assertEqual(42, extractor.extract(node))

    def test_xquery_extractor(self):
        child = DrbLogicalNode('child')
        child.add_attribute('attr', 42)
        child.value = 'test'
        node = DrbLogicalNode('foobar')
        node.append_child(child)

        data = {'xquery': 'xs:integer(data(./child/@attr))'}
        extractor = parse_extractor(data)
        self.assertIsNotNone(extractor)
        self.assertIsInstance(extractor, XQueryExtractor)
        self.assertEqual(42, extractor.extract(node))

        data = {'xquery': 'data(./child)'}
        extractor = parse_extractor(data)
        self.assertEqual('test', extractor.extract(node))

    def test_script_extractor(self):
        data = {'script': 'tests.test_extractor:name_test'}
        node = DrbFileNode('tests')
        extractor = parse_extractor(data)
        self.assertIsNotNone(extractor)
        self.assertIsInstance(extractor, ScriptExtractor)
        self.assertEqual('tests_with_script', extractor.extract(node))
