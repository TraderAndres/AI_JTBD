import unittest
import os
from prompt_builder import PromptBuilder, PromptParser  # Import both PromptBuilder and PromptParser


class TestPromptBuilder(unittest.TestCase):
    def setUp(self):
        """
        Set up instances for PromptBuilder and PromptParser.
        """
        # Create a PromptBuilder instance to test prompt loading and fetching
        self.prompt_builder = PromptBuilder(prompts_dir='prompts')
        # Create a PromptParser instance to test parsing methods
        self.prompt_parser = PromptParser()

    def test_load_prompts(self):
        """
        Test that all prompts, including those in subdirectories, are correctly loaded.
        """
        # Load prompts from the specified directory
        self.prompt_builder.load_prompts(prompts_dir='prompts')

        # Check prompts loaded from both base and subdirectories
        self.assertIn('job_contexts', self.prompt_builder.prompts)
        self.assertIn('job_map', self.prompt_builder.prompts)
        self.assertIn('sectors', self.prompt_builder.prompts)
        self.assertIn('subsectors', self.prompt_builder.prompts)
        self.assertIn('jtbd_customers', self.prompt_builder.prompts)
        self.assertIn('end_users_customer', self.prompt_builder.prompts)

    def test_get_prompt(self):
        """
        Test the generation of prompts using provided parameters.
        """
        prompt = self.prompt_builder.get_prompt(
            'job_contexts',
            end_user='DevOps Engineer',
            job='Building Systems',
            n=10
        )
        # Check that the prompt is correctly formatted
        self.assertIn('Act as a(n) DevOps Engineer', prompt)
        self.assertIn('Building Systems', prompt)
        self.assertIn('List 10 contexts', prompt)  # Check that 'n=10' is reflected in the context

        prompt = self.prompt_builder.get_prompt(
            'job_map',
            end_user='Hedge Fund Analyst',
            job='Building Systems',
            context='Analyzing financials',
            fidelity='med'
        )
        # Check that the prompt is correctly formatted
        self.assertIn('Act as a(n) Hedge Fund Analyst', prompt)
        self.assertIn('Building Systems', prompt)
        self.assertIn('Analyzing financials', prompt)
        self.assertIn('med', prompt)  # Check that 'n=10' is reflected in the context

    def test_get_prompt_with_defaults(self):
        """
        Test getting a prompt using only required parameters and default values.
        """
        # Test a prompt that has a default value for 'fidelity'
        prompt = self.prompt_builder.get_prompt(
            'subsectors',
            industry='Healthcare',
            sector='Pharmaceuticals'
        )
        # Check if the default fidelity value is used
        self.assertIn('Healthcare', prompt)
        self.assertIn('Pharmaceuticals', prompt)
        self.assertIn('comprehensive', prompt)  # Default fidelity value should be 'comprehensive'

    def test_get_prompt_missing_required(self):
        """
        Test that an error is raised when a required parameter is missing.
        """
        with self.assertRaises(ValueError):
            self.prompt_builder.get_prompt('job_contexts', end_user='DevOps Engineer')

    def test_parse_job_contexts(self):
        """
        Test parsing for job contexts using the PromptParser class.
        """
        response = """
        1. **IT Managed Services Provider** - A company looking to outsource the management of their IT infrastructure.
        2. **Network Security Specialist** - An individual focused on protecting the organization's network from cyber threats.
        """
        expected = [
            {
                "name": "IT Managed Services Provider",
                "description": "A company looking to outsource the management of their IT infrastructure."
            },
            {
                "name": "Network Security Specialist",
                "description": "An individual focused on protecting the organization's network from cyber threats."
            }
        ]
        result = self.prompt_parser.parse_job_contexts(response)
        self.assertEqual(result, expected)

    def test_parse_job_map(self):
        """
        Test parsing for job maps using the PromptParser class.
        """
        response = """
        1. **Developing System Architecture** - Creating a structured framework for system design.
        2. **Designing Technical Specifications** - Laying out detailed technical requirements for system components.
        """
        expected = [
            {
                "name": "Developing System Architecture",
                "description": "Creating a structured framework for system design."
            },
            {
                "name": "Designing Technical Specifications",
                "description": "Laying out detailed technical requirements for system components."
            }
        ]
        result = self.prompt_parser.parse_job_map(response)
        self.assertEqual(result, expected)

    def test_parse_list_responses(self):
        """
        Test the generic _parse_list_response function with different formatting using the PromptParser.
        """
        response = """
        1. **Role A** - Description A.
        2. **Role B**: Description B.
        3. Role C - Description C.
        """
        # Adjust the expected result to include all three roles correctly
        expected = [
            {"name": "Role A", "description": "Description A."},
            {"name": "Role B", "description": "Description B."},
            {"name": "Role C", "description": "Description C."},  # Include the missing element in the expected output
        ]

        # Run the _parse_list_response function and check if the result matches the expected output
        result = self.prompt_parser._parse_list_response(response)

        # Debug prints
        print(f"Result: {result}")
        print(f"Expected: {expected}")
        print(f"Assertion Difference: {set([str(r) for r in result]) - set([str(e) for e in expected])}")

    
        self.assertEqual(result, expected)


    def test_parsing_methods(self):
        """
        Test the specific parsing methods for various prompt types using the PromptParser.
        """
        response = """
        1. **Improving Data Security** - Developing security protocols for data.
        2. **Enhancing System Scalability** - Increasing the system's capacity to handle growth.
        """
        # Test parsing for different job-related prompts using the PromptParser instance
        parse_methods = [
            'parse_job_contexts',
            'parse_job_map',
            'parse_desired_outcomes',
            'parse_themed_desired_outcomes',
            'parse_situational_and_complexity_factors',
            'parse_related_jobs',
            'parse_emotional_jobs',
            'parse_social_jobs',
            'parse_financial_metrics_of_purchasing_decision_makers',
            'parse_ideal_job_state',
            'parse_potential_root_causes_preventing_the_ideal_state'
        ]

        for method in parse_methods:
            parse_fn = getattr(self.prompt_parser, method)
            result = parse_fn(response)
            # Expected result for parsing methods
            self.assertEqual(result, [
                {"name": "Improving Data Security", "description": "Developing security protocols for data."},
                {"name": "Enhancing System Scalability", "description": "Increasing the system's capacity to handle growth."}
            ])


if __name__ == '__main__':
    unittest.main()
