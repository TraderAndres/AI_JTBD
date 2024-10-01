# tests/test_utils.py

import unittest
from unittest.mock import mock_open, patch
import json
from anytree import Node, PreOrderIter
from utils import (
    node_to_dict,
    save_hierarchy_to_file,
    save_hierarchy_to_markdown,
    dict_to_tree,
    render_hierarchy_markdown
)


class TestUtils(unittest.TestCase):
    def setUp(self):
        # Create a sample hierarchy
        self.root = Node("Finance", description="Root node for industry hierarchy", processed=False)
        banking = Node(
            "Banking",
            parent=self.root,
            description="This sector includes institutions that accept deposits, offer loans, and provide various financial services, including retail banking, commercial banking, and investment banking.",
            processed=False
        )
        investment = Node(
            "Investment",
            parent=self.root,
            description="Focuses on asset management, securities trading, and advisory services.",
            processed=False
        )

        retail_banking = Node(
            "Retail Banking",
            parent=banking,
            description="This involves providing financial services such as checking and savings accounts, personal loans, mortgages, and credit cards directly to consumers and small businesses.",
            processed=False
        )
        corporate_banking = Node(
            "Corporate Banking",
            parent=banking,
            description="Offers financial services to businesses.",
            processed=False
        )

        asset_management = Node(
            "Asset Management",
            parent=investment,
            description="Manages client assets and investments.",
            processed=False
        )
        investment_banking = Node(
            "Investment Banking",
            parent=investment,
            description="Provides advisory and capital raising services.",
            processed=False
        )

        service_providers = Node(
            "Service Providers",
            parent=retail_banking,
            description="Companies that offer financial services.",
            processed=False
        )
        product_providers = Node(
            "Product Providers",
            parent=retail_banking,
            description="Firms that develop financial products.",
            processed=False
        )

        individual_consumers = Node(
            "Individual Consumers",
            parent=corporate_banking,
            description="People looking for personal banking solutions.",
            processed=False
        )
        small_businesses = Node(
            "Small Businesses",
            parent=corporate_banking,
            description="Enterprises requiring financial support.",
            processed=False
        )

        account_manager = Node(
            "Account Manager",
            parent=service_providers,
            description="Manages customer accounts and ensures satisfaction.",
            processed=False
        )
        financial_analyst = Node(
            "Financial Analyst",
            parent=service_providers,
            description="Analyzes financial data to guide investment decisions.",
            processed=False
        )

        personal_banker = Node(
            "Personal Banker",
            parent=individual_consumers,
            description="Assists individuals with their banking needs.",
            processed=False
        )
        business_consultant = Node(
            "Business Consultant",
            parent=small_businesses,
            description="Provides financial advice to small businesses.",
            processed=False
        )

    def test_node_to_dict(self):
        """
        Test that node_to_dict correctly converts a Node tree to a dictionary.
        """
        expected_dict = {
            "name": "Finance",
            "description": "Root node for industry hierarchy",
            "processed": False,
            "children": [
                {
                    "name": "Banking",
                    "description": "This sector includes institutions that accept deposits, offer loans, and provide various financial services, including retail banking, commercial banking, and investment banking.",
                    "processed": False,
                    "children": [
                        {
                            "name": "Retail Banking",
                            "description": "This involves providing financial services such as checking and savings accounts, personal loans, mortgages, and credit cards directly to consumers and small businesses.",
                            "processed": False,
                            "children": [
                                {
                                    "name": "Service Providers",
                                    "description": "Companies that offer financial services.",
                                    "processed": False,
                                    "children": [
                                        {
                                            "name": "Account Manager",
                                            "description": "Manages customer accounts and ensures satisfaction.",
                                            "processed": False,
                                            "children": []
                                        },
                                        {
                                            "name": "Financial Analyst",
                                            "description": "Analyzes financial data to guide investment decisions.",
                                            "processed": False,
                                            "children": []
                                        }
                                    ]
                                },
                                {
                                    "name": "Product Providers",
                                    "description": "Firms that develop financial products.",
                                    "processed": False,
                                    "children": []
                                }
                            ]
                        },
                        {
                            "name": "Corporate Banking",
                            "description": "Offers financial services to businesses.",
                            "processed": False,
                            "children": [
                                {
                                    "name": "Individual Consumers",
                                    "description": "People looking for personal banking solutions.",
                                    "processed": False,
                                    "children": [
                                        {
                                            "name": "Personal Banker",
                                            "description": "Assists individuals with their banking needs.",
                                            "processed": False,
                                            "children": []
                                        }
                                    ]
                                },
                                {
                                    "name": "Small Businesses",
                                    "description": "Enterprises requiring financial support.",
                                    "processed": False,
                                    "children": [
                                        {
                                            "name": "Business Consultant",
                                            "description": "Provides financial advice to small businesses.",
                                            "processed": False,
                                            "children": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "name": "Investment",
                    "description": "Focuses on asset management, securities trading, and advisory services.",
                    "processed": False,
                    "children": [
                        {
                            "name": "Asset Management",
                            "description": "Manages client assets and investments.",
                            "processed": False,
                            "children": []
                        },
                        {
                            "name": "Investment Banking",
                            "description": "Provides advisory and capital raising services.",
                            "processed": False,
                            "children": []
                        }
                    ]
                }
            ]
        }

        result_dict = node_to_dict(self.root)
        self.assertEqual(result_dict, expected_dict)

    def test_save_hierarchy_to_file(self):
        """
        Test that save_hierarchy_to_file correctly writes the hierarchy to a JSON file.
        """
        with patch('builtins.open', mock_open()) as mocked_file:
            save_hierarchy_to_file(self.root, 'test_hierarchy.json')

            # Ensure open was called correctly
            mocked_file.assert_called_once_with('test_hierarchy.json', 'w')

            # Retrieve the handle to the mock file
            handle = mocked_file()

            # Expected JSON string
            expected_dict = node_to_dict(self.root)
            expected_json = json.dumps(expected_dict, indent=4)

            # Retrieve all write calls and concatenate them
            written_data = ''.join(call.args[0] for call in handle.write.call_args_list)

            # Assert that the concatenated write calls match the expected JSON
            self.assertEqual(written_data, expected_json)


    def test_save_hierarchy_to_markdown(self):
        """
        Test that save_hierarchy_to_markdown correctly writes the hierarchy to a Markdown file.
        """
        # Prepare a mock for open in read mode to return the JSON hierarchy
        mock_json_data = node_to_dict(self.root)
        mock_json_str = json.dumps(mock_json_data)

        # Create two separate mock_open instances
        m_open_read = mock_open(read_data=mock_json_str)
        m_open_write = mock_open()

        # Use side_effect to return different mocks based on the order of open calls
        with patch('builtins.open', side_effect=[m_open_read.return_value, m_open_write.return_value]) as mocked_file:
            save_hierarchy_to_markdown('test_hierarchy.json', 'test_hierarchy.md')

            # Check that open was called correctly for reading
            mocked_file.assert_any_call('test_hierarchy.json', 'r')

            # Check that open was called correctly for writing
            mocked_file.assert_any_call('test_hierarchy.md', 'w')

            # Build the expected markdown text
            root = dict_to_tree(mock_json_data)
            expected_text = render_hierarchy_markdown(root)

            # Retrieve the handle for the write mock and assert the write call
            handle_write = m_open_write()
            handle_write.write.assert_called_once_with(expected_text)


    def test_dict_to_tree(self):
        """
        Test that dict_to_tree correctly reconstructs the tree from a dictionary.
        """
        hierarchy_dict = node_to_dict(self.root)
        reconstructed_root = dict_to_tree(hierarchy_dict)

        # Compare the original and reconstructed trees
        original_names = [node.name for node in PreOrderIter(self.root)]
        reconstructed_names = [node.name for node in PreOrderIter(reconstructed_root)]
        self.assertEqual(original_names, reconstructed_names)

        # Compare descriptions and processed attributes
        for original_node, reconstructed_node in zip(PreOrderIter(self.root), PreOrderIter(reconstructed_root)):
            self.assertEqual(original_node.description, reconstructed_node.description)
            self.assertEqual(original_node.processed, reconstructed_node.processed)

    def test_render_hierarchy_markdown(self):
        """
        Test that render_hierarchy_markdown correctly formats the hierarchy as Markdown.
        """
        expected_text = (
            "- **Finance**: Root node for industry hierarchy\n"
            "    - **Banking**: This sector includes institutions that accept deposits, offer loans, and provide various financial services, including retail banking, commercial banking, and investment banking.\n"
            "        - **Retail Banking**: This involves providing financial services such as checking and savings accounts, personal loans, mortgages, and credit cards directly to consumers and small businesses.\n"
            "            - **Service Providers**: Companies that offer financial services.\n"
            "                - **Account Manager**: Manages customer accounts and ensures satisfaction.\n"
            "                - **Financial Analyst**: Analyzes financial data to guide investment decisions.\n"
            "            - **Product Providers**: Firms that develop financial products.\n"
            "        - **Corporate Banking**: Offers financial services to businesses.\n"
            "            - **Individual Consumers**: People looking for personal banking solutions.\n"
            "                - **Personal Banker**: Assists individuals with their banking needs.\n"
            "            - **Small Businesses**: Enterprises requiring financial support.\n"
            "                - **Business Consultant**: Provides financial advice to small businesses.\n"
            "    - **Investment**: Focuses on asset management, securities trading, and advisory services.\n"
            "        - **Asset Management**: Manages client assets and investments.\n"
            "        - **Investment Banking**: Provides advisory and capital raising services.\n"
        )

        hierarchy_dict = node_to_dict(self.root)
        root = dict_to_tree(hierarchy_dict)
        result_text = render_hierarchy_markdown(root)
        self.assertEqual(result_text, expected_text)


if __name__ == '__main__':
    unittest.main()
