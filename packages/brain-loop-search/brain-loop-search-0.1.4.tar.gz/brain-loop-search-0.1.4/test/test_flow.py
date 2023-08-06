import unittest
import pandas as pd
from brain_loop_search.search import MaxFlowLoopSearch


class TestNetworkFlowSearch(unittest.TestCase):

    def setUp(self):
        self.edges = pd.DataFrame({
            "a": [1, 2, 3, 4, 5],
            "b": [4, -1, -1, 1, -1],
            "c": [5, 6, 7, 8, 9],
            "d": [-1, 2, 3, 1, 2],
            "e": [-1, -1, -1, -1, -1]
        }, index=["a", "b", "c", "d", "e"])

    def test_single(self):
        g = MaxFlowLoopSearch()
        g.add_subgraph(self.edges)
        new_g = g.single_flow('b', 'c')
        print()
        for k in new_g.edges(data=True):
            print(k)

    def test_cycle(self):
        g = MaxFlowLoopSearch()
        g.add_subgraph(self.edges)
        new_g = g.cycle_flows(['b', 'c', 'a'])
        for k, v in new_g.items():
            print(k, v.edges(data=True))

    def test_magnet(self):
        g = MaxFlowLoopSearch()
        g.add_subgraph(self.edges)
        new_g = g.magnet_flow('b', 'a')
        for k in new_g.edges(data=True):
            print(k)

    def test_cycle_flow(self):
        g = MaxFlowLoopSearch()
        g.add_subgraph(self.edges)
        new_g = g.merged_cycle_flow(['b', 'c', 'a'])
        for k in new_g.edges(data=True):
            print(k)


if __name__ == '__main__':
    unittest.main()
