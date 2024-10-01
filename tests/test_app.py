# tests/test_app.py
import logging

import unittest
from unittest.mock import MagicMock, patch
from anytree import Node, RenderTree

from app import process_job, display_job_selection  # Ensure process_job is correctly imported from app.py

logging.basicConfig(level=logging.DEBUG)


class TestDisplayJobSelection(unittest.TestCase):

    @patch('app.st')
    def test_display_job_selection_no_jobs(self, mock_st):
        """
        Test display_job_selection when there are no jobs available.
        """
        mock_hierarchy_builder = MagicMock()
        mock_hierarchy_builder.job_nodes = []

        # Mock downstream_processor and visualizer
        mock_downstream_processor = MagicMock()
        mock_visualizer = MagicMock()

        # Call the function
        display_job_selection(mock_hierarchy_builder, mock_downstream_processor, mock_visualizer)

        # Assert that a warning is displayed
        mock_st.warning.assert_called_with("No Jobs available for selection.")
        mock_st.text_input.assert_not_called()
        mock_st.multiselect.assert_not_called()
        mock_st.button.assert_not_called()

    @patch('app.st')
    def test_display_job_selection_with_jobs_no_selection(self, mock_st):
        """
        Test display_job_selection with available jobs but no selection made.
        """
        # Create sample job nodes
        job1 = Node("Job1", parent=None, description="Description1", processed=False)
        job2 = Node("Job2", parent=None, description="Description2", processed=False)

        # Mock hierarchy_builder with job_nodes
        mock_hierarchy_builder = MagicMock()
        mock_hierarchy_builder.job_nodes = [job1, job2]
        mock_hierarchy_builder.industry = "Finance"
        mock_hierarchy_builder.fidelity = "high"
        mock_hierarchy_builder.root = Node("High Level Job")

        # Create job paths directly as real data instead of using mock objects
        job_paths = ["/High Level Job/Job1", "/High Level Job/Job2"]

        # Mock downstream_processor and visualizer
        mock_downstream_processor = MagicMock()
        mock_visualizer = MagicMock()

        # Configure Streamlit mocks
        mock_st.text_input.return_value = ""
        mock_st.multiselect.return_value = []
        mock_st.button.return_value = False  # Simulate button not clicked

        # Call the function with real job paths instead of mock objects
        display_job_selection(mock_hierarchy_builder, mock_downstream_processor, mock_visualizer)

        # Assert that Streamlit components are called correctly
        mock_st.header.assert_called_with("Select Jobs for Further Processing")
        mock_st.text_input.assert_called_with("Search Jobs")
        mock_st.multiselect.assert_called()
        mock_st.button.assert_called_with("Process Selected Jobs")

        # Ensure process_job is not called since no jobs are selected
        mock_downstream_processor.process_job.assert_not_called()


    # @patch('app.st')
    # def test_display_job_selection_with_jobs_and_selection(self, mock_st):
    #     """
    #     Test display_job_selection with available jobs and some selection made.
    #     """
    #     # Create sample job nodes with proper parent-child relationships
    #     high_level_job = Node("High Level Job")  # Root node
    #     job1 = Node("Job1", parent=high_level_job, description="Description1", processed=False)
    #     job2 = Node("Job2", parent=high_level_job, description="Description2", processed=False)

    #     # Mock hierarchy_builder with job_nodes
    #     mock_hierarchy_builder = MagicMock()
    #     mock_hierarchy_builder.job_nodes = [job1, job2]  # Set up with a list of nodes
    #     mock_hierarchy_builder.industry = "Finance"
    #     mock_hierarchy_builder.fidelity = "high"
    #     mock_hierarchy_builder.root = high_level_job  # Set root as the top-level job

    #     # Mock downstream_processor and visualizer
    #     mock_downstream_processor = MagicMock()
    #     mock_visualizer = MagicMock()

    #     # Create the expected job paths
    #     job_paths = ["High Level Job/Job1", "High Level Job/Job2"]

    #     # Configure Streamlit mocks
    #     mock_st.text_input.return_value = "Job"
    #     mock_st.multiselect.return_value = ["High Level Job/Job1"]
    #     mock_st.button.return_value = True  # Simulate button clicked

    #     # Call the function
    #     display_job_selection(mock_hierarchy_builder, mock_downstream_processor, mock_visualizer)

    #     # Verify that the job_paths generated in display_job_selection match the expected paths
    #     expected_paths = ["/".join([ancestor.name for ancestor in job.path]) for job in [job1, job2]]
    #     assert expected_paths == job_paths, f"Expected paths: {job_paths}, but got: {expected_paths}"

    #     # Debugging: Print the actual call arguments
    #     logging.debug("Actual process_job calls: ", mock_downstream_processor.process_job.call_args_list)

    #     # Print more detailed call information
    #     for call in mock_downstream_processor.process_job.call_args_list:
    #         print(f"Call details: {call}")

    #     # Assert that Streamlit components are called correctly
    #     mock_st.header.assert_called_with("Select Jobs for Further Processing")
    #     mock_st.text_input.assert_called_with("Search Jobs")
    #     mock_st.multiselect.assert_called_with("Select Jobs to Process", options=job_paths)
    #     mock_st.button.assert_called_with("Process Selected Jobs")

    #     # Assert that process_job is called with the correct job node
    #     mock_downstream_processor.process_job.assert_any_call(
    #         job_node=job1,
    #         downstream_processor=mock_downstream_processor,
    #         hierarchy_builder=mock_hierarchy_builder,
    #         visualizer=mock_visualizer
    #     )

    #     # Assert that hierarchy is saved correctly
    #     mock_st.success.assert_called_with("Selected Jobs have been processed and hierarchy updated.")
    #     mock_visualizer.display_hierarchy.assert_called_with(mock_hierarchy_builder.root)




    # @patch('app.st')
    # def test_display_job_selection_with_jobs_and_multiple_selection(self, mock_st):
    #     """
    #     Test display_job_selection with multiple job selections.
    #     """
    #     # Create sample job nodes
    #     job1 = Node("Job1", parent=None, description="Description1", processed=False)
    #     job2 = Node("Job2", parent=None, description="Description2", processed=False)
    #     job3 = Node("Job3", parent=None, description="Description3", processed=False)

    #     # Mock hierarchy_builder with job_nodes
    #     mock_hierarchy_builder = MagicMock()
    #     mock_hierarchy_builder.job_nodes = [job1, job2, job3]
    #     mock_hierarchy_builder.industry = "Finance"
    #     mock_hierarchy_builder.fidelity = "high"
    #     mock_hierarchy_builder.root = Node("High Level Job")

    #     # Create job paths directly as real data
    #     job_paths = ["/High Level Job/Job1", "/High Level Job/Job2", "/High Level Job/Job3"]

    #     # Mock downstream_processor and visualizer
    #     mock_downstream_processor = MagicMock()
    #     mock_visualizer = MagicMock()

    #     # Configure Streamlit mocks
    #     mock_st.text_input.return_value = "Job"
    #     mock_st.multiselect.return_value = [job_paths[0], job_paths[2]]  # Select Job1 and Job3
    #     mock_st.button.return_value = True  # Simulate button clicked

    #     # Call the function with real job paths instead of mock objects
    #     display_job_selection(mock_hierarchy_builder, mock_downstream_processor, mock_visualizer)

    #     # Assert that Streamlit components are called correctly
    #     mock_st.header.assert_called_with("Select Jobs for Further Processing")
    #     mock_st.text_input.assert_called_with("Search Jobs")
    #     mock_st.multiselect.assert_called_with("Select Jobs to Process", options=job_paths)
    #     mock_st.button.assert_called_with("Process Selected Jobs")

    #     # Assert that process_job is called with the correct job nodes
    #     expected_calls = [
    #         unittest.mock.call(
    #             job_node=job1,
    #             downstream_processor=mock_downstream_processor,
    #             hierarchy_builder=mock_hierarchy_builder,
    #             visualizer=mock_visualizer
    #         ),
    #         unittest.mock.call(
    #             job_node=job3,
    #             downstream_processor=mock_downstream_processor,
    #             hierarchy_builder=mock_hierarchy_builder,
    #             visualizer=mock_visualizer
    #         )
    #     ]
    #     self.assertEqual(mock_downstream_processor.process_job.call_count, 2)
    #     mock_downstream_processor.process_job.assert_has_calls(expected_calls, any_order=True)

    #     # Assert that hierarchy is saved correctly
    #     mock_st.success.assert_called_with("Selected Jobs have been processed and hierarchy updated.")
    #     mock_visualizer.display_hierarchy.assert_called_with(mock_hierarchy_builder.root)


class TestApp(unittest.TestCase):

    def setUp(self):
        # Create the root job node
        self.root_job = Node("High Level Job",
                             description="Root of the job hierarchy",
                             processed=False)

        # Mock downstream_processor with methods that add child nodes
        self.downstream_processor = MagicMock()

        # Define side effects for each processing method
        def process_job_contexts(node, n, fidelity, temp):
            logging.debug(f"Mock: Adding 'Job Contexts' under '{node.name}'")
            # Add 'Job Contexts' as a child with processed=False
            job_contexts = Node(
                "Job Contexts",
                parent=node,
                description="Handles job contexts",
                processed=False  # Set to False for further processing
            )

        def process_job_map(node, n, fidelity, temp):
            logging.debug(f"Mock: Adding 'Job Map' under '{node.name}'")
            # Add 'Job Map' as a child under 'Job Contexts' with processed=False
            job_map = Node("Job Map",
                           parent=node,
                           description="Handles job mapping",
                           processed=False)

        def process_desired_outcomes_success_metrics(node, n, fidelity, temp):
            logging.debug(
                f"Mock: Adding 'Desired Outcomes' under '{node.name}'")
            # Add 'Desired Outcomes (success metrics)' under 'Job Map' with processed=False
            desired_outcomes = Node("Desired Outcomes (success metrics)",
                                    parent=node,
                                    description="Handles desired outcomes",
                                    processed=False)

        def process_themed_desired_outcomes_themed_success_metrics(
                node, n, fidelity, temp):
            logging.debug(f"Mock: Adding 'Themed Success Metrics' under '{node.name}'")
            # Add 'Themed Desired Outcomes (Themed Success Metrics)' under 'Job Map' with processed=False
            themed_desired_outcomes = Node(
                "Themed Desired Outcomes (Themed Success Metrics)",
                parent=node,
                description="Handles themed desired outcomes",
                processed=False)

        def process_situational_complexity_factors(node, n, fidelity, temp):
            logging.debug(f"Mock: Adding 'Situational and Complexity factors' under '{node.name}'")
            # Add 'Situational and Complexity Factors' under 'Job Contexts' with processed=False
            situational_factors = Node(
                "Situational and Complexity Factors",
                parent=node,
                description="Handles situational factors",
                processed=False)

        def process_related_jobs(node, n, fidelity, temp):
            logging.debug(f"Mock: Adding 'Related Jobs' under '{node.name}'")
            # Add 'Related Jobs' under 'Job Contexts' with processed=False
            related_jobs = Node("Related Jobs",
                                parent=node,
                                description="Handles related jobs",
                                processed=False)

        def process_emotional_jobs(node, n, fidelity, temp):
            logging.debug(f"Mock: Adding 'Emotional Jobs' under '{node.name}'")
            # Add 'Emotional Jobs' under 'Job Contexts' with processed=False
            emotional_jobs = Node("Emotional Jobs",
                                  parent=node,
                                  description="Handles emotional jobs",
                                  processed=False)

        def process_social_jobs(node, n, fidelity, temp):
            logging.debug(f"Mock: Adding 'Social Jobs' under '{node.name}'")
            # Add 'Social Jobs' under 'Job Contexts' with processed=False
            social_jobs = Node("Social Jobs",
                               parent=node,
                               description="Handles social jobs",
                               processed=False)

        def process_financial_metrics_of_purchasing_decision_makers(
                node, n, fidelity, temp):
            logging.debug(f"Mock: Adding 'Financial Metrics' under '{node.name}'")
            # Add 'Financial Metrics of Purchasing Decision Makers' under 'Job Contexts' with processed=False
            financial_metrics = Node(
                "Financial Metrics of Purchasing Decision Makers",
                parent=node,
                description="Handles financial metrics",
                processed=False)

        def process_ideal_job_state(node, n, fidelity, temp):
            logging.debug(f"Mock: Adding 'Ideal Job State' under '{node.name}'")
            # Add 'Ideal Job State' under 'Job Contexts' with processed=False
            ideal_job_state = Node("Ideal Job State",
                                   parent=node,
                                   description="Handles ideal job state",
                                   processed=False)

        def process_potential_root_causes_preventing_the_ideal_state(
                node, n, fidelity, temp):
            logging.debug(f"Mock: Adding 'Potential Root Causes' under '{node.name}'")
            # Add 'Potential Root Causes Preventing the Ideal State' under 'Ideal Job State' with processed=False
            root_causes = Node(
                "Potential Root Causes Preventing the Ideal State",
                parent=node,
                description="Handles root causes",
                processed=False)

        # Assign side effects to the mocked methods
        self.downstream_processor.process_job_contexts.side_effect = process_job_contexts
        self.downstream_processor.process_job_map.side_effect = process_job_map
        self.downstream_processor.process_desired_outcomes_success_metrics.side_effect = process_desired_outcomes_success_metrics
        self.downstream_processor.process_themed_desired_outcomes_themed_success_metrics.side_effect = process_themed_desired_outcomes_themed_success_metrics
        self.downstream_processor.process_situational_complexity_factors.side_effect = process_situational_complexity_factors
        self.downstream_processor.process_related_jobs.side_effect = process_related_jobs
        self.downstream_processor.process_emotional_jobs.side_effect = process_emotional_jobs
        self.downstream_processor.process_social_jobs.side_effect = process_social_jobs
        self.downstream_processor.process_financial_metrics_of_purchasing_decision_makers.side_effect = process_financial_metrics_of_purchasing_decision_makers
        self.downstream_processor.process_ideal_job_state.side_effect = process_ideal_job_state
        self.downstream_processor.process_potential_root_causes_preventing_the_ideal_state.side_effect = process_potential_root_causes_preventing_the_ideal_state

        # Mock hierarchy_builder and visualizer if needed
        self.hierarchy_builder = MagicMock()
        self.visualizer = MagicMock()

    def test_process_job_hierarchy(self):
        # Invoke process_job
        process_job(job_node=self.root_job,
                    downstream_processor=self.downstream_processor,
                    hierarchy_builder=self.hierarchy_builder,
                    visualizer=self.visualizer)

        # Verify the hierarchy
        self.assertEqual(len(self.root_job.children), 1)
        job_contexts = self.root_job.children[0]
        self.assertEqual(job_contexts.name, "Job Contexts")
        self.assertEqual(len(job_contexts.children),
                         7)  # Expecting 7 children under 'Job Contexts'

        # Verify 'Job Map' under 'Job Contexts'
        job_map = next(
            (child
             for child in job_contexts.children if child.name == "Job Map"),
            None)
        self.assertIsNotNone(job_map,
                             "'Job Map' should be a child of 'Job Contexts'")
        self.assertEqual(len(job_map.children),
                         2)  # 'Desired Outcomes' and 'Themed Desired Outcomes'
        desired_outcomes = next((child for child in job_map.children
                                 if child.name == "Desired Outcomes (success metrics)"), None)
        self.assertIsNotNone(
            desired_outcomes,
            "'Desired Outcomes (success metrics)' should be a child of 'Job Map'"
        )
        self.assertEqual(desired_outcomes.description,
                         "Handles desired outcomes")
        self.assertEqual(len(desired_outcomes.children),
                         0)  # Further children not mocked here

        themed_desired_outcomes = next(
            (child for child in job_map.children if child.name ==
             "Themed Desired Outcomes (Themed Success Metrics)"), None)
        self.assertIsNotNone(
            themed_desired_outcomes,
            "'Themed Desired Outcomes (Themed Success Metrics)' should be a child of 'Job Map'"
        )
        self.assertEqual(themed_desired_outcomes.description,
                         "Handles themed desired outcomes")
        self.assertEqual(len(themed_desired_outcomes.children), 0)

        # Verify 'Potential Root Causes Preventing the Ideal State' under 'Ideal Job State'
        ideal_job_state = next((child for child in job_contexts.children
                                if child.name == "Ideal Job State"), None)
        self.assertIsNotNone(
            ideal_job_state,
            "'Ideal Job State' should be a child of 'Job Contexts'")
        self.assertEqual(len(ideal_job_state.children), 1)
        root_causes = ideal_job_state.children[0]
        self.assertEqual(root_causes.name,
                         "Potential Root Causes Preventing the Ideal State")
        self.assertEqual(root_causes.description, "Handles root causes")
        self.assertEqual(len(root_causes.children), 0)

        # Verify other children under 'Job Contexts'
        situational_factors = next(
            (child for child in job_contexts.children
             if child.name == "Situational and Complexity Factors"), None)
        self.assertIsNotNone(
            situational_factors,
            "'Situational and Complexity Factors' should be a child of 'Job Contexts'"
        )
        self.assertEqual(situational_factors.description,
                         "Handles situational factors")
        self.assertEqual(len(situational_factors.children), 0)

        related_jobs = next((child for child in job_contexts.children
                             if child.name == "Related Jobs"), None)
        self.assertIsNotNone(
            related_jobs, "'Related Jobs' should be a child of 'Job Contexts'")
        self.assertEqual(related_jobs.description, "Handles related jobs")
        self.assertEqual(len(related_jobs.children), 0)

        emotional_jobs = next((child for child in job_contexts.children
                               if child.name == "Emotional Jobs"), None)
        self.assertIsNotNone(
            emotional_jobs,
            "'Emotional Jobs' should be a child of 'Job Contexts'")
        self.assertEqual(emotional_jobs.description, "Handles emotional jobs")
        self.assertEqual(len(emotional_jobs.children), 0)

        social_jobs = next((child for child in job_contexts.children
                            if child.name == "Social Jobs"), None)
        self.assertIsNotNone(
            social_jobs, "'Social Jobs' should be a child of 'Job Contexts'")
        self.assertEqual(social_jobs.description, "Handles social jobs")
        self.assertEqual(len(social_jobs.children), 0)

        financial_metrics = next(
            (child for child in job_contexts.children
             if child.name == "Financial Metrics of Purchasing Decision Makers"
             ), None)
        self.assertIsNotNone(
            financial_metrics,
            "'Financial Metrics of Purchasing Decision Makers' should be a child of 'Job Contexts'"
        )
        self.assertEqual(financial_metrics.description,
                         "Handles financial metrics")
        self.assertEqual(len(financial_metrics.children), 0)

        # Optionally, verify that visualizer was called
        self.visualizer.display_hierarchy.assert_called_once()

        # Optionally, print the tree for visual inspection (uncomment if needed)
        # for pre, fill, node in RenderTree(self.root_job):
        #     print("%s%s" % (pre, node.name))


if __name__ == '__main__':
    unittest.main()
