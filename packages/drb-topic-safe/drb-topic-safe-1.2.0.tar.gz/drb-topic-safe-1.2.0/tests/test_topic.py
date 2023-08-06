from drb.core.node import DrbNode
from drb.topics.topic import TopicCategory
from drb.topics.dao import ManagerDao
from drb.core.factory import FactoryLoader
from drb.nodes.logical_node import DrbLogicalNode, WrappedNode
import unittest
import uuid


def generate_node_with_child(child: DrbNode, **kwargs) -> DrbNode:
    """
    Generates a node having the given node as unique child.
    Parameters:
        child (DrbNode): the future child node
    Keyword Arguments:
        name (str): node name
    Returns:
        DrbNode - A DrbNode having the given node as unique child.
    """
    parent = DrbLogicalNode(kwargs.get('name', 'container'))
    parent.append_child(WrappedNode(child))
    return parent


class TestSafeTopic(unittest.TestCase):
    dummy_id = uuid.UUID('02e07eb6-780e-4dda-bd1e-d2ada6cd4efe')
    safe_product_id = uuid.UUID('487b0c70-6199-46de-9e41-4914520e25d9')
    safe_manifest_id = uuid.UUID('3289b9eb-4c8e-4d3b-8e37-8eeb843941f5')
    ic_loader = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.ic_loader = ManagerDao()

    def test_safe_product_topic(self):
        ic = self.ic_loader.get_drb_topic(self.safe_product_id)
        self.assertIsNotNone(ic)
        self.assertEqual(self.safe_product_id, ic.id)
        self.assertIsNone(ic.subClassOf)
        self.assertEqual('SAFE Product', ic.label)
        self.assertIsNone(ic.description)
        self.assertEqual(TopicCategory.CONTAINER, ic.category)
        self.assertIsNone(ic.factory)
        self.assertEqual(1, len(ic.signatures))

    def test_safe_product_topic_signature(self):
        ic = self.ic_loader.get_drb_topic(self.safe_product_id)
        name = 'foobar.safe'

        node = generate_node_with_child(DrbLogicalNode('manifest.safe'),
                                        name=name)
        self.assertTrue(ic.matches(node))
        node = generate_node_with_child(DrbLogicalNode('MANIFEST.SAFE'),
                                        name=name)
        self.assertTrue(ic.matches(node))

        node = generate_node_with_child(DrbLogicalNode('manifest.xml'),
                                        name=name)
        self.assertTrue(ic.matches(node))
        node = generate_node_with_child(DrbLogicalNode('MANIFEST.XML'),
                                        name=name)
        self.assertTrue(ic.matches(node))

        node = generate_node_with_child(DrbLogicalNode('xfdumanifest.xml'),
                                        name=name)
        self.assertTrue(ic.matches(node))
        node = generate_node_with_child(DrbLogicalNode('XFDUMANIFEST.XML'),
                                        name=name)
        self.assertTrue(ic.matches(node))

        node = generate_node_with_child(DrbLogicalNode('anything.safe'))
        self.assertFalse(ic.matches(node))

        node = generate_node_with_child(DrbLogicalNode('manifest.tar'))
        self.assertFalse(ic.matches(node))

        node = generate_node_with_child(DrbLogicalNode('foobar'))
        self.assertFalse(ic.matches(node))

        node = generate_node_with_child(DrbLogicalNode('foobar'), name=name)
        self.assertFalse(ic.matches(node))

        node = generate_node_with_child(DrbLogicalNode('manifest.safe'),
                                        name='foobar')
        self.assertFalse(ic.matches(node))

    def test_safe_manifest_topic(self):
        ic = self.ic_loader.get_drb_topic(self.safe_manifest_id)
        self.assertIsNotNone(ic)
        self.assertEqual(self.safe_manifest_id, ic.id)
        self.assertIsNone(ic.subClassOf)
        self.assertEqual('SAFE Manifest', ic.label)
        self.assertIsNone(ic.description)
        self.assertEqual(TopicCategory.FORMATTING, ic.category)
        self.assertEqual('xml', ic.factory)
        self.assertEqual(1, len(ic.signatures))

    def test_safe_manifest_topic_signature(self):
        node = DrbLogicalNode('manifest.safe')
        item_class = self.ic_loader.get_drb_topic(self.safe_manifest_id)
        self.assertTrue(item_class.matches(node))

        node = DrbLogicalNode('MANIFEST.SAFE')
        item_class = self.ic_loader.get_drb_topic(self.safe_manifest_id)
        self.assertTrue(item_class.matches(node))
