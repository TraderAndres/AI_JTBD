# tests/test_downstream_processor.py

import unittest
from unittest.mock import MagicMock
from anytree import Node, PreOrderIter
from downstream_processor import DownstreamProcessor
from prompt_builder import PromptBuilder
from llm_interface import LLMInterface

class TestDownstreamProcessor(unittest.TestCase):
    def setUp(self):
        # Initialize PromptBuilder and LLMInterface with mocked responses
        self.prompt_builder = PromptBuilder(prompts_dir='prompts')
        self.llm = LLMInterface()

        # Define a dictionary to map prompts to mocked responses
        def mock_get_response(prompt, temperature=0.1):
            prompt_lower = prompt.lower()
            # job contexts
            if "The term context in problem-solving refers to the surrounding information".lower() in prompt_lower:  
                return """
                1. **IT Managed Services Provider** - A company looking to outsource the management of their IT infrastructure.
                2. **Network Security Specialist** - An individual focused on protecting the organization's network from cyber threats.
                """
            # job map
            elif "with a deep expertise in Jobs-to-be-Done theory, which you will use here. As you know, Jobs have steps, much like a process, but they do not indicate how the".lower() in prompt_lower:  
                return """
                1. **Infrastructure Engineer** - Designs and maintains the IT infrastructure.
                2. **DevOps Engineer** - Bridges the gap between development and operations.
                """
            # desired outcomes
            elif "with a deep expertise in Jobs-to-be-Done theory. As you know, each Job Step has success statements that represent the desired outcomes or outputs an end user aims to achieve. For each Step submitted for the job ".lower() in prompt_lower:
                return """
                1. **Improved Efficiency** - Streamlining operations to reduce costs and increase productivity.
                2. **Enhanced Security** - Strengthening security measures to protect data and assets.
                """
            # themed desired outcomes
            elif "please generate a list of themed success statements that a(n)".lower() in prompt_lower:
                return """
                1. **Customer Satisfaction** - Ensuring customers are happy with the services provided.
                2. **Operational Excellence** - Achieving high standards in operational processes.
                """
            # emotional jobs
            elif "Generate a complete list of emotions that can be experienced while".lower() in prompt_lower:
                return """
                1. **Building Trust** - Establishing a trustworthy relationship with clients.
                2. **Reducing Anxiety** - Helping clients feel secure about their financial decisions.
                """
            # social jobs
            elif "Generate a complete list of positive perceptions you want others to have of you while".lower() in prompt_lower:
                return """
                1. **Networking** - Connecting with industry peers and potential clients.
                2. **Community Engagement** - Participating in community events and initiatives.
                """
            # Add more conditions as needed for other steps
            else:
                return ""

        # Mock the get_response method to return responses based on the prompt content
        self.llm.get_response = MagicMock(side_effect=mock_get_response)

        self.downstream_processor = DownstreamProcessor(self.prompt_builder, self.llm)

    def verify_hierarchy(self, actual_node, expected_structure):
        """
        Recursively verifies that the actual_node's children match the expected_structure.

        :param actual_node: The anytree.Node to verify.
        :param expected_structure: A list of dictionaries representing the expected hierarchy.
        """
        for expected_child in expected_structure:
            # Find the actual child node with the expected name
            actual_child = next((child for child in actual_node.children if child.name == expected_child['name']), None)
            self.assertIsNotNone(actual_child, f"Expected child '{expected_child['name']}' not found under '{actual_node.name}'.")
            self.assertEqual(actual_child.description, expected_child['description'],
                             f"Description mismatch for '{actual_child.name}'.")
            self.assertFalse(actual_child.processed, f"Child node '{actual_child.name}' should not be marked as processed.")

            # If the expected child has its own children, recursively verify
            if 'children' in expected_child and expected_child['children']:
                self.verify_hierarchy(actual_child, expected_child['children'])

    def test_full_hierarchy_building(self):
        """
        Integration test to verify processing of multiple downstream steps and building a comprehensive hierarchy.
        """
        # Create a node hierarchy with two parent levels:
        # Root -> Department -> High-Level Job
        root = Node(
            "Finance",
            description="Handles all financial operations.",
            processed=False
        )
        banking_department = Node(
            "Banking Department",
            parent=root,
            description="Manages banking-related services.",
            processed=False
        )
        account_manager = Node(
            "Account Manager",
            parent=banking_department,
            description="Responsible for managing client accounts and relationships.",
            processed=False
        )

        # Process 'Job Contexts' on 'Account Manager'
        self.downstream_processor.process_job_contexts(
            account_manager, n=2, fidelity='high', temp=0.1
        )

        # Process 'Job Map' on 'Account Manager'
        self.downstream_processor.process_job_map(
            account_manager, fidelity='high', temp=0.1
        )

        # Process 'Emotional Jobs' on 'Account Manager'
        self.downstream_processor.process_emotional_jobs(
            account_manager, n=2, fidelity='high', temp=0.1
        )

        # Process 'Social Jobs' on 'Account Manager'
        self.downstream_processor.process_social_jobs(
            account_manager, n=2, fidelity='high', temp=0.1
        )

        # Process 'Desired Outcomes Success Metrics' on each Job Context
        for context_node in account_manager.children[:2]:  # First two children are 'Job Contexts'
            self.downstream_processor.process_desired_outcomes(
                context_node, n=2, fidelity='high', temp=0.1
            )
            self.downstream_processor.process_themed_desired_outcomes(
                context_node, n=2, fidelity='high', temp=0.1
            )

        # Define the expected hierarchy structure
        expected_hierarchy = [
            {
                'name': 'IT Managed Services Provider',
                'description': 'A company looking to outsource the management of their IT infrastructure.',
                'children': [
                    {
                        'name': 'Desired Outcomes Success Metrics',
                        'description': '',
                        'children': [
                            {
                                'name': 'Improved Efficiency',
                                'description': 'Streamlining operations to reduce costs and increase productivity.'
                            },
                            {
                                'name': 'Enhanced Security',
                                'description': 'Strengthening security measures to protect data and assets.'
                            }
                        ]
                    },
                    {
                        'name': 'Themed Desired Outcomes Themed Success Metrics',
                        'description': '',
                        'children': [
                            {
                                'name': 'Customer Satisfaction',
                                'description': 'Ensuring customers are happy with the services provided.'
                            },
                            {
                                'name': 'Operational Excellence',
                                'description': 'Achieving high standards in operational processes.'
                            }
                        ]
                    }
                ]
            },
            {
                'name': 'Network Security Specialist',
                'description': "An individual focused on protecting the organization's network from cyber threats.",
                'children': [
                    {
                        'name': 'Desired Outcomes Success Metrics',
                        'description': '',
                        'children': [
                            {
                                'name': 'Improved Efficiency',
                                'description': 'Streamlining operations to reduce costs and increase productivity.'
                            },
                            {
                                'name': 'Enhanced Security',
                                'description': 'Strengthening security measures to protect data and assets.'
                            }
                        ]
                    },
                    {
                        'name': 'Themed Desired Outcomes Themed Success Metrics',
                        'description': '',
                        'children': [
                            {
                                'name': 'Customer Satisfaction',
                                'description': 'Ensuring customers are happy with the services provided.'
                            },
                            {
                                'name': 'Operational Excellence',
                                'description': 'Achieving high standards in operational processes.'
                            }
                        ]
                    }
                ]
            },
            {
                'name': 'Infrastructure Engineer',
                'description': 'Designs and maintains the IT infrastructure.',
                'children': []
            },
            {
                'name': 'DevOps Engineer',
                'description': 'Bridges the gap between development and operations.',
                'children': []
            },
            {
                'name': 'Emotional Jobs',
                'description': '',
                'children': [
                    {
                        'name': 'Building Trust',
                        'description': 'Establishing a trustworthy relationship with clients.'
                    },
                    {
                        'name': 'Reducing Anxiety',
                        'description': 'Helping clients feel secure about their financial decisions.'
                    }
                ]
            },
            {
                'name': 'Social Jobs',
                'description': '',
                'children': [
                    {
                        'name': 'Networking',
                        'description': 'Connecting with industry peers and potential clients.'
                    },
                    {
                        'name': 'Community Engagement',
                        'description': 'Participating in community events and initiatives.'
                    }
                ]
            }
        ]

        # Traverse the 'Account Manager' node and verify its hierarchy
        self.verify_hierarchy(account_manager, expected_hierarchy)

if __name__ == '__main__':
    unittest.main()
