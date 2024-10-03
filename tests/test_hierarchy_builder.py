# tests/test_hierarchy_builder.py

import unittest
import json
import os
from unittest.mock import MagicMock, patch
from anytree import Node, PreOrderIter
from hierarchy_builder import HierarchyBuilder
from utils import save_hierarchy_to_file, save_hierarchy_to_markdown


# Sample responses for testing
SECTORS_RESPONSE = """
1. **Banking**: Deals with deposit accounts, loans, and credit services.
2. **Investment**: Focuses on asset management, securities trading, and advisory services.
"""

SUBSECTORS_RESPONSE_BANKING = """
1. **Retail Banking**: Provides services to individual consumers.
2. **Corporate Banking**: Offers financial services to businesses.
"""

SUBSECTORS_RESPONSE_INVESTMENT = """
1. **Asset Management**: Manages client assets and investments.
2. **Investment Banking**: Provides advisory and capital raising services.
"""

END_USERS_PROVIDER_RESPONSE = """
1. **Service Providers**: Companies that offer financial services.
2. **Product Providers**: Firms that develop financial products.
"""

END_USERS_CUSTOMER_RESPONSE = """
1. **Individual Consumers**: People looking for personal banking solutions.
2. **Small Businesses**: Enterprises requiring financial support.
"""

JOBS_RESPONSE = """
1. **Account Manager** - Manages customer accounts and ensures satisfaction.
2. **Financial Analyst** - Analyzes financial data to guide investment decisions.
"""

JOBS_CUSTOMER_RESPONSE = """
1. **Personal Banker** - Assists individuals with their banking needs.
2. **Business Consultant** - Provides financial advice to small businesses.
"""

class TestHierarchyBuilder(unittest.TestCase):
    def setUp(self):
        # Initialize mocks for LLMInterface and PromptBuilder
        self.mock_llm = MagicMock()
        self.mock_prompt_builder = MagicMock()

        # Initialize HierarchyBuilder with mocks
        self.hierarchy_builder = HierarchyBuilder(
            llm_interface=self.mock_llm,
            prompt_builder=self.mock_prompt_builder,
            fidelity="comprehensive"
        )

        # Sample industry
        self.industry = "Finance"
        self.hierarchy_builder.industry = self.industry

    def tearDown(self):
        # Clean up any saved hierarchy files after the test run
        save_file_path = self.hierarchy_builder._get_save_file_path(self.industry)
        if os.path.exists(save_file_path):
            try:
                os.remove(save_file_path)
                print(f"Successfully removed file: {save_file_path}")
            except PermissionError as e:
                print(f"Permission error when removing file: {save_file_path}. Retrying...")
                time.sleep(1)  # Wait a moment and try again
                try:
                    os.remove(save_file_path)
                    print(f"Successfully removed file after retry: {save_file_path}")
                except Exception as e:
                    print(f"Failed to remove file '{save_file_path}': {e}")
            except Exception as e:
                print(f"Failed to remove file '{save_file_path}': {e}")

    def test_parse_list(self):
        # Test parsing a sectors response
        parsed = self.hierarchy_builder.parse_list(SECTORS_RESPONSE)
        expected = [
            {"name": "Banking", "description": "Deals with deposit accounts, loans, and credit services."},
            {"name": "Investment", "description": "Focuses on asset management, securities trading, and advisory services."}
        ]
        self.assertEqual(parsed, expected)

    def test_parse_roles(self):
        # Test parsing end users (providers)
        parsed = self.hierarchy_builder.parse_roles(END_USERS_PROVIDER_RESPONSE)
        expected = [
            {"role": "Service Providers", "description": "Companies that offer financial services."},
            {"role": "Product Providers", "description": "Firms that develop financial products."}
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

    @patch("hierarchy_builder.save_hierarchy_to_file")
    @patch("os.path.exists", return_value=True)  # Mock os.path.exists to always return True
    @patch("hierarchy_builder.save_hierarchy_to_markdown")
    def test_save_current_hierarchy(self, mock_save_markdown, mock_path_exists, mock_save_file):
        # Setup hierarchy_builder attributes with description and processed
        self.hierarchy_builder.root = Node(
            "Finance", 
            description="Root node for industry hierarchy", 
            processed=False
        )
        self.hierarchy_builder.industry = "Finance"

        # Mock file path to ensure consistent behavior
        save_file_path = self.hierarchy_builder._get_save_file_path(self.industry)

        # Add debugging statements before the function call
        print(f"Root node name: {self.hierarchy_builder.root.name}, Description: {self.hierarchy_builder.root.description}")
        print(f"Save file path: {save_file_path}")
        print("Calling _save_current_hierarchy...")

        # Call the method
        try:
            self.hierarchy_builder._save_current_hierarchy()
        except Exception as e:
            print(f"Exception occurred: {e}")

        # Debug print after the function call
        print("Finished calling _save_current_hierarchy")

        # Assertions to ensure file was saved and markdown function was called
        print(f"mock_save_file called: {mock_save_file.called}")
        print(f"mock_save_markdown called: {mock_save_markdown.called}")
        print(f"mock_save_file call args: {mock_save_file.call_args}")
        print(f"mock_save_markdown call args: {mock_save_markdown.call_args}")

        # Verify if save_hierarchy_to_file was called correctly
        mock_save_file.assert_called_once_with(self.hierarchy_builder.root, save_file_path)
        mock_save_markdown.assert_called_once_with(save_file_path, f"{self.industry}_hierarchy_output.md")



    def test_resume_from_saved_state(self):
        # Create a mock saved hierarchy to simulate resuming from a saved state
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

        # Mock loading the hierarchy file
        with patch("builtins.open", unittest.mock.mock_open(read_data=json.dumps(saved_hierarchy))):
            self.hierarchy_builder._resume_from_saved_state(saved_hierarchy)

            # Check that the root node was correctly reconstructed
            self.assertEqual(self.hierarchy_builder.root.name, "Finance")
            self.assertEqual(self.hierarchy_builder.root.description, "Root node for industry hierarchy")

            # Validate children nodes
            banking_node = self.hierarchy_builder.root.children[0]
            self.assertEqual(banking_node.name, "Banking")
            self.assertEqual(banking_node.description, "Deals with deposit accounts, loans, and credit services.")

            retail_node = banking_node.children[0]
            self.assertEqual(retail_node.name, "Retail Banking")
            self.assertEqual(retail_node.description, "Provides services to individual consumers.")

    def test_build_hierarchy_from_scratch(self):
        # Mock LLM responses and prompts to simulate hierarchy building from scratch
        self.mock_prompt_builder.build_sectors_prompt.return_value = "Build sectors prompt"
        self.mock_prompt_builder.build_subsectors_prompt.side_effect = self.mock_build_subsectors_prompt
        self.mock_prompt_builder.build_end_users_provider_prompt.return_value = "Build end users provider prompt"
        self.mock_prompt_builder.build_jobs_prompt.return_value = "Build jobs prompt"
        self.mock_prompt_builder.build_end_users_customer_prompt.return_value = "Build end users customer prompt"
        self.mock_prompt_builder.build_jtbd_customers_prompt.return_value = "Build JTBD customers prompt"

        # Mock the prompt_builder.get_prompt method to return expected string prompts
        self.mock_prompt_builder.get_prompt.side_effect = lambda prompt_name, **kwargs: {
            'sectors': f"Prompt for sectors in industry {kwargs.get('industry')} with fidelity {kwargs.get('fidelity')}",
            'subsectors': f"Prompt for subsectors in industry {kwargs.get('industry')}, sector {kwargs.get('sector')} with fidelity {kwargs.get('fidelity')}",
            'end_users_provider': f"Prompt for providers in industry {kwargs.get('industry')}, sector {kwargs.get('sector')}, subsector {kwargs.get('subsector')} with fidelity {kwargs.get('fidelity')}",
            'end_users_customer': f"Prompt for customers in industry {kwargs.get('industry')}, sector {kwargs.get('sector')}, subsector {kwargs.get('subsector')} with fidelity {kwargs.get('fidelity')}",
            'jtbd_industry': f"Prompt for jobs-to-be-done in provider {kwargs.get('provider_role')} in industry {kwargs.get('industry')}, sector {kwargs.get('sector')}, subsector {kwargs.get('subsector')}",
            'jtbd_customers': f"Prompt for jobs-to-be-done in customer {kwargs.get('customer_role')} in industry {kwargs.get('industry')}, sector {kwargs.get('sector')}, subsector {kwargs.get('subsector')}"
        }.get(prompt_name, "Invalid prompt")

        # Mock LLM responses to correspond to each of the prompts
        self.mock_llm.get_response.side_effect = lambda prompt: {
            f"Prompt for sectors in industry Finance with fidelity comprehensive": SECTORS_RESPONSE,
            f"Prompt for subsectors in industry Finance, sector Banking with fidelity comprehensive": SUBSECTORS_RESPONSE_BANKING,
            f"Prompt for subsectors in industry Finance, sector Investment with fidelity comprehensive": SUBSECTORS_RESPONSE_INVESTMENT,
            f"Prompt for providers in industry Finance, sector Banking, subsector Retail Banking with fidelity comprehensive": END_USERS_PROVIDER_RESPONSE,
            f"Prompt for customers in industry Finance, sector Banking, subsector Retail Banking with fidelity comprehensive": END_USERS_CUSTOMER_RESPONSE,
            f"Prompt for jobs-to-be-done in provider Service Providers in industry Finance, sector Banking, subsector Retail Banking": JOBS_RESPONSE,
            f"Prompt for jobs-to-be-done in customer Individual Consumers in industry Finance, sector Banking, subsector Retail Banking": JOBS_CUSTOMER_RESPONSE
        }.get(prompt, "")
        # self.mock_llm.get_response.side_effect = lambda prompt: {
        #     "Build sectors prompt": SECTORS_RESPONSE,
        #     "Build subsectors prompt for Banking": SUBSECTORS_RESPONSE_BANKING,
        #     "Build subsectors prompt for Investment": SUBSECTORS_RESPONSE_INVESTMENT,
        #     "Build end users provider prompt": END_USERS_PROVIDER_RESPONSE,
        #     "Build jobs prompt": JOBS_RESPONSE,
        #     "Build end users customer prompt": END_USERS_CUSTOMER_RESPONSE,
        #     "Build JTBD customers prompt": JOBS_CUSTOMER_RESPONSE
        # }.get(prompt, "")
        # self.mock_llm.get_response.side_effect = lambda prompt: {
        #     "sectors": SECTORS_RESPONSE,
        #     "subsectors": SUBSECTORS_RESPONSE_BANKING,
        #     "end_users_provider": END_USERS_PROVIDER_RESPONSE,
        #     "jobs": JOBS_RESPONSE,
        #     "end_users_customer": END_USERS_CUSTOMER_RESPONSE,
        #     "jtbd_customers": JOBS_CUSTOMER_RESPONSE
        # }.get(prompt, "")


        # Build the hierarchy from scratch
        root = self.hierarchy_builder.build_hierarchy(
            industry=self.industry,
            fidelity="comprehensive",
            n_end_users=2,
            n_jobs=2
        )

        # Add debugging prints to trace the values
        print(f"Root node: {root.name}, Description: {root.description}")

        # Validate the root node
        self.assertEqual(root.name, "Finance")
        self.assertEqual(root.description, "Root node for industry hierarchy")

        # Validate sectors
        sectors = [child for child in root.children]
        print(f"Parsed sectors: {sectors}")
        self.assertEqual(len(sectors), 2)  # Ensure two sectors were parsed

        if len(sectors) > 0:
            self.assertEqual(sectors[0].name, "Banking")
            self.assertEqual(sectors[1].name, "Investment")
        else:
            print("Error: Sectors list is empty. Check LLM responses and parsing.")

    def mock_build_subsectors_prompt(self, industry, sector_info, fidelity):
        if "Banking" in sector_info:
            return "Build subsectors prompt for Banking"
        elif "Investment" in sector_info:
            return "Build subsectors prompt for Investment"
        else:
            return "Build subsectors prompt"

if __name__ == '__main__':
    unittest.main()
