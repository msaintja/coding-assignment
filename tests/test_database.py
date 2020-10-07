"""File hosting the TestDatabase class, for pytest."""

import os
import json
import pytest
from database import Database


class TestDatabase:
    """Associated test class for the Database class.
    Follows the pytest convention for automatic testing.
    """

    def perform_db_operations(self, build, extract, edits):
        """Factored code to perform a set of operations on an instance of the Database class. Code adapted from https://github.com/Foodvisor/coding-assignment/blob/master/README.md

        Args:
            build (list): List of tuples corresponding to nodes and their respective parent.
            extract (dict): Dictionary mapping image names to their corresponding classes/nodes (in a list).
            edits (list): List of tuples, corresponding to additional nodes and parents.

        Returns:
            [dict]: A dictionary of image names and their associated status.
        """

        status = {}

        if len(build) > 0:
            # Build graph
            db = Database(build[0][0])
            if len(build) > 1:
                db.add_nodes(build[1:])
            # Add extract
            db.add_extract(extract)
            # Graph edits
            db.add_nodes(edits)
            # Update status
            status = db.get_extract_status()

        return status


    def test_simple_1(self):
        """First simple test case, illustrating how `granularity_staged` is used."""

        # Initial graph
        build = [("core", None), ("A", "core"), ("B", "core"), ("C", "core"), ("C1", "C")]
        # Extract
        extract = {"img001": ["A"], "img002": ["C1"]}
        # Graph edits
        edits = [("A1", "A"), ("A2", "A")]

        status = self.perform_db_operations(build, extract, edits)

        assert status == {"img001": "granularity_staged", "img002": "valid"}

    def test_simple_2(self):
        """Second simple test case, illustrating the precendence of `coverage_staged` over `granularity_staged` and the `invalid` status."""

        # Initial graph
        build = [("core", None), ("A", "core"), ("B", "core"), ("C", "core"), ("C1", "C")]
        # Extract
        extract = {"img001": ["A", "B"], "img002": ["A", "C1"], "img003": ["B", "E"]}
        # Graph edits
        edits = [("A1", "A"), ("A2", "A"), ("C2", "C")]

        status = self.perform_db_operations(build, extract, edits)

        assert status == {"img001": "granularity_staged", "img002": "coverage_staged", "img003": "invalid"}


    def test_release(self):
        """Test case using the JSON files from the release attachments (https://github.com/msaintja/coding-assignment/releases/tag/v0.1.0). Shows how this system can be applied to larger datasets."""

        # Set of required files
        required_files = {"expected_status.json", "graph_build.json", "graph_edits.json", "img_extract.json"}

        # Check that all files are present
        assert required_files.issubset(set(os.listdir("tests"))), \
        f"Missing one or more of the following files in the ./tests/ directory: {required_files}.\n" + \
        "Please download them from the releases at https://github.com/msaintja/coding-assignment/releases/tag/v0.1.0"


        # Open JSON files and load them into variables
        with open("tests/expected_status.json") as f:
            expected_status = json.load(f)

        with open("tests/graph_build.json") as f:
            build = json.load(f)

        with open("tests/graph_edits.json") as f:
            edits = json.load(f)

        with open("tests/img_extract.json") as f:
            extract = json.load(f)

        status = self.perform_db_operations(build, extract, edits)

        # Check that we get our expected output
        assert status == expected_status
