import unittest
from brain_loop_search.packing import VertexPacker
from brain_loop_search.brain_utils import CCFv3Ontology


class TestVertexPacker(unittest.TestCase):

    def test_filter_by_level(self):
        # Create a test ontology
        ontology = CCFv3Ontology()
        vertices = [322, 329, 981, 337, 453, 8, 1070]
        # Create a VertexPacker object for testing
        vp = VertexPacker(vertices, ontology)
        # Test filtering by level
        vp.filter_by_level(fro=1, to=2)
        self.assertEqual(set(vp.stash()), {329, 337})

    def test_filter_by_depth(self):
        # Create a test ontology
        ontology = CCFv3Ontology()
        vertices = [322, 329, 981, 337, 453, 8, 1070]
        # Create a VertexPacker object for testing
        vp = VertexPacker(vertices, ontology)
        # Test filtering by depth
        vp.filter_by_depth(fro=1, to=2)
        self.assertEqual(set(vp.stash()), {8})

    def test_filter_super(self):
        # Create a test ontology
        ontology = CCFv3Ontology()
        vertices = [322, 329, 981, 337, 453, 8, 1070]
        # Create a VertexPacker object for testing
        vp = VertexPacker(vertices, ontology)
        # Test filtering by super nodes
        vp.filter_super()
        self.assertEqual(set(vp.stash()), {1070, 337, 981})

    def test_filter_sub(self):
        # Create a test ontology
        ontology = CCFv3Ontology()
        vertices = [322, 329, 981, 337, 453, 8, 1070]
        # Create a VertexPacker object for testing
        vp = VertexPacker(vertices, ontology)
        # Test filtering by sub nodes
        vp.filter_sub()
        self.assertEqual(set(vp.stash()), {8})

    def test_filter_by_immediate_child_of(self):
        # Create a test ontology
        ontology = CCFv3Ontology()
        vertices = [322, 329, 981, 337, 453, 8, 1070]
        # Create a VertexPacker object for testing
        vp = VertexPacker(vertices, ontology)
        # Test filtering by immediate child nodes
        vp.filter_by_immediate_child_of([322, 453])
        self.assertEqual(set(vp.stash()), {329, 337, 322})

    def test_filter_by_descendants_of(self):
        # Create a test ontology
        ontology = CCFv3Ontology()
        vertices = [322, 329, 981, 337, 453, 8, 1070]
        # Create a VertexPacker object for testing
        vp = VertexPacker(vertices, ontology)
        # Test filtering by descendants nodes
        vp.filter_by_descendants_of([322])
        self.assertEqual(set(vp.stash()), {1070, 981, 329, 337})

    def test_merge_by_level(self):
        # Create a test ontology
        ontology = CCFv3Ontology()
        vertices = [322, 329, 981, 337, 453, 8, 1070]
        # Create a VertexPacker object for testing
        vp = VertexPacker(vertices, ontology)
        # Test merging by level
        vp.merge_by_level(thr=2)
        self.assertEqual(set(vp.stash()), {322, 453, 8})

    def test_merge_by_depth(self):
        # Create a test ontology
        ontology = CCFv3Ontology()
        vertices = [322, 329, 981, 337, 453, 8, 1070]
        # Create a VertexPacker object for testing
        vp = VertexPacker(vertices, ontology)
        # Test merging by depth
        vp.merge_by_depth(thr=1)
        self.assertEqual(set(vp.stash()), {8})


if __name__ == '__main__':
    unittest.main()
