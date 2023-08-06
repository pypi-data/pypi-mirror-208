import unittest
from brain_loop_search.brain_utils import draw_single_loop, draw_brain_graph
from brain_loop_search.search import MaxFlowLoopSearch
import pandas as pd
import numpy as np

class DrawTest(unittest.TestCase):
    def test_loop(self):
        draw_single_loop([[950, 974, 417], [417, 993], [993, 234, 289, 950]], 'test.png')

    def test_graph(self):
        vertices = [322, 329, 981, 337, 453, 1070, 345, 353, 361]
        # create an adjacent matrix for the graph
        adj_mat = pd.DataFrame(np.array([
            [0, 2, 1, 0, 0, 0, 1, 8, 0],
            [0, 0, 3, 1, 5, 1, 0, 5, 0],
            [0, 0, 0, 0, 1, 3, 2, 1, 2],
            [0, 0, 6, 0, 0, 1, 0, 4, 0],
            [1, 0, 1, 0, 0, 1, 0, 4, 0],
            [0, 1, 7, 1, 4, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 0, 0, 0, 2, 2, 1, 0],
            [1, 2, 2, 0, 0, 1, 0, 1, 1]
        ]), index=vertices, columns=vertices)
        g = MaxFlowLoopSearch()
        g.add_subgraph(adj_mat)
        draw_brain_graph(g.graph, 'test2.png', thr=3)


if __name__ == '__main__':
    unittest.main()
