# tests/test_visualizer.py

import unittest
from anytree import Node
from visualizer import Visualizer
import pandas as pd

class TestVisualizer(unittest.TestCase):
    def setUp(self):
        # Create a sample tree with unique node names
        self.root = Node("Finance", description="Finance industry hierarchy", processed=False)
        self.banking = Node("Banking", parent=self.root, description="Banking sector", processed=False)
        self.retail_banking = Node("Retail Banking", parent=self.banking, description="Services for individual consumers", processed=False)
        self.corporate_banking = Node("Corporate Banking", parent=self.banking, description="Services for businesses", processed=False)
        self.investment = Node("Investment", parent=self.root, description="Investment services", processed=False)
        self.asset_management = Node("Asset Management", parent=self.investment, description="Managing client assets", processed=False)
        self.investment_banking = Node("Investment Banking", parent=self.investment, description="Advisory and capital raising", processed=False)
        self.visualizer = Visualizer()

    def test_prepare_dataframe(self):
        """
        Test that prepare_dataframe correctly converts the AnyTree structure to a DataFrame.
        """
        df = self.visualizer.prepare_dataframe(self.root)
        expected_data = [
            {"Name": "Finance", "Description": "Finance industry hierarchy", "Processed": False, "Path": "Finance"},
            {"Name": "Banking", "Description": "Banking sector", "Processed": False, "Path": "Finance / Banking"},
            {"Name": "Retail Banking", "Description": "Services for individual consumers", "Processed": False, "Path": "Finance / Banking / Retail Banking"},
            {"Name": "Corporate Banking", "Description": "Services for businesses", "Processed": False, "Path": "Finance / Banking / Corporate Banking"},
            {"Name": "Investment", "Description": "Investment services", "Processed": False, "Path": "Finance / Investment"},
            {"Name": "Asset Management", "Description": "Managing client assets", "Processed": False, "Path": "Finance / Investment / Asset Management"},
            {"Name": "Investment Banking", "Description": "Advisory and capital raising", "Processed": False, "Path": "Finance / Investment / Investment Banking"},
        ]
        expected_df = pd.DataFrame(expected_data)
        # Reset index to ensure alignment
        pd.testing.assert_frame_equal(df.reset_index(drop=True), expected_df)

    def test_find_node_by_name_exists(self):
        """
        Test that find_node_by_name returns the correct node when it exists.
        """
        node = self.visualizer.find_node_by_name(self.root, "Retail Banking")
        self.assertIsNotNone(node)
        self.assertEqual(node.description, "Services for individual consumers")
        self.assertFalse(node.processed)

    def test_find_node_by_name_not_exists(self):
        """
        Test that find_node_by_name returns None when the node does not exist.
        """
        node = self.visualizer.find_node_by_name(self.root, "NonExistent Node")
        self.assertIsNone(node)

    # Removed the following test as prepare_tree_dict no longer exists
    # def test_prepare_tree_dict(self):
    #     expected_dict = {
    #         "name": "Finance",
    #         "children": [
    #             {
    #                 "name": "Banking",
    #                 "children": [
    #                     {"name": "Retail Banking", "children": []},
    #                     {"name": "Corporate Banking", "children": []}
    #                 ]
    #             },
    #             {
    #                 "name": "Investment",
    #                 "children": [
    #                     {"name": "Asset Management", "children": []},
    #                     {"name": "Investment Banking", "children": []}
    #                 ]
    #             }
    #         ]
    #     }
    #     result = self.visualizer.prepare_tree_dict(self.root)
    #     self.assertEqual(result, expected_dict)

    def test_display_hierarchy_runs_without_exception(self):
        """
        Test that display_hierarchy runs without raising exceptions.
        Note: This test is limited as it cannot verify Streamlit's UI output.
        """
        try:
            self.visualizer.display_hierarchy(self.root)
            self.assertTrue(True)  # Pass if no exception is raised
        except Exception as e:
            self.fail(f"display_hierarchy raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()
