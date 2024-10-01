# tests/test_hierarchy_builder.py

import unittest
from unittest.mock import MagicMock, patch
from anytree import Node, PreOrderIter
from hierarchy_builder import HierarchyBuilder

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

    def test_build_hierarchy(self):
        # Setup the mock_prompt_builder to return specific prompts based on input
        self.mock_prompt_builder.build_sectors_prompt.return_value = "Build sectors prompt"
        self.mock_prompt_builder.build_subsectors_prompt.side_effect = self.mock_build_subsectors_prompt
        self.mock_prompt_builder.build_end_users_provider_prompt.return_value = "Build end users provider prompt"
        self.mock_prompt_builder.build_jobs_prompt.return_value = "Build jobs prompt"
        self.mock_prompt_builder.build_end_users_customer_prompt.return_value = "Build end users customer prompt"
        self.mock_prompt_builder.build_jtbd_customers_prompt.return_value = "Build JTBD customers prompt"

        # Setup the mock_llm to return specific responses based on prompts
        def llm_get_response_side_effect(prompt):
            if prompt == "Build sectors prompt":
                return SECTORS_RESPONSE
            elif prompt == "Build subsectors prompt for Banking":
                return SUBSECTORS_RESPONSE_BANKING
            elif prompt == "Build subsectors prompt for Investment":
                return SUBSECTORS_RESPONSE_INVESTMENT
            elif prompt == "Build end users provider prompt":
                return END_USERS_PROVIDER_RESPONSE
            elif prompt == "Build jobs prompt":
                return JOBS_RESPONSE
            elif prompt == "Build end users customer prompt":
                return END_USERS_CUSTOMER_RESPONSE
            elif prompt == "Build JTBD customers prompt":
                return JOBS_CUSTOMER_RESPONSE
            else:
                return ""

        self.mock_llm.get_response.side_effect = llm_get_response_side_effect

        # Build the hierarchy
        root = self.hierarchy_builder.build_hierarchy(
            industry=self.industry,
            fidelity="comprehensive",
            n_end_users=2,
            n_jobs=2
        )

        # Verify the structure
        # Root node
        self.assertEqual(root.name, "Finance")
        self.assertEqual(root.description, "Root node for industry hierarchy")

        # Sectors
        sectors = [child for child in root.children]
        self.assertEqual(len(sectors), 2)
        self.assertEqual(sectors[0].name, "Banking")
        self.assertEqual(sectors[1].name, "Investment")

        # Subsectors
        banking_subsectors = [child for child in sectors[0].children]
        investment_subsectors = [child for child in sectors[1].children]
        self.assertEqual(len(banking_subsectors), 2)
        self.assertEqual(len(investment_subsectors), 2)
        self.assertEqual(banking_subsectors[0].name, "Retail Banking")
        self.assertEqual(banking_subsectors[1].name, "Corporate Banking")
        self.assertEqual(investment_subsectors[0].name, "Asset Management")
        self.assertEqual(investment_subsectors[1].name, "Investment Banking")

        # End Users - Providers and Customers
        for subsector in banking_subsectors + investment_subsectors:
            # Providers
            providers_parent = next(
                (child for child in subsector.children if child.name == "End Users - Providers"), None)
            self.assertIsNotNone(providers_parent)
            providers = [child for child in providers_parent.children]
            self.assertEqual(len(providers), 2)
            self.assertEqual(providers[0].name, "Service Providers")
            self.assertEqual(providers[1].name, "Product Providers")

            # Customers
            customers_parent = next(
                (child for child in subsector.children if child.name == "End Users - Customers"), None)
            self.assertIsNotNone(customers_parent)
            customers = [child for child in customers_parent.children]
            self.assertEqual(len(customers), 2)
            self.assertEqual(customers[0].name, "Individual Consumers")
            self.assertEqual(customers[1].name, "Small Businesses")

        # Jobs
        # Collect all job nodes
        jobs = [node for node in PreOrderIter(root) if node.name in ["Account Manager", "Financial Analyst", "Personal Banker", "Business Consultant"]]
        self.assertEqual(len(jobs), 32)
        # Further checks can be added as needed

        # Ensure all job nodes are marked as not processed
        for job in jobs:
            self.assertFalse(job.processed)

    def mock_build_subsectors_prompt(self, industry, sector_info, fidelity):
        """
        Mocked build_subsectors_prompt to return different prompts based on sector.
        """
        if "Banking" in sector_info:
            return "Build subsectors prompt for Banking"
        elif "Investment" in sector_info:
            return "Build subsectors prompt for Investment"
        else:
            return "Build subsectors prompt"

    # Corrected test_save_current_hierarchy with proper patching
    @patch("hierarchy_builder.save_hierarchy_to_file")
    @patch("hierarchy_builder.save_hierarchy_to_markdown")
    def test_save_current_hierarchy(self, mock_save_text, mock_save_file):
        # Setup hierarchy_builder attributes with description and processed
        self.hierarchy_builder.root = Node(
            "Finance", 
            description="Root node for hierarchy", 
            processed=False
        )
        self.hierarchy_builder.industry = "Finance"

        # Call the method
        self.hierarchy_builder.save_current_hierarchy()

        # Assertions
        mock_save_file.assert_called_once_with(self.hierarchy_builder.root, "Finance_hierarchy.json")
        mock_save_text.assert_called_once_with("Finance_hierarchy.json", "Finance_hierarchy_output.md")


if __name__ == '__main__':
    unittest.main()
