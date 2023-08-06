# Brain Loop Search
Tools for screening significant loop structures in a graph, typically a
brain structure graph with physiological or anatomical edge data.

## Installation

```shell
$ pip install brain-loop-search
```

## Usage

### Packing a bigger graph for regions of interest
Packing vertices:
```python
import brain_loop_search as bls

vertices = [322, 329, 981, 337, 453, 8, 1070] # ccf brain id

# ccf ontology
ontology = bls.brain_utils.CCFv3Ontology()

vp = bls.packing.VertexPacker(vertices, ontology)
# filtering by level
vp.filter_by_level(fro=1, to=2)
```
Packing a graph:
```python
import brain_loop_search as bls
import pandas as pd
import numpy as np

vertices = [322, 329, 981, 337, 453, 1070, 345, 353, 361] # ccf brain id

# adjacent matrix
adj_mat = pd.DataFrame(np.array([
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

# ccf ontology
ontology = bls.brain_utils.CCFv3Ontology()

# packing
new_rows = [322]
new_cols = [337, 329, 353]
graph_packer = bls.packing.GraphPacker(adj_mat, ontology)
new_mat = graph_packer.pack(new_rows, new_cols, def_val=0, superior_as_complement=True, aggr_func=np.sum)
```
### Shortest Path Loop Search

Screen simple loops from the graph.

```python
import brain_loop_search as bls
import pandas as pd

edges = pd.DataFrame({
            "a": [1, 2, 3, 4, 5],
            "b": [4, -1, -1, 1, -1],
            "c": [5, 6, 7, 8, 9],
            "d": [-1, 2, 3, 1, 2],
            "e": [-1, -1, -1, -1, -1]
        }, index=["a", "b", "c", "d", "e"])

g = bls.search.ShortestPathLoopSearch()
g.add_subgraph(edges)

# search by single shortest path with a reverse edge
loops = g.pair_complement(axis_pool=['a', 'b', 'c'])
# search by chaining 3 of the shortest paths found
loops, sssp = g.chain_screen(n_axis=3)
```

### Max Flow Loop Search

Generate a new graph of potentially integrated loops.

```python
import brain_loop_search as bls
import pandas as pd

edges = pd.DataFrame({
            "a": [1, 2, 3, 4, 5],
            "b": [4, -1, -1, 1, -1],
            "c": [5, 6, 7, 8, 9],
            "d": [-1, 2, 3, 1, 2],
            "e": [-1, -1, -1, -1, -1]
        }, index=["a", "b", "c", "d", "e"])

g = bls.search.ShortestPathLoopSearch()
g.add_subgraph(edges)

# find a single max flow with a reverse edge (like a magnet field)
new_g = g.magnet_flow(s='b', t='a')
# find cycled max flows and merge them into a new graph
new_g = g.merged_cycle_flow(axes=['b', 'c', 'a'])
```

### Visualization

Visualize a single loop

```python
import brain_loop_search as bls

# a loop is a list of list, with the head and tail of the sublist as axes
# here are some random picked brain regions
loop = [[950, 974, 417], [417, 993], [993, 234, 289, 950]]
bls.brain_utils.draw_single_loop(loop, 'test.png')
```
Figure:
![](https://raw.githubusercontent.com/SEU-ALLEN-codebase/brain-loop-search/main/test/test.png)

Visualize a graph

```python
import numpy as np
import pandas as pd
import brain_loop_search as bls
vertices = [322, 329, 981, 337, 453, 1070, 345, 353, 361]
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
g = bls.search.GraphMaintainer()
g.add_subgraph(adj_mat)
bls.brain_utils.draw_brain_graph(g.graph, 'test2.png', thr=3)
```

Figure:
![](https://raw.githubusercontent.com/SEU-ALLEN-codebase/brain-loop-search/main/test/test2.png)


## Useful Links

Github project: https://github.com/SEU-ALLEN-codebase/brain-loop-search

Documentation: https://SEU-ALLEN-codebase.github.io/brain-loop-search