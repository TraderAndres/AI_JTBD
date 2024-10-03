# tests/test_hierarchy_builder.py

import unittest
import json
import os
from unittest.mock import MagicMock, patch
from anytree import Node
from hierarchy_builder import HierarchyBuilder
from mongo_manager import MongoDBManager

# Sample responses for testing
SECTORS_RESPONSE = """
1. **Banking**: Deals with deposit accounts, loans, and credit services.
2. **Investment**: Focuses on asset management, securities trading, and advisory services.
"""

SUBSECTORS_RESPONSE_BANKING = """
1. **Retail Banking**: Provides services to individual consumers.
2. **Corporate Banking**: Offers financial services to businesses.
"""

END_USERS_PROVIDER_RESPONSE = """
1. **Service Providers**: Companies that offer financial services.
2. **Product Providers**: Firms that develop financial products.
"""

JOBS_RESPONSE = """
1. **Account Manager** - Manages customer accounts and ensures satisfaction.
2. **Financial Analyst** - Analyzes financial data to guide investment decisions.
"""

class TestHierarchyBuilder(unittest.TestCase):
    @patch("hierarchy_builder.MongoDBManager")  # Mock the MongoDBManager class
    def setUp(self, mock_mongo_manager):
        """
        Set up the test environment, mocking MongoDB and other components.
        """
        # Mock the MongoDBManager instance and its methods
        self.mock_mongo_manager_instance = mock_mongo_manager.return_value
        self.mock_mongo_manager_instance.set_collection.return_value = None
        self.mock_mongo_manager_instance.find_entry.return_value = None  # Default no saved entry

        # Set up mocks for LLMInterface and PromptBuilder
        self.mock_llm = MagicMock()
        self.mock_prompt_builder = MagicMock()

        # Initialize HierarchyBuilder with mocks, including MongoDBManager mock
        self.hierarchy_builder = HierarchyBuilder(
            llm_interface=self.mock_llm,
            prompt_builder=self.mock_prompt_builder,
            fidelity="comprehensive",
            mongo_uri="mongodb://localhost:27017",  # Use test URI
            db_name="test_db"
        )

        # Inject the mocked MongoDBManager into the HierarchyBuilder
        self.hierarchy_builder.mongo_manager = self.mock_mongo_manager_instance

    def test_parse_list(self):
        # Test parsing a sectors response
        parsed = self.hierarchy_builder.parse_list(SECTORS_RESPONSE)
        expected = [
            {"name": "Banking", "description": "Deals with deposit accounts, loans, and credit services."},
            {"name": "Investment", "description": "Focuses on asset management, securities trading, and advisory services."}
        ]
        self.assertEqual(parsed, expected)

    def test_parse_jobs(self):
        # Test parsing jobs
        parsed = self.hierarchy_builder.parse_jobs(JOBS_RESPONSE)
        expected = [
            {"job": "Account Manager", "description": "Manages customer accounts and ensures satisfaction."},
            {"job": "Financial Analyst", "description": "Analyzes financial data to guide investment decisions."}
        ]
        self.assertEqual(parsed, expected)

    def test_save_current_hierarchy(self):
        """
        Test if the current hierarchy is saved correctly to MongoDB.
        """
        # Setup a mock root node
        self.hierarchy_builder.root = Node("Finance", description="Root node for industry hierarchy")
        self.hierarchy_builder.industry = "Finance"

        # Call the _save_current_hierarchy method
        self.hierarchy_builder._save_current_hierarchy()

        # Prepare expected document for insertion
        expected_document = {
            "industry": "Finance",
            "hierarchy": {
                "name": "Finance",
                "description": "Root node for industry hierarchy",
                "processed": False,
                "children": []
            }
        }

        # Assert that insert_entry or update_entry was called with the expected document
        self.mock_mongo_manager_instance.insert_entry.assert_called_once_with(expected_document)
        self.mock_mongo_manager_instance.update_entry.assert_not_called()

    def test_resume_from_saved_state(self):
        """
        Test if the hierarchy is correctly resumed from a saved state in MongoDB.
        """
        # Create a mock saved hierarchy entry
        saved_hierarchy = {
            "name": "Finance",
            "description": "Root node for industry hierarchy",
            "processed": False,
            "children": [
                {
                    "name": "Banking",
                    "description": "Deals with deposit accounts, loans, and credit services.",
                    "processed": False,
                    "children": [
                        {
                            "name": "Retail Banking",
                            "description": "Provides services to individual consumers.",
                            "processed": False,
                            "children": []
                        }
                    ]
                }
            ]
        }

        # Mock MongoDBManager find_entry method to return the saved hierarchy
        self.mock_mongo_manager_instance.find_entry.return_value = {"hierarchy": saved_hierarchy}

        # Call the resume method
        self.hierarchy_builder._resume_from_saved_state(saved_hierarchy)

        # Check that the root node was correctly reconstructed
        self.assertEqual(self.hierarchy_builder.root.name, "Finance")
        self.assertEqual(self.hierarchy_builder.root.description, "Root node for industry hierarchy")

        # Validate the child nodes
        banking_node = self.hierarchy_builder.root.children[0]
        self.assertEqual(banking_node.name, "Banking")
        self.assertEqual(banking_node.description, "Deals with deposit accounts, loans, and credit services.")

        retail_node = banking_node.children[0]
        self.assertEqual(retail_node.name, "Retail Banking")
        self.assertEqual(retail_node.description, "Provides services to individual consumers.")

    def test_build_hierarchy_from_scratch(self):
        """
        Test building the hierarchy from scratch and saving to MongoDB.
        """
        # Set the industry properly before building the hierarchy
        self.hierarchy_builder.industry = "Finance"

        # Mock LLM responses and prompts to simulate hierarchy building from scratch
        self.mock_prompt_builder.get_prompt.side_effect = lambda prompt_name, **kwargs: f"Prompt for {prompt_name}"

        self.mock_llm.get_response.side_effect = lambda prompt: {
            "Prompt for sectors": SECTORS_RESPONSE,
            "Prompt for subsectors": SUBSECTORS_RESPONSE_BANKING,
            "Prompt for end_users_provider": END_USERS_PROVIDER_RESPONSE,
            "Prompt for jobs": JOBS_RESPONSE,
            "Prompt for end_users_customer": END_USERS_PROVIDER_RESPONSE,
            "Prompt for jtbd_customers": JOBS_RESPONSE
        }.get(prompt, "")

        # Ensure that the MongoDB mock has insert_entry and update_entry set up
        print(f"Before build: MongoDB insert_entry called {self.mock_mongo_manager_instance.insert_entry.call_count} times")
        print(f"Before build: MongoDB update_entry called {self.mock_mongo_manager_instance.update_entry.call_count} times")

        # Build the hierarchy from scratch with the correct industry parameter
        root = self.hierarchy_builder.build_hierarchy(
            industry=self.hierarchy_builder.industry,  # Pass the correct industry here
            fidelity="comprehensive",
            n_end_users=2,
            n_jobs=2
        )

        # Check that the MongoDB insert_entry method was called multiple times during hierarchy building
        self.assertGreater(self.mock_mongo_manager_instance.insert_entry.call_count, 0, "MongoDB insert_entry was not called during hierarchy building")

        # Additional debugging information after build
        print(f"After build: MongoDB insert_entry called {self.mock_mongo_manager_instance.insert_entry.call_count} times")



if __name__ == '__main__':
    unittest.main()
