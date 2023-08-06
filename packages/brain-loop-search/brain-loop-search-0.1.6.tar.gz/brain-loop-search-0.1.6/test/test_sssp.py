import unittest
import pandas as pd
from brain_loop_search.search import ShortestPathLoopSearch


class TestLoopSearchGraph(unittest.TestCase):

    def setUp(self):
        self.edges = pd.DataFrame({
            "a": [1, 2, 3, 4, 5],
            "b": [4, -1, -1, 1, -1],
            "c": [5, 6, 7, 8, 9],
            "d": [-1, 2, 3, 1, 2],
            "e": [-1, -1, -1, -1, -1]
        }, index=["a", "b", "c", "d", "e"])

    def test_add_subgraph(self):
        g = ShortestPathLoopSearch()
        g.add_subgraph(self.edges)
        self.assertCountEqual(g.graph.nodes(), ["a", "b", "c", "d", "e"])
        self.assertCountEqual(g.graph.edges(data=True), [
            ("a", "a", {"weight": 1}),
            ("b", "a", {"weight": 2}),
            ("c", "a", {"weight": 3}),
            ("d", "a", {"weight": 4}),
            ("e", "a", {"weight": 5}),
            ("c", "c", {"weight": 7}),
            ("d", "d", {"weight": 1}),
            ("d", "b", {"weight": 1}),
            ("a", "b", {"weight": 4}),
            ("b", "c", {"weight": 6}),
            ("d", "c", {"weight": 8}),
            ("a", "c", {"weight": 5}),
            ("e", "c", {"weight": 9}),
            ("b", "d", {"weight": 2}),
            ("c", "d", {"weight": 3}),
            ("e", "d", {"weight": 2})
        ])

    def test_find_loop_sssp(self):
        g = ShortestPathLoopSearch()
        g.add_subgraph(self.edges)
        loops, sssp = g.chain_screen(n_axis=2)
        self.assertCountEqual(list(loops.keys()), [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d"), ("b", "c")])
        self.assertCountEqual(["".join(s) for s in loops[("a", "b")]['loop']], ["ab", "ba"])
        self.assertCountEqual(["".join(s) for s in loops[("a", "c")]['loop']], ["ac", 'ca'])
        self.assertCountEqual(["".join(s) for s in loops[("b", "d")]['loop']], ["bd", "db"])
        self.assertCountEqual(["".join(s) for s in loops[("c", "d")]['loop']], ["cd", 'dbc'])
        self.assertCountEqual(["".join(s) for s in loops[("b", "c")]['loop']], ["bc", 'cdb'])
        print(loops)

    def test_find_loop_sssp_knot_allow(self):
        g = ShortestPathLoopSearch()
        g.add_subgraph(self.edges)
        print()
        loops, sssp = g.chain_screen(n_axis=2, allow_knots=True)
        for k, v in loops.items():
            print(k, v)

    def test_find_loop_sssp_axis_include(self):
        g = ShortestPathLoopSearch()
        g.add_subgraph(self.edges)
        print()
        loops, sssp = g.chain_screen(n_axis=2, allow_knots=True, axis_must_include=['a'])
        for k, v in loops.items():
            print(k, v)

    def test_find_loop_sssp_axis_pool(self):
        g = ShortestPathLoopSearch()
        g.add_subgraph(self.edges)
        print()
        loops, sssp = g.chain_screen(n_axis=2, allow_knots=True, axis_pool=['a', 'b'])
        for k, v in loops.items():
            print(k, v)

    def test_find_loop_sssp_3axis(self):
        g = ShortestPathLoopSearch()
        g.add_subgraph(self.edges)
        print()
        loops, sssp = g.chain_screen(n_axis=3, top=3)
        for k, v in loops.items():
            print(k, v)

    def test_weight_trans(self):
        g = ShortestPathLoopSearch()
        g.add_subgraph(self.edges)
        g.weight_transform()
        print(g.graph.edges(data=True))

    def test_pair(self):
        g = ShortestPathLoopSearch()
        g.add_subgraph(self.edges)
        print(g.pair_complement(['a', 'b', 'c']))


if __name__ == '__main__':
    unittest.main()
