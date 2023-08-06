"""

This module contains all utilities associated with brain projects, so other modules can be used to do without coupling
the brain ontology.

The `CCFv3Ontology` is an example of how to derive an ontology.

`draw_loop_in_ccf` is a visualization based on the brainrender project, also a good example.
What is tricky is that this lib needs internet connection to download the atlas, and used some deprecated functions
by other libs, so it may not work well for first-time. You might need to modify the lib's code.
running.

"""
import itertools
import os
import typing
import networkx as nx

import pandas as pd
import numpy as np
from importlib_resources import files, as_file
from .packing import Ontology
from brainrender import Scene, settings
from myterial import grey, white, grey_dark
from vedo.shapes import Spline, Arrow, Tube, Line

import colorsys
import random
from brainrender._colors import map_color


with as_file(files('brain_loop_search') / 'structures.csv') as path:
    ccfv3 = pd.read_csv(path, index_col=1)


class CCFv3Ontology(Ontology):
    def __init__(self):
        """
        Use the already stashed ccfv3 structure table, containing the ID and acronym of each brain region.
        """
        super(Ontology, self).__init__()
        self._tree = ccfv3.copy()
        self._tree['parents'] = self._tree['structure_id_path']. \
            str.removeprefix('/').str.removesuffix('/').str.split('/')  # create ancestors as lists
        self._tree['parents'] = self._tree['parents'].apply(lambda x:[int(i) for i in x[:-1]])    # remove the last one(self)
        self._tree['depth'] = self._tree['parents'].apply(len)  # create depths
        self._find_children()
        self._leveling()

    def _find_children(self):
        self._tree['children'] = [[] for i in range(len(self._tree))]
        for ind, row in self._tree.iterrows():
            id = row['parent_structure_id']
            if not np.isnan(id):
                self._tree.at[id,'children'].append(ind)

    def _leveling(self):
        self._tree['level'] = 0
        for st in self._tree.index[self._tree['children'].apply(len) == 0]:
            par = self._tree.at[st, 'parent_structure_id']
            count = 1
            while par in self._tree.index and self._tree.at[par, 'level'] < count:
                self._tree.at[par, 'level'] = count
                par = self._tree.at[par, 'parent_structure_id']
                count += 1

    def check_include(self, vert: typing.Iterable):
        return set(vert).issubset(self._tree.index)

    def levels_of(self, vert: typing.Iterable) -> pd.Series:
        return self._tree.loc[vert, 'level']

    def depths_of(self, vert: typing.Iterable) -> pd.Series:
        return self._tree.loc[vert, 'depth']

    def ancestors_of(self, vert: typing.Iterable) -> pd.Series:
        return self._tree.loc[vert, 'parents']

    def immediate_children_of(self, vert: typing.Iterable) -> pd.Series:
        return self._tree.loc[vert, 'children']


def draw_brain_graph(graph: nx.DiGraph, path: str | os.PathLike, thr: float = 0, render_ops: dict = None, cmap='jet'):
    """
    Plot a directed graph among ccfv3 brain structures.

    Note: It will reset some of the brainrender global settings.

    Using brainrender can cause some problem, as it
    will attempt downloading the brain atlas from the internet and ping google.com beforehand.

    If you are not connected, it will fail.

    One solution to do this is to remove the ping in the package source. If the downloading is too slow,
    you can manually download it from their website and decompress it into the package's storage directory, usually set
    in `$HOME/.brainglobe`. Anyway, you can hack into their code to see it for yourself.

    Another problem I found with brainrender is that it uses numpy's deprecated features, you might need to
    refactor the lib source until it passes.

    :param graph: a list of shortest paths consisting of brain structure IDs. Each sublist will be assigned a different
    random color. You need to make sure the heads and tails are repeated in adjacent lists.
    :param path: screenshot save path.
    :param thr: only edge weights over this will be plotted.
    :param render_ops: render options. Default is None to use the default options, see the code.
    :param cmap: matplotlib colormap.
    """
    if render_ops is None:
        render_ops = {
            'interactive': False,
            'camera': {
                'pos': (4811, 3225, -42167),
                'viewup': (0, -1, 0),
                'clippingRange': (24770, 51413),
                'focalPoint': (7252, 4096, -5657),
                'distance': 36602
            },
            'zoom': 2
        }
    settings.SHOW_AXES = False
    settings.SHADER_STYLE = "cartoon"
    settings.ROOT_ALPHA = .05
    settings.ROOT_COLOR = grey
    settings.BACKGROUND_COLOR = white

    scene = Scene(atlas_name='allen_mouse_100um')

    regions = list(graph.nodes)
    regions = ccfv3.loc[regions, 'acronym']
    scene.add_brain_region(*list(regions), alpha=.02, hemisphere='left', silhouette=True)
    e = graph.edges(data=True)
    data = [d['weight'] for u, v, d in e if u != v]
    vmax, vmin = max(data), min(data)

    # change silhouette
    for i in scene.get_actors(br_class="brain region"):
        i._silhouette_kwargs['lw'] = 1
        i._silhouette_kwargs['color'] = grey_dark

    rt = scene.get_actors(br_class="brain region", name="root")[0]
    rt._silhouette_kwargs['lw'] = 1
    rt._silhouette_kwargs['color'] = grey

    for u, v, d in e:
        if u == v or d['weight'] < thr:
            continue
        # tube
        # get a proper center of each region (this is difficult, for brain structures can be very twisted)
        # then connect them to make a spline for a tube, which will envelop arrows
        actors = scene.get_actors(br_class="brain region", name=list(regions.loc[[u, v]]))
        z_mean = [np.mean(m.points()[:, 2]) for m in actors]
        centers = [np.mean(m.points()[m.points()[:, 2] - z < 10], axis=0) * (1, 1, -1) for m, z in zip(actors, z_mean)]
        spl = Line(*centers, res=3)
        pts = spl.points()
        c = map_color(d['weight'], cmap, vmin, vmax)
        feint = list(colorsys.rgb_to_hsv(*c))
        feint[1] /= 2
        feint = colorsys.hsv_to_rgb(*feint)

        rr = 1 + (d['weight'] - vmin) / (vmax - vmin)
        radius = [(np.linalg.norm(i - centers[0]) + np.linalg.norm(i - centers[-1])) / 20 * rr for i in pts]
        scene.add(Tube(pts, radius, c=feint, alpha=0.2))

        # arrows
        scene.add(*[Arrow(*i, c=c, s=rr*3) for i in itertools.pairwise(pts)])

    scene.render(**render_ops)
    scene.screenshot(str(path))
    scene.close()

def draw_single_loop(loop: list[list], path: str | os.PathLike, render_ops: dict = None):
    """
    Plot one loop in the ccfv3 atlas using brainrender.

    Note: It will reset some of the brainrender global settings.

    Using brainrender can cause some problem, as it
    will attempt downloading the brain atlas from the internet and ping google.com beforehand.

    If you are not connected, it will fail.

    One solution to do this is to remove the ping in the package source. If the downloading is too slow,
    you can manually download it from their website and decompress it into the package's storage directory, usually set
    in `$HOME/.brainglobe`. Anyway, you can hack into their code to see it for yourself.

    Another problem I found with brainrender is that it uses numpy's deprecated features, you might need to
    refactor the lib source until it passes.

    :param loop: a list of shortest paths consisting of brain structure IDs. Each sublist will be assigned a different
    random color. You need to make sure the heads and tails are repeated in adjacent lists.
    :param path: screenshot save path.
    :param render_ops: render options. Default is None to use the default options, see the code.
    """
    if render_ops is None:
        render_ops = {
            'interactive': False,
            'camera': {
                'pos': (4811, 3225, -42167),
                'viewup': (0, -1, 0),
                'clippingRange': (24770, 51413),
                'focalPoint': (7252, 4096, -5657),
                'distance': 36602
            },
            'zoom': 2
        }
    settings.SHOW_AXES = False
    settings.SHADER_STYLE = "cartoon"
    settings.ROOT_ALPHA = .05
    settings.ROOT_COLOR = grey
    settings.BACKGROUND_COLOR = white

    scene = Scene(atlas_name='allen_mouse_100um')
    count = 0

    # the root brain (usually this is just a background and not used to plot loops)
    rt = scene.get_actors(br_class="brain region", name="root")[0]
    rt._silhouette_kwargs['lw'] = 1
    rt._silhouette_kwargs['color'] = grey

    for run in loop:    # each run in a loop is one sssp, will be marked by different colors
        # map to ccf acronym
        run = list(ccfv3.loc[run, 'acronym'])

        # all traversed brain structures but the first and last one (axes)
        scene.add_brain_region(*run[1:-1], alpha=.2, hemisphere='left', silhouette=False)

        # axis regions will add silhouette, and bigger alpha
        scene.add_brain_region(run[0], run[-1], alpha=.5, hemisphere='left', silhouette=False)
        scene.add_silhouette(*scene.get_actors(br_class="brain region", name=[run[0], run[-1]]), lw=2)

        # random hue
        hue = random.random()

        # tube
        # get a proper center of each region (this is difficult, for brain structures can be very twisted)
        # then connect them to make a spline for a tube, which will envelop arrows
        actors = scene.get_actors(br_class="brain region", name=run)
        z_mean = [np.mean(m.points()[:, 2]) for m in actors]
        centers = [np.mean(m.points()[m.points()[:, 2] - z < 10], axis=0) * (1, 1, -1) for m, z in zip(actors, z_mean)]
        if len(centers) < 3:
            spl = Line(*centers, res=20)
        else:
            spl = Spline(centers)
        pts = spl.points()
        radius = [(np.linalg.norm(i - centers[0]) + np.linalg.norm(i - centers[-1])) / 100 for i in pts]
        scene.add(Tube(pts, radius, c=colorsys.hsv_to_rgb(hue, .5, .9), alpha=0.2))

        # arrows
        scene.add(*[Arrow(*i, c=colorsys.hsv_to_rgb(hue, .9, .9)) for i in itertools.pairwise(pts)])

        # text
        for i in range(len(run) - 1):
            count += 1
            actors[i].caption(f'{count + 1}. {run[i]}', centers[i] * (1, 1, -1), (.04, .04))

    scene.render(**render_ops)
    scene.screenshot(str(path))
    scene.close()
