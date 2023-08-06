import os
import unittest
import uuid
import drb.topics.resolver as resolver
from drb.core.factory import FactoryLoader
from drb.drivers.java.drb_driver_java_factory import DrbJavaFactory


class TestLandsat8MTL(unittest.TestCase):
    path = os.path.join(os.path.dirname(__file__),
                        "LC08_L1TP_003006_20180602_20180615_01_T1_MTL.txt")
    current_node = None
    factories = FactoryLoader()

    def tearDown(self) -> None:
        # force close node after test
        if self.current_node is not None:
            self.current_node.close()

    def test_resolve_mtl_file(self):
        topic, self.current_node = resolver.resolve(self.path)
        self.assertEqual(uuid.UUID("b299117e-123b-482e-869f-ddb085677952"),
                         topic.id)
        factory_name = 'java'
        java_node_factory = self.factories.get_factory(factory_name)
        self.assertIsNotNone(java_node_factory)
        self.assertEqual(factory_name, topic.factory)

    def test_browse_mtl_file(self):
        self.current_node = DrbJavaFactory().create(self.path)
        node = self.current_node["l1MetadataFile"]

        expected = "L1TP"
        actual = node["productMetadata"]["dataType"].value
        self.assertEqual(expected, actual)

        expected = 0.11
        actual = node["imageAttributes"]["cloudCover"].value
        self.assertEqual(expected, actual)
