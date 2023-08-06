"""
This module for now involves 2 loop search algorithms. Because of the great complexity this task can have, such
loop searching can only be done in a screening way. Thus, they might not be able to give every possible results,
but it's good to make a combination of different strategies and use multiple modailty of data to make up for this.

# Shortest Path Methods
One method is based on shortest path that will typically get you a series of loops made up of nodes. The shortest path
integrates scores on the path so the smaller the score is the better the loop can be. And the scores are actually
addable. These are the basic requirements of using such method.

Shortest paths itself can't be loops, so the strategy tries different ways to assemble the shortest paths into loops.
It can be a direction connection plus a reverse shortest path, or both shortest path. By doing so, a new concept is
introduced as the axis, which is the key node in the graph that you use them as the source or target in shortest path
searching. You can have more than 2 axes, of course.

There are other problems like duplication or knots in a loop. Typically, you wouldn't expect that because it means
a more basic loop exists, but between some nodes there are only crossed shortest paths connecting them.

# Max flow methods
Given the problems the shortest paths can have, we find that shortest paths tend to throw away much of the information
in the network, and we need another form of computation. Flow methods come in handy because they balance between the overall
graph weights, while introducing other problems. In a flow, the bigger the weight the better the connection can be.
The weight can't be summed along any path, but be summed in a node. This requires a very different kind of data than shortest
path.

It returns a new graph of flows. You can see the graph as a new distribution of connection, when you want to look into
the overall connection from one node to another, which ways are preferred. The downsides are obvious, since flow computation
is intensive, you can only pick specific axes to make the flow, and also a flow is a graph instead of an actual loop.
No mass screening this time but look more closely at specific sites.

Is it possible to bring these two methods together? Yes, because the flow results can replace the graph to do shortest paths.
This way you may get diverse loops with different flow strategies on a single network.
"""


import typing

import networkx as nx
import pandas as pd
import numpy as np
import itertools
from copy import deepcopy
from collections import OrderedDict


class GraphMaintainer:

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_subgraph(self, adj_mat: pd.DataFrame, def_val: float = -1):
        """
        Add weighted edges from a pandas dataframe as an adjacent matrix.

        Each row/column name is a vertex that can be mapped to the input ontology.

        The graph is directed and the projection is from row to column.

        This function can be called multiple times for different dataframes if you don't have
        them in a single dataframe, but loading edges with same indices will overwrite the original one.

        :param adj_mat: a pandas dataframe, with unique rows and columns.
        :param def_val: the default value for non-connecting edges.
        """
        assert adj_mat.index.is_unique, "rows contain duplication"
        assert adj_mat.columns.is_unique, "columns contain duplication"
        for fro, row in adj_mat.iterrows():
            active = row[row != def_val]
            self.graph.add_weighted_edges_from([*zip([fro] * len(active), active.index, active)])

    def weight_transform(self, in_key='weight', out_key='weight', func=lambda x: 1 / x):
        """
        Transform the edge weights. The transform is based on networkx edge data, which is maintained as a dict.
        The default key is 'weight', which is the default key when the edge is added to the graph and used for both
        shortest path and flow algorithms' input. So this function replace the weights by default.

        This is useful because different algorithms such as network flow and shortest paths expect edge weights
        of different meaning, thus leading to different treatment to 'big' and 'small'. Smaller weights in network flow
        is equivalent to bigger weights in shortest path.

        :param func: transform function.
        :param in_key: input attribute key.
        :param out_key: output attribute key.
        """
        w = nx.get_edge_attributes(self.graph, 'weight')
        for k, v in w.items():
            w[k] = {'weight': func(v)}
        nx.set_edge_attributes(self.graph, w)


class MaxFlowLoopSearch(GraphMaintainer):
    """
    Using networkx directed graph for implementing loop search algorithms based on network flow.

    As this method uses network flow, you should make sure the edge weights are meaningful so that
    a bigger weight means a strong connection. The flow along a path is throttled by the max capacity,
    and the whole flow is distributed over the edges and determined by the overall capacity.

    With this class, you can get loops in forms of a residual network.
    There is no definite loop that can form a list, unlike shortest path, but it maximally considers and
    retains the information of the whole graph while shortest paths may omit lesser good routes.
    The graph generated can even be applied the shortest path search, if you find it make sense. You can
    assign the graph member in `ShortestPathLoopSearch` with the result from this one, because they are identical in form.

    Since network flow considers only one pair of source and sink, applying this on multiple pairs
    can be time-consuming, so the method isn't designed to search through all pairs in the graph.
    """

    def single_flow(self, s, t, rm_negative_and_zero=True):
        """
        compute a max flow, on edge attribute 'weight'. Though it uses the networkx algorithm that stores the result
        in a new attribute 'flow', it will get this value back to 'weight' for less confusion.

        :param s: source
        :param t: sink
        :param rm_negative_and_zero: remove the negative and zero flow on all edges, default as True.
        :return: a directed graph with flow results as its edges.
        """
        flow = nx.flow.preflow_push(self.graph, s, t, 'weight')
        it = nx.get_edge_attributes(flow, 'flow').items()
        out = nx.DiGraph()
        out.add_weighted_edges_from([k + (v,) for k, v in it if not rm_negative_and_zero or v > 0])
        return out

    def cycle_flows(self, axes: typing.Iterable, rm_negative_and_zero=True):
        """
        compute multiple max flow along multiple key vertices that are supposed to be on the loop.

        The flow will be computed from the 1st to 2nd, 2nd to 3rd, ..., last to 1st.

        :param axes: the key vertices.
        :param rm_negative_and_zero: remove the negative and zero flow on all edges, default as True.
        :return: a dict of all the flow that is identical to that of the `single_flow`.
        """
        axes = list(axes)
        axes = axes + axes[:1]
        out = {}
        for i, j in itertools.pairwise(axes):
            out[(i, j)] = self.single_flow(i, j, rm_negative_and_zero)
        return out

    def magnet_flow(self, s, t):
        """
        With a pair of key vertices s and t in a loop, when edge t -> s exists, it calculates the max flow from s -> t.
        This is similar to a magnet, where the magnetic field outside corresponds to the max flow and the inner field
        corresponds to the direct edge.

        Networkx will return a residual network with flow[u][v] == -flow[v][u], but we will remove any negative and zero
        flows and replace the flow t -> s with just edge t -> s.

        This new graph can be seen as a redistribution of connection intensity, and can be used to do shortest path
        searches since it's identical in form with the input of the algorithm.

        :param s: the source of the max flow
        :param t: the sink of the max flow
        :return: a flow graph with 'weight' as its edge.
        """
        assert self.graph.has_edge(t, s), "the edge from t to s doesn't exist, loop can't be formed"
        flow = self.single_flow(s, t, rm_negative_and_zero=True)
        flow.add_edge(t, s, weight=self.graph[t][s]['weight'])
        return flow

    def merged_cycle_flow(self, axes: typing.Iterable, merge_func=np.sum):
        """
        compute multiple max flows along a cycle of key vertices, and merge the flows into one graph.

        The max flows used are rid of negative and zero flow weights. It's still possible that a single edge may encounter
        multiple positive flows, meaning some paths can be reused between different key vertices. Then it's necessary
        to determine how they are merged.

        :param axes: the key vertices.
        :param merge_func: how to merge multiple weights on a single edge. By default, they are summed.
        :return: a flow graph with 'weight' as its edge.
        """
        axes = list(axes)
        sg = nx.DiGraph()
        for k, v in self.cycle_flows(axes, rm_negative_and_zero=True).items():
            sg.add_weighted_edges_from([(u, v, d['weight']) for u, v, d in v.edges(data=True)], k)
        out = nx.DiGraph()
        out.add_weighted_edges_from([(u, v, merge_func(list(d.values()))) for u, v, d in sg.edges(data=True)])
        return out


class ShortestPathLoopSearch(GraphMaintainer):
    """
    Using networkx directed graph for implementing loop search algorithms based on shortest paths.

    As this method uses shortest paths, you should make sure the edge weights are meaningful so that a
    smaller weight means a stronger connection. The shortest path aggregates the weights along the path, so that
    summation is also meaningful.

    With this class, you can get loops in forms of exact lists of nodes along the loop.

    The shortest path algorithm uses the 'weight' attribute in the networkx graph.
    """

    def chain_screen(self, n_axis=2, top: int = None, must_include: typing.Iterable = None, allow_knots=False,
                     axis_pool: typing.Iterable = None, axis_must_include: typing.Iterable = None, priority=np.sum):
        """
        Using connected single source shortest paths to find loops. You should ensure that in your graph smaller edge
        weights means stronger connection for this method.

        First, use Bellman Ford to find the shortest paths between all regions. Then loops can be found by
        pairing any shortest paths like A -> B and B -> A. You can also find loops with more anchors' shortest path like A -> B,
        B -> C, C -> A, and even more. But with more anchors, the computation will be greatly slowed down, and number of
        discovery will be greatly expanded.

        When the search number is very great, you can use `top` to have an early stop. The shortest path are sorted such that a
        loop with minimal shortest path element will be retrieved first, but it won't guarantee the final loop will be ordered
        ascending. Besides, you can also set the must included nodes in the loop so that those without are skipped.

        The method attempts to located unique loops by the axes, i.e. one set of axes corresponding to one loop.
        It's likely that multiple axes can be connected in multiple ways, in which case once finding a shorter one a
        replacement will occur. The purpose is for balance between the uniqueness and computation.
        Since the shortest path will also be returned, you can check other connection ways easily.

        This can fail to give a loop between a set of axis, because there may be overlap between their shortest path, thus giving
        rise to smaller loops, whereas there may exist an exact loop that contain non shortest paths but unique vertices.
        Therefore, the shortest path from A to B here is better off interpreted as the most preferable path from A to B,
        which means other paths from A to B are not considered.

        :param n_axis: the number to consider for connecting shortest path into a loop. Larger n_axis will significantly
            increase the computation
        :param top: the most prominent results. This can speed up as it searches from the most probable loops and can
            have an early stop. Default as None to turn off.
        :param axis_pool: a list of vertices for axes to choose from, which can largely narrow down the search space.
            Default as None to turn off.
        :param must_include: the vertices that must appear in the search result.
        :param axis_must_include: the vertices that must appear in axes, and must be subset of `axis_pool`. This check
            is independent of `must_include`.
        :param allow_knots: whether to allow duplicate nodes (but not duplicated with axes).
        :param priority: the edge weight aggregation function for shortest path sorting. Default as sum, you can also use, for
        example, mean to make up for shortest path that travel through many vertices.
        :return: a dict of axis mapped to loop in the form of loops[(a,b,c)] -> [[a, ..., b], [b, ..., c], [c, ..., a]],
            where the key (a,b,c) is a sorted tuple of axes, doesn't necessarily mean a -> b -> c -> a,
            and shortest path in the form of sssp[from_node][to_node] -> [from_node, ..., to_node]
        """
        if must_include is not None:
            must_include =  set(must_include)
        if axis_must_include is not None:
            axis_must_include = set(axis_must_include)
            assert len(axis_must_include) <= n_axis, "number of must included axis is more than specified"
        if axis_pool is not None:
            axis_pool = set(axis_pool)
            assert len(axis_pool) >= n_axis, "size of axis pool is smaller than specified"
            if axis_must_include is not None:
                assert axis_must_include.issubset(axis_pool), "must included axis should be subset of axis pool"

        # bellman ford
        sssp = dict(nx.all_pairs_bellman_ford_path(self.graph))

        # do an edge sorting beforehand, ascending
        # vertices not in axis pool (if not None) will be omitted
        connection = []
        for k1, v1 in sssp.items():
            if axis_pool is not None and k1 not in axis_pool:
                continue
            for k2, v2 in v1.items():
                if axis_pool is not None and k2 not in axis_pool:
                    continue
                if k1 == k2:
                    continue
                w = []
                for i, j in itertools.pairwise(v2):
                    w.append(self.graph[i][j]['weight'])
                connection.append([k1, k2, priority(w)])
        connection.sort(key=lambda x: x[2])
        sorted_sssp = OrderedDict()
        # sorted_sssp[k1][k2] -> (length, list of vertices)
        # and k2 mapping is ordered
        for i, (k1, k2, w) in enumerate(connection):
            if k1 not in sorted_sssp:
                sorted_sssp[k1] = OrderedDict()
            sorted_sssp[k1][k2] = (w, sssp[k1][k2])

        max_iter = [0 if top is None else top]
        loops = {}

        def dfs_loop_search(loop: list, visited: set, length: float):
            # finishing, the last part of the cycle,
            if len(loop) == n_axis - 1:
                # check the existence of the last part
                k1 = loop[-1][-1]
                k2 = loop[0][0]
                if k1 not in sorted_sssp or k2 not in sorted_sssp[k1]:
                    yield
                last_part = sorted_sssp[k1][k2][1]

                # check knot
                sl = set(last_part[1:-1])
                new_visited = visited | sl
                if not allow_knots and len(new_visited) != len(visited) + len(last_part) - 2 or \
                        not sl.isdisjoint(i[0] for i in loop):
                    yield
                loop.append(last_part)
                length += sorted_sssp[k1][k2][0]
                axis = tuple(sorted(i[0] for i in loop))

                if (must_include is None or must_include.issubset(new_visited)) and \
                        (axis_must_include is None or axis_must_include.issubset(axis)):
                    if axis in loops:
                        # check if smaller than existed
                        if loops[axis]['length'] < length:
                            yield
                        else:
                            max_iter[0] += 1
                    max_iter[0] -= 1
                    loops[axis] = {
                        'loop': loop,
                        'length': length,
                    }
            # start
            elif len(loop) == 0:
                for k1, k2, w in connection:
                    v = sorted_sssp[k1][k2][1]
                    yield dfs_loop_search([v], set(v), w)
            else:
                k1 = loop[-1][-1]   # last axis
                for k, (w, c) in sorted_sssp[k1].items():
                    sc = set(c[1:])
                    new_visited = visited | sc
                    if len(new_visited) == len(visited) + len(c) - 1 or \
                            allow_knots and sc.isdisjoint(i[0] for i in loop):
                        yield dfs_loop_search(loop + [c], new_visited, length + w)
            yield

        gen = dfs_loop_search([], set(), 0)
        stk = []
        while top is None or max_iter[0] > 0:
            if isinstance(gen, typing.Generator):
                stk.append(gen)
                gen = next(gen)
            else:
                stk.pop()
                if not stk:
                    break
                gen = stk[-1].send(gen)

        return loops, deepcopy(sssp)

    def pair_complement(self, axis_pool: typing.Iterable = None):
        """
        Given a pair of vertices, the loop is defined as the direct connection between them plus the inverted shortest path.
        For example, with A and B, the loop can be either edge AB + the shortest path from B to A
        or edge BA + the shortest path from A to B. This comes in handy when shortest paths from A to B and B to A have
        intersection, leading to knots in a loop.

        This can also be much faster and doesn't need speedup or sorting.

        :param axis_pool: a list of vertices for axes to choose from, which can largely narrow down the search space.
            Default as None to turn off, and it will try every pair of vertices as long as there's a direct edge.
        :return: a dict of loops, keys are the direct edges and values are the corresponding inverse shortest path.
        """
        if axis_pool is not None:
            axis_pool = set(axis_pool)
        sssp = dict(nx.all_pairs_bellman_ford_path(self.graph))
        out = {}
        for fro, to in self.graph.edges:
            if axis_pool is not None and (fro not in axis_pool or to not in axis_pool) or to == fro:
                continue
            if to in sssp and fro in sssp[to]:
                out[(fro, to)] = sssp[to][fro]
        return out
