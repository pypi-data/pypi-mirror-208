import unittest
from brain_loop_search.packing import GraphPacker
from brain_loop_search.brain_utils import CCFv3Ontology
import pandas as pd
import numpy as np


class TestGraphPacker(unittest.TestCase):
    def setUp(self):
        # create an ontology with dummy hierarchy
        self.ontology = CCFv3Ontology()
        vertices = [322, 329, 981, 337, 453, 1070, 345, 353, 361]
        # create an adjacent matrix for the graph
        self.adj_mat = pd.DataFrame(np.array([
            [0, 1, 1, 0, 0, 0, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 1, 0],
            [0, 0, 0, 0, 1, 1, 1, 1, 1],
            [0, 0, 1, 0, 0, 1, 0, 1, 0],
            [1, 0, 1, 0, 0, 1, 0, 1, 0],
            [0, 1, 1, 1, 1, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 1, 1, 0],
            [1, 1, 1, 0, 0, 1, 0, 1, 1]
        ]), index=vertices, columns=vertices)

        # create a graph packer instance
        self.graph_packer = GraphPacker(self.adj_mat, self.ontology)

    def test1(self):
        # pack the graph with new rows and columns
        new_rows = [322]
        new_cols = [337, 329, 353]
        new_mat = self.graph_packer.pack(new_rows, new_cols, def_val=0, superior_as_complement=True, aggr_func=np.sum)

        # define the expected output
        expected_mat = pd.DataFrame(np.array([
            [2., 15., 7.],
        ]), index=[322], columns=[337, 329, 353])

        # assert the new matrix is equal to the expected output
        pd.testing.assert_frame_equal(new_mat, expected_mat)

    def test2(self):
        # pack the graph with new rows and columns
        new_rows = [322]
        new_cols = [337, 329, 353]
        new_mat = self.graph_packer.pack(new_rows, new_cols, def_val=0, superior_as_complement=False, aggr_func=np.sum)

        # define the expected output
        expected_mat = pd.DataFrame(np.array([
            [0., 1., 1.],
        ]), index=[322], columns=[337, 329, 353])

        # assert the new matrix is equal to the expected output
        pd.testing.assert_frame_equal(new_mat, expected_mat)

    def test3(self):
        # pack the graph with new rows and columns
        new_rows = [337, 329, 353]
        new_cols = [337, 329, 353]
        new_mat = self.graph_packer.pack(new_rows, new_cols, def_val=0, superior_as_complement=True, aggr_func=np.sum)

        # define the expected output
        expected_mat = pd.DataFrame(np.array([
            [0., 2., 1.],
            [2., 0., 3.],
            [0., 1., 0.]
        ]), index=[337, 329, 353], columns=[337, 329, 353])

        # assert the new matrix is equal to the expected output
        pd.testing.assert_frame_equal(new_mat, expected_mat)


if __name__ == '__main__':
    unittest.main()
