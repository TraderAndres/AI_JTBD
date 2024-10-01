# tests/test_downstream_processor.py

import unittest
from unittest.mock import MagicMock
from anytree import Node
from downstream_processor import DownstreamProcessor
from prompt_builder import PromptBuilder
from llm_interface import LLMInterface

class TestDownstreamProcessor(unittest.TestCase):
    def setUp(self):
        # Initialize PromptBuilder and LLMInterface with mocked responses
        self.prompt_builder = PromptBuilder(prompts_dir='prompts')
        self.llm = LLMInterface()
        self.llm.get_response = MagicMock(return_value="""
        1. **IT Managed Services Provider** - A company looking to outsource the management of their IT infrastructure.
        2. **Network Security Specialist** - An individual focused on protecting the organization's network from cyber threats.
        """)
        self.downstream_processor = DownstreamProcessor(self.prompt_builder, self.llm)

    # def test_process_job_contexts(self):
    #     # Create a real node hierarchy with three levels
    #     engineering_department = Node(
    #         "Engineering Department",
    #         description="Handles all engineering-related tasks.",
    #         processed=False
    #     )
    #     devops_engineer = Node(
    #         "DevOps Engineer",
    #         parent=engineering_department,
    #         description="Responsible for overseeing the deployment and integration of software systems.",
    #         processed=False
    #     )
    #     building_systems = Node(
    #         "Building Systems",
    #         parent=devops_engineer,
    #         description="Responsible for ensuring system reliability.",
    #         processed=False
    #     )

    #     # Invoke the method under test
    #     parsed_response = self.downstream_processor.process_job_contexts(
    #         building_systems, n=2, fidelity='high', temp=0.1
    #     )

    #     # Check if LLM was called correctly
    #     self.llm.get_response.assert_called_once()

    #     # Check if node.processed is set to True
    #     self.assertTrue(building_systems.processed)

    #     # Check if downstream tasks were added (2 children in this case)
    #     self.assertEqual(len(building_systems.children), 2)

    #     # Verify the names and descriptions of the added children
    #     expected_children = [
    #         {
    #             'name': 'IT Managed Services Provider',
    #             'description': 'A company looking to outsource the management of their IT infrastructure.'
    #         },
    #         {
    #             'name': 'Network Security Specialist',
    #             'description': "An individual focused on protecting the organization's network from cyber threats."
    #         }
    #     ]

    #     for child, expected in zip(building_systems.children, expected_children):
    #         self.assertEqual(child.name, expected['name'])
    #         self.assertEqual(child.description, expected['description'])

    #     # Optionally, verify that 'processed' is False for new child nodes
    #     for child in building_systems.children:
    #         self.assertFalse(child.processed)

    def test_process_job_contexts(self):
        """
        Test processing of the 'Job Contexts' step on a high-level job node.
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

        # Invoke the method under test: Process 'Job Contexts' on 'Account Manager'
        self.downstream_processor.process_job_contexts(
            account_manager, n=2, fidelity='high', temp=0.1
        )

        # Check if LLM was called correctly
        self.llm.get_response.assert_called_once()

        # Check if 'Account Manager' node is marked as processed
        self.assertTrue(account_manager.processed, "'Account Manager' node should be marked as processed.")

        # Check if downstream tasks were added (2 children in this case)
        self.assertEqual(len(account_manager.children), 2, "There should be exactly 2 child nodes added.")

        # Define the expected children
        expected_children = [
            {
                'name': 'IT Managed Services Provider',
                'description': 'A company looking to outsource the management of their IT infrastructure.'
            },
            {
                'name': 'Network Security Specialist',
                'description': "An individual focused on protecting the organization's network from cyber threats."
            }
        ]

        # Verify the names and descriptions of the added children
        for child, expected in zip(account_manager.children, expected_children):
            with self.subTest(child=child.name):
                self.assertEqual(child.name, expected['name'], f"Child node name should be '{expected['name']}'.")
                self.assertEqual(child.description, expected['description'], f"Child node description should be '{expected['description']}'.")

        # Optionally, verify that 'processed' is False for new child nodes
        for child in account_manager.children:
            self.assertFalse(child.processed, f"Child node '{child.name}' should not be marked as processed.")

if __name__ == '__main__':
    unittest.main()
