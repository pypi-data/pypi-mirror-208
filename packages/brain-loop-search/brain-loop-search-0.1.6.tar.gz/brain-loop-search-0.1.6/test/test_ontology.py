import unittest
from brain_loop_search.brain_utils import CCFv3Ontology


class TestOntology(unittest.TestCase):
    def test_check_include1(self):
        to_include = [997, -1]
        ont = CCFv3Ontology()
        self.assertEqual(False, ont.check_include(to_include))

    def test_check_include2(self):
        to_include = [997]
        ont = CCFv3Ontology()
        self.assertEqual(True, ont.check_include(to_include))

    def test_levels_of(self):
        to_check = [997, 68, 8]
        ont = CCFv3Ontology()
        self.assertEqual([9, 0, 8], list(ont.levels_of(to_check)))

    def test_depths_of(self):
        to_check = [997, 68, 8]
        ont = CCFv3Ontology()
        self.assertEqual([0, 7, 1], list(ont.depths_of(to_check)))

    def test_ancestors_of(self):
        to_check = [997, 68, 8]
        ont = CCFv3Ontology()
        print(ont.ancestors_of(to_check))

    def test_immediate_children_of(self):
        to_check = [997, 68, 8]
        ont = CCFv3Ontology()
        print(ont.immediate_children_of(to_check))


if __name__ == '__main__':
    unittest.main()
