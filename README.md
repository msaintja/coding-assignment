# Coding assignment - Proposal details

This is my solution proposal for the coding assignment from Foodvisor. The original description can be found [here](https://github.com/Foodvisor/coding-assignment/blob/master/README.md).

---
Quick jump to:
- [Design and implementation choices](#design-and-implementation-choices)
- [Running the code/tests](#running-the-code/tests)
- [Credits](#credits)

---

## Design and implementation choices

### Observations
First, here are a few observations:

1. Reading the description, there are two key events in this system, which occur when we insert a node in the graph:
    - we need to change the status of the images linked to the **parent** of this node, and
    - we change the status of the images linked to the **siblings** (i.e. other children of the parent) of this node.

2. In this situation, since inserts into the graph are performed in order (top to bottom / root to the innermost leaves), then we only need to consider direct descendants and parents rather than all predecessors and successors.

### Node relationships: descendants view vs. parents view
In order to encode the relationships between nodes in the graph, we may have two views of the problem: 
- either to build a set of descendants, for each node (descendants view)
- or to build a dictionary/lookup table indicating the parent of each node (parents view).

While the second option may seem more natural, or in phase with the way the data is given as input (lists of nodes and their parent), I chose to implement the first option. It makes more sense considering the events we have to implement described in *1.* above. 

Consider the following time complexities table:

| Operation \ Design 	| Descendants view                                              	| Parents view 	|
|--------------------	|---------------------------------------------------------------	|--------------	|
| Retrieve parent    	| O(1)                                                          	| O(1)         	|
| Retrieve siblings  	| [O(1) avg.](https://wiki.python.org/moin/TimeComplexity#dict) 	| O(n) exact   	|

Retrieving the parent of a node is cheap in both cases, especially since we get this information from the input tuples. With the descendants view, we only need to find the value associated to the parent key in a dict - which has an average time complexity of O(1) to get back a set of all siblings. Conversely, with the parents view, we would need to test for each of the nodes we have whether their parent is the target parent, costing us an exact O(n) time.

Alternatively, we could build more elaborate data structures (e.g. a Node object) containing information both on parents and descendants, but this didn't seem necesary here as we have very few properties to keep track of. So I don't think it warrants the extra cost of having to maintain multiple/symmetrical "copies" of the same information when a single dict of strings + sets of strings work.

### Stucture for images information

We are once again confronted with the choice of a data structure to store information about the images.

First, let's note that with `get_extract_status()`, we need to retrieve information about all images anyways.

Also, let us consider that having a mapping from images to nodes (in a similar form to the input we're given) would be expensive because we need to update the images' status based on node information (and not the other way around). In this situation, when we would want to perform an update, we would need to iterate over all **existing** images to find the relevant nodes (parents/siblings), costing us a hefty O(n·m) time complexity - n and m being the number of nodes and images, respectively.

My proposed solution is to handle two mappings, one from nodes their associated set of images, and the other from images to their status.  
We incur a higher time complexity when calling `add_extract()`, as we will need to iterate through all **new** nodes and images. We need this nested loop in O(n'·m') time complexity because we need to check that all nodes are valid (here, n' and m' being the number of **new** nodes and images, respectively).  
However, the update here is cheaper since we directly know with the mapping which images need a status update for a target node.

### Case of invalid information

From the description, it is not explicit whether invalid references to non-existent nodes should be kept. e.g. if `img003` references node `E` that is not in the graph, should this reference be kept in case node `E` is added later on.

Here we choose not to keep the information linking images to invalid nodes, however if this is not the intended behavior, or if requirements change, it would be easy to adapt the code to keep adding references to these invalid nodes and update the associated images' status should this invalid node be added later.

### Possible improvements, concerns

#### Root node
The original description mentions building the reference abstract category in the constructor,
>"A reference abstract category (named core in the following examples) will need to be created in your constructor"

with test cases adding this same "core" node *a posteriori* - but is handled separately. The description for the `add_nodes()` method suggest that it is that method's responsibility rather than the constructor's to build the root node.

>"If the parent node is None, this operation should be conducted first and will define the root node"

Here, I left it as it was presented in test cases - built in constructor and with the rest of the list passed to `add_nodes()`.

#### Other improvements

A great number of improvements can be added to this code. As they were not the object of the presented test cases, I did not implement all of them considering they may or may not be relevant nor useful depending on the used datasets/nodes/images. Here is a non-exhaustive list:
- Introduce a hard check that each parent must exist when adding nodes.
- Pre-sort the node list for dependencies / find the source(s) node(s) + ordering in a DAG. e.g. [("core", None), ("A1", "A"), ("A", "core")] wouldn't be an issue.
- Forbid the addition of nodes with existing names.
- Forbid the addition of nodes with a `None` parent if one was already added.
- Forbid the addition of images with existing names, or merge these objects to keep labels/nodes of both.
- etc.

---

## Running the code/tests
 
### Environment and setup

This code was tested using Python 3.7.5 and pytest 1.6.1 on Linux.  
YMMV - trying to run the code on Windows may show you an unrelated warning such as [this one](https://github.com/pyreadline/pyreadline/issues/65), depending on your existing environment.  

You may install pytest directly, or use the supplied `requirements.txt` file.  
For example, with `pip`※:
```
pip install -r requirements.txt
```

You can also run this within a virtual env or conda environment.

If you want to use pytest (recommended) and run all test cases, please make sure that `expected_status.json`, `graph_build.json`, `graph_edits.json` and `img_extract.json` from the [original release attachments](https://github.com/msaintja/coding-assignment/releases/tag/v0.1.0) are correctly located in the `tests/` directory.

### Execution
You may import the `Database` class directly within the python interpreter, or a standalone script.

Using pytest, you may check that all test cases from the original description have the intended output by running※:
```
python -m pytest
```
which should confirm that the tests passed.

### Note
※ Please make sure you're running the commands in the base `coding-assignment` directory.

---
## Credits

The tests written and found in the `tests/` directory are all test cases described in the [original description](https://github.com/Foodvisor/coding-assignment/blob/master/README.md). 

The tests rely on the `pytest` library, distributed by Holger Krekel et al. under MIT licence. [[PyPI](https://pypi.org/project/pytest/), [GitHub](https://docs.pytest.org/en/latest/), [Documentation](https://docs.pytest.org/en/latest/)]
