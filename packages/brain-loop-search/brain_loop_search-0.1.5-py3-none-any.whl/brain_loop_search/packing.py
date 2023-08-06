"""
This module contains the classes that can be used to commit any task of packing a graph, i.e. reduce the undesired
vertices based on a set of rules and an ontology tree that describe the affiliation among the vertices.
"""
import typing

import numpy as np
import pandas as pd


class Ontology:
    """
    The prior knowledge about tree relationship among the vertices in graph, namely ontology, used for packing graph
    vertices.
This is a meta class that doesn't implement any function, so any subclass this with the same functions can use it
    with other modules smoothly.

    I used this as an abstract interface and make derivation for ccfv3 ontology in brain.
    You can follow my subclass for your own.

    I would recommend using pandas for tree representation for its speed and also because you can save some useful info
    as appended columns.
    """

    def __init__(self):
        """
        Here, some preprocessing can be done make other functions easier and faster to operate. Also, you need to
        ensure that this is actually a tree.
        """
        pass

    def check_include(self, vert: typing.Iterable):
        """
        check if the vertices given is included
        :param vert: the vertices to check
        :return: True or False.
        """
        pass

    def levels_of(self, vert: typing.Iterable) -> pd.Series:
        """
        Level is defined as the largest count from the current node to its leaves in the tree, starting from 0.
        :param vert: the vertices to check
        :return: the levels of each vertex in the ontology
        """
        pass

    def depths_of(self, vert: typing.Iterable) -> pd.Series:
        """
        Depth is defined as the count from the current node to its root in the tree, starting from 0.
        :param vert: the vertices to check
        :return: the depths of each vertex in the ontology
        """
        pass

    def ancestors_of(self, vert: typing.Iterable) -> pd.Series:
        """
        The parents of each vertex as a list, starting from the tree root to its immediate parent, the length of which
        equals the depth.

        :param vert: the vertices to check
        :return: the lists of parents of each vertex in the ontology
        """
        pass

    def immediate_children_of(self, vert: typing.Iterable) -> pd.Series:
        """
        The immediate children of each vertex as a list, starting from the tree root to its direct parent.

        :param vert: the vertices to check
        :return: the lists of children of each vertex in the ontology
        """


class VertexPacker:
    """
    Given a set of vertices in a graph, e.g. brain structures in a macroscopic brain connectome,
    rearrange them by filtering and merging into a new set, based on a filtering rule and according
    to an ontology.

    This is the precursor step before packing the whole graph. A directed graph may not share its rows
    with columns, so this might need to be done once for each, even with different rules.

    Also, for a complexed graph, where you may expect heterogeneous level hierarchies, you can pack the graph multiple
    times, and their vertices apply different rules naturally. This way, you'll also utilize this decoupled facility.

    This class uses a state machine functionality, by which each time you trigger the alteration each the
    stash changes. When you need a diversion or something you can retrieve the intermediate result and start anew.
    """

    def __init__(self, vertices: typing.Iterable, ontology: Ontology):
        """
        Initialize the vertex packer with an initial set of vertices and ontology. It also checks the viability of
        the vertices.

        :param vertices: a set of entities in the ontology to filter and merge.
        :param ontology: a derivation of the abstract class `Ontology`.
        """
        vertices = pd.Series(vertices)
        assert ontology.check_include(vertices), f"vertices contain unrecognizable ID "
        self._vert = vertices
        self._ont = ontology

    def stash(self):
        """
        For retrieving the intermediate or final results. To remove mutability, it's turned to tuple. If you need a
        diversion of processing, you can retrieve the intermediate result and make a new pathway.

        :return: the stashed vertices' copy as a numpy array.
        """
        return self._vert.copy()

    def filter_by_level(self, fro: int = None, to: int = None, invert=False):
        """
        Only retain the vertices within the level range, c style.

        Levels are the max count from the current node to its leaves in the tree, staring from 0.

        :param fro: the starting level, inclusive, default as None, meaning no limit.
        :param to: the ending level, exclusive, default as None, meaning no limit.
        :param invert: whether retain the otherwise non-descendents
        """
        levels = self._ont.levels_of(self._vert)
        if fro is not None:
            levels = levels[levels >= fro]
        if to is not None:
            levels = levels[levels < to]
        if invert:
            self._vert = self._vert[~self._vert.isin(levels.index)]
        else:
            self._vert = levels.index

    def filter_by_depth(self, fro: int = None, to: int = None, invert=False):
        """
        Only retain the vertices within the depth range, c style.

        Depths are the count from the current node to its root in the tree, staring from 0.

        :param fro: the starting depth, inclusive, default as None, meaning no limit.
        :param to: the ending depth, exclusive, default as None, meaning no limit.
        :param invert: whether retain the otherwise non-descendents
        """
        depths = self._ont.depths_of(self._vert)
        if fro is not None:
            depths = depths[depths >= fro]
        if to is not None:
            depths = depths[depths < to]
        if invert:
            self._vert = self._vert[~self._vert.isin(depths.index)]
        else:
            self._vert = depths.index

    def filter_super(self):
        """
        Remove any vertices that happen to be the ancestor of another.
        """
        un = set.union(*map(set, self._ont.ancestors_of(self._vert)))
        self._vert = self._vert[~self._vert.isin(un)]

    def filter_sub(self):
        """
        Remove any vertices that happen to be the descendent of another.
        """
        vert = set(self._vert)
        tf = [vert.isdisjoint(i) for i in self._ont.ancestors_of(self._vert)]
        self._vert = self._vert[tf]

    def filter_by_immediate_child_of(self, parents: typing.Iterable, invert=False):
        """
        Only retain the direct children under some vertices, which is convenient when you have a big super node with
        many branches below.

        :param parents: the direct parent vertices.
        :param invert: whether retain the otherwise non-descendents
        """
        un = set.union(*map(set, self._ont.immediate_children_of(parents)))
        if invert:
            self._vert = self._vert[~self._vert.isin(un)]
        else:
            self._vert = self._vert[self._vert.isin(un)]

    def filter_by_descendants_of(self, parents: typing.Iterable, include_parents=False, invert=False):
        """
        Only retain the descendents of some vertices.

        :param parents: the ancestors.
        :param include_parents: whether to allow the parents to exist in the result, default as not.
        :param invert: whether retain the otherwise non-descendents
        """
        parents = set(parents)
        tf = map(lambda p: not parents.isdisjoint(p), self._ont.ancestors_of(self._vert))
        if include_parents:
            tf = [*tf] | self._vert.isin(parents)
        if invert:
            tf = [not i for i in tf]
        self._vert = self._vert[tf]

    def merge_by_level(self, thr):
        """
        Merge the vertices until they are all above the min level or no merge can be done.

        Levels are the max count from the current node to its leaves in the tree, staring from 0.

        :param thr: the min level.
        """
        vert = set()
        for i, p, l in zip(self._vert, self._ont.ancestors_of(self._vert), self._ont.levels_of(self._vert)):
            if l < thr:
                vert.add(p[l - thr])
            else:
                vert.add(i)
        self._vert = pd.Series(list(vert))

    def merge_by_depth(self, thr):
        """
        Merge the vertice until they are all below the max depth or no merge can be done.

        Depths are the count from the current node to its root in the tree, staring from 0.

        :param thr: the max depth.
        """
        vert = set()
        for i, p in zip(self._vert, self._ont.ancestors_of(self._vert)):
            if len(p) > thr:
                vert.add(p[thr])
            else:
                vert.add(i)
        self._vert = pd.Series(list(vert))


class GraphPacker:
    """
    Given a directed graph (in adjacent matrix form), according to an ontology,
    rearrange as a new graph with superior structures or just merge redundant edges. The projection is from
    rows to columns

    Taking brain graph as an example, a group of neurons project from regions to regions,
    meaning edge (a, b) can have redundant occurrences with different weights. This is where merging needs to be done.

    Sometimes, you want to look into their coarser regions' relations rather than the finer ones. This is where
    rearrangement needs to be done.
    """

    def __init__(self, adj_mat: pd.DataFrame, ontology: Ontology):
        """
        :param adj_mat: the adjacent matrix in pandas dataframe, the projection is from rows to columns.
        :param ontology: a derivation of the abstract class `Ontology`.
        """
        # check adjacent matrix
        assert ontology.check_include(adj_mat.index), f"rows contain unrecognizable ID"
        assert ontology.check_include(adj_mat.columns), f"columns contain unrecognizable ID"
        self._mat = adj_mat.to_numpy()
        self._rows = adj_mat.index
        self._cols = adj_mat.columns
        self._ont = ontology

    def pack(self, new_rows: typing.Iterable, new_cols: typing.Iterable, def_val: float = -1,
             superior_as_complement: bool = False, aggr_func=lambda x: 1 / (1 / x).sum()):
        """
        Specifying new rows and columns (usually generated by feeding the original to VertexPacker, but you can
        provide your own list, long as it's within the ontology),
        retrieve a new graph in adjacent matrix.

        Packing usually involves merging redundant edges or edges inferior to a superior one. Sometimes, conflicts can
        take place where the superior edge and inferior edge coexist. Normally this is an undefined behavior, but
        considering in some ontology assignment, areas where the inferior don't cover in the superior, namely,
        for set A containing set B and set C, A - (B|C) can be represented using the superior. So here, by turning this
        on, you can always merge them. Otherwise, merge is done only for mutually excluded vertices.

        :param new_rows: the new 'project from' vertices.
        :param new_cols: the new 'project to' vertices.
        :param def_val: the default value for non-connecting edges.
        :param superior_as_complement: do merge for both superior and inferior vertices when encountered,
            default as False.
        :param aggr_func: the aggregation function.
        :return: a new adjacent matrix as pandas dataframe.
        """
        new_rows = pd.Series(new_rows)
        new_cols = pd.Series(new_cols)
        assert new_rows.is_unique, "new row items are not unique"
        assert new_cols.is_unique, "new column items are not unique"

        new_mat = np.ones([len(new_rows), len(new_cols)]) * def_val

        def vertex_map_gen(all_vert, new_vert):
            # prefilter
            packer = VertexPacker(all_vert.unique(), self._ont)
            packer.filter_by_descendants_of(new_vert, include_parents=True)
            needed_vert = packer.stash()
            # map
            map = []
            for v in new_vert:
                packer = VertexPacker(needed_vert, self._ont)
                packer.filter_by_descendants_of([v], include_parents=True)
                nodes = packer.stash()
                if not superior_as_complement:  # filter the sub nodes in this mode
                    packer = VertexPacker(nodes, self._ont)
                    packer.filter_sub()
                    nodes = packer.stash()
                map.append(np.where(all_vert.isin(nodes)))
            return map

        row_map = vertex_map_gen(self._rows, new_rows)
        col_map = vertex_map_gen(self._cols, new_cols)

        # calculate the edges in the new matrix
        for i, (row, fro_ind) in enumerate(zip(new_rows, row_map)):
            if len(fro_ind) == 0:
                continue
            for j, (col, to_ind) in enumerate(zip(new_cols, col_map)):
                if row == col or len(to_ind) == 0:
                    continue
                dat = self._mat[fro_ind][:,to_ind].reshape(-1)
                dat = dat[dat != def_val]
                if len(dat) == 0:
                    continue
                new_mat[i, j] = aggr_func(dat)
        return pd.DataFrame(new_mat, index=new_rows, columns=new_cols)
