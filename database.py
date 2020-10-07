#!usr/bin/python
# -*- coding: utf-8 -*-


class Database(object):
    """Database class holding information about node/label relationships, mappings from nodes to images and from images to status."""

    def __init__(self, root_name="core"):
        """Constuctor for the Database class.

        Args:
            root_name (str, optional): Name given to the reference abstract category. Defaults to "core".
        """

        # Create the graph as a dict naming descendants of each node
        self.graph = {root_name: set()}
        # Mapping between each node/label and the images referencing it
        self.nodes_images = {root_name: set()}
        # Dict holding the current status of each image
        self.images_status = dict()

    def add_nodes(self, nodes):
        """Method to add nodes to the Database graph, given a parent-child relationship.

        Args:
            nodes (list): List of tuples describing nodes and their parent, to be added to the graph.
        """

        for (name, parent) in nodes:
            """Possible improvements here:
            - Introduce a hard check that each parent must exist
            - Pre-sort the node list for dependencies / find the source(s) node(s) + ordering in a DAG.
                e.g. [("core", None), ("A1", "A"), ("A", "core")] wouldn't be an issue.
            """
            
            # Notify the parent node that the granularity has changed
            self.notify_granularity(parent)

            # Notify sibling nodes (parent's other children) that the coverage has changed
            for sibling in self.graph[parent]:
                self.notify_coverage(sibling)

            # Formally add node to the graph (as itself + child of its parent) and create entry in mapping
            self.graph[parent].add(name)
            self.graph[name] = set()
            self.nodes_images[name] = set()

    def add_extract(self, images):
        """Method to add image labeling information in the Database.

        Args:
            images (dict): Mappings of each image to one or multiple labels/nodes.
        """

        for image, nodes in images.items():
            # Flag keeping track of whether the current image has referenced only known nodes so far.
            valid_nodes = True

            """Nested loop for this reason: we need to update the status of an image if it references an invalid node.
            Therefore we need to iterate both on images and nodes.
            """
            for node in nodes:
                """ From the description, it is not explicit whether invalid references to non-existent nodes should be kept. e.g. if `img003` references node `E` that is not in the graph, should this reference be kept in case node `E` is added later on.
                Here we choose not to keep it, however in the opposite case, we can easily move the content of the if-statement outside.
                """
                if node in self.graph:
                    self.nodes_images[node].add(image)
                else:
                    # Report that an invalid reference was found for this image
                    valid_nodes = False

            # Update the image status accordingly
            self.images_status[image] = "valid" if valid_nodes else "invalid"


    def get_extract_status(self):
        """Retrieve the status associated to each image, which was maintained on the fly as we updated the Database.

        Returns:
            [dict]: A dictionary of image names and their associated status.
        """

        return self.images_status

    def notify_granularity(self, node):
        """Helper method allowing to change the status of an image if there was an extension in granularity (only on valid images, no precendence over coverage changes).

        Args:
            node (string): Name of the node whose status needs an update
        """

        for image in self.nodes_images[node]:
            if self.images_status[image] == "valid":
                self.images_status[image] = "granularity_staged"


    def notify_coverage(self, node):
        """Helper method allowing to change the status of an image if there was an extension in coverage (only on valid images or images that have had their granularity changed).

        Args:
            node (string): Name of the node whose status needs an update
        """

        for image in self.nodes_images[node]:
            if self.images_status[image] in ["valid", "granularity_staged"]:
                self.images_status[image] = "coverage_staged"
