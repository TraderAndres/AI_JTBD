# test_console_app.py

import unittest
from unittest.mock import MagicMock, patch
from anytree import Node
from console_app import load_hierarchy, save_hierarchy, get_job_nodes, process_node, display_leaf_nodes, select_node_for_processing, process_steps

class TestConsoleApp(unittest.TestCase):

    def setUp(self):
        """
        Create a mock hierarchy and downstream processor to be used in tests.
        """
        # Create a mock hierarchy with a leaf node
        self.root = Node("Finance", processed=False, description="Finance sector")
        banking = Node("Banking", parent=self.root, processed=False, description="Banking industry")
        retail_banking = Node("Retail Banking", parent=banking, processed=False, description="Retail Banking segment")
        end_users_providers = Node("End Users - Providers", parent=retail_banking, processed=False, description="Providers of banking services")
        self.mock_leaf_node = Node("Providing Financial Solutions", parent=end_users_providers, processed=False, description="Mock Leaf Node")

        # Mock downstream processor with all methods
        self.mock_downstream_processor = MagicMock()

        # Add mock methods to simulate creating children nodes
        def mock_process_job_contexts(node, n, fidelity, temp):
            Node("Job Map", parent=node, description="Mock Job Map node", processed=False)

        def mock_process_job_map(node, fidelity, temp):
            Node("Desired Outcomes", parent=node, description="Mock Desired Outcomes node", processed=False)

        def mock_process_desired_outcomes_success_metrics(node, n, fidelity, temp):
            Node("Themed Desired Outcomes", parent=node, description="Mock Themed Desired Outcomes node", processed=False)

        # Assign side effects to each mock method
        self.mock_downstream_processor.process_job_contexts.side_effect = mock_process_job_contexts
        self.mock_downstream_processor.process_job_map.side_effect = mock_process_job_map
        self.mock_downstream_processor.process_desired_outcomes_success_metrics.side_effect = mock_process_desired_outcomes_success_metrics
        # Correct mock names
        # self.mock_downstream_processor.process_themed_desired_outcomes_themed_success_metrics.side_effect = mock_process_themed_desired_outcomes
        # self.mock_downstream_processor.process_situational_complexity_factors.side_effect = mock_process_situational_complexity_factors
        # self.mock_downstream_processor.process_related_jobs.side_effect = mock_process_related_jobs
        # self.mock_downstream_processor.process_emotional_jobs.side_effect = mock_process_emotional_jobs
        # self.mock_downstream_processor.process_social_jobs.side_effect = mock_process_social_jobs
        # self.mock_downstream_processor.process_financial_metrics_of_purchasing_decision_makers.side_effect = mock_process_financial_metrics
        # self.mock_downstream_processor.process_ideal_job_state.side_effect = mock_process_ideal_job_state




    def test_load_hierarchy(self):
        """
        Test that the hierarchy loads correctly from a JSON file.
        """
        with patch("builtins.open", unittest.mock.mock_open(read_data='{"name": "Finance"}')), \
             patch("json.load", return_value={"name": "Finance"}):
            root_node = load_hierarchy("mock_hierarchy.json")
            self.assertEqual(root_node.name, "Finance")

    def test_save_hierarchy(self):
        """
        Test that the hierarchy saves correctly to a JSON file.
        """
        with patch("json.dump") as mock_json_dump, \
             patch("builtins.open", unittest.mock.mock_open()):
            save_hierarchy(self.root, "mock_hierarchy.json")
            mock_json_dump.assert_called_once()

    def test_get_job_nodes(self):
        """
        Test that only leaf nodes are returned as job nodes.
        """
        leaf_nodes = get_job_nodes(self.root)
        self.assertEqual(len(leaf_nodes), 1)
        self.assertEqual(leaf_nodes[0].name, "Providing Financial Solutions")

    def test_process_node(self):
        """
        Test that process_node correctly processes the node with mock downstream steps.
        """
        process_node(self.mock_leaf_node, self.mock_downstream_processor)

        # Verify that process_job_contexts was called and a child was created
        self.mock_downstream_processor.process_job_contexts.assert_called()
        job_map_node = self.mock_leaf_node.children[-1]
        self.assertEqual(job_map_node.name, "Job Map")

        # Verify that process_job_map was called for the "Job Map" node
        self.mock_downstream_processor.process_job_map.assert_called_once_with(
            node=job_map_node, fidelity="comprehensive", temp=0.1
        )


    def test_process_steps(self):
        """
        Test the process_steps function with mock downstream processor.
        """
        # Define all steps in the hierarchy
        steps = [
            {
                'step': 'Job Contexts',
                'n': 10,
                'children_steps': [
                    {
                        'step': 'Job Map',
                        'n': 0,
                        'children_steps': [
                            {'step': 'Desired Outcomes (success metrics)', 'n': 20},
                            {'step': 'Themed Desired Outcomes (Themed Success Metrics)', 'n': 10},
                        ]
                    },
                    {'step': 'Situational Complexity Factors', 'n': 10},
                    {'step': 'Related Jobs', 'n': 10},
                    {'step': 'Emotional Jobs', 'n': 10},
                    {'step': 'Social Jobs', 'n': 10},
                    {'step': 'Financial Metrics of Purchasing Decision Makers', 'n': 10},
                    {
                        'step': 'Ideal Job State',
                        'n': 15,
                        'children_steps': [
                            {'step': 'Potential Root Causes Preventing the Ideal State', 'n': 15},
                        ]
                    },
                ]
            }
        ]

        # Call process_steps with the mock leaf node and steps
        process_steps(self.mock_leaf_node, steps, self.mock_downstream_processor)

        # Verify that process_job_contexts was called once
        self.mock_downstream_processor.process_job_contexts.assert_called_once_with(
            node=self.mock_leaf_node, n=10, fidelity="comprehensive", temp=0.1
        )

        # Check that the first child was added correctly under "Providing Financial Solutions"
        job_map_node = self.mock_leaf_node.children[-1]
        self.assertEqual(job_map_node.name, "Job Map")

        # Verify that process_job_map was called with the new child node
        self.mock_downstream_processor.process_job_map.assert_called_once_with(
            node=job_map_node, fidelity="comprehensive", temp=0.1
        )

        # Track the new child node created under "Job Map"
        desired_outcomes_node = job_map_node.children[-1]
        self.assertEqual(desired_outcomes_node.name, "Desired Outcomes")

        # Verify that process_desired_outcomes_success_metrics was called with "Desired Outcomes" node
        self.mock_downstream_processor.process_desired_outcomes_success_metrics.assert_called_once_with(
            node=desired_outcomes_node, n=20, fidelity="comprehensive", temp=0.1
        )


        # Continue adding assertions as necessary to confirm the hierarchy is being built correctly



    def test_select_node_for_processing(self):
        """
        Test node selection for processing from mock user input.
        """
        with patch("builtins.input", return_value='1'):
            selected_node = select_node_for_processing(self.root)
            self.assertEqual(selected_node, self.mock_leaf_node)

    def test_display_leaf_nodes(self):
        """
        Test that leaf nodes are correctly displayed.
        """
        with patch("builtins.print") as mock_print:
            display_leaf_nodes(self.root)
            mock_print.assert_any_call("Finance -> Banking -> Retail Banking -> End Users - Providers -> Providing Financial Solutions (Processed: False)")

if __name__ == "__main__":
    unittest.main()
