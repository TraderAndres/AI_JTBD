# tests/test_processing.py

import unittest
from unittest.mock import MagicMock
from anytree import Node, PreOrderIter

from utils import node_to_dict, dict_to_tree
from prompt_builder import PromptBuilder
from llm_interface import LLMInterface
from hierarchy_builder import HierarchyBuilder
from downstream_processor import DownstreamProcessor
from visualizer import Visualizer


class TestProcessing(unittest.TestCase):
    def setUp(self):
        """
        Set up the necessary components for the integration test.
        """
        # Initialize PromptBuilder
        self.prompt_builder = PromptBuilder()

        # Initialize LLMInterface with mocked responses
        self.llm = LLMInterface()
        self.llm.get_response = MagicMock(side_effect=self.mock_llm_responses)

        # Initialize HierarchyBuilder
        self.hierarchy_builder = HierarchyBuilder(self.llm, self.prompt_builder)
        self.hierarchy_builder.fidelity = 'high'  # Set fidelity as needed

        # Initialize DownstreamProcessor
        self.downstream_processor = DownstreamProcessor(self.prompt_builder, self.llm)

        # Initialize Visualizer (optional, as it's Streamlit-based)
        self.visualizer = Visualizer()

        # Build a sample hierarchy
        self.root = Node(
            "Finance",
            description="Root node for industry hierarchy",
            processed=False
        )
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

        # Assign nodes as instance variables for accessibility in tests
        self.personal_banker = Node(
            "Personal Banker",
            parent=individual_consumers,
            description="Assists individuals with their banking needs.",
            processed=False
        )
        self.account_manager = Node(
            "Account Manager",
            parent=service_providers,
            description="Manages customer accounts and ensures satisfaction.",
            processed=False
        )
        self.business_consultant = Node(
            "Business Consultant",
            parent=small_businesses,
            description="Provides financial advice to small businesses.",
            processed=False
        )

    def mock_llm_responses(self, prompt, temperature=0.1):
        """
        Mock LLM responses based on the prompt content.
        This function returns predictable responses for testing.
        """
        # Define mock responses for different prompt types
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
        # situational and complexity factors
        elif "The situation will be rated by survey respondents on a scale of 1 through 5, where 1 will be the worst case and 5 being the best case.".lower() in prompt_lower:
            return """
            1. **Market Competition** - The level of competition in the financial sector.
            2. **Regulatory Compliance** - Adhering to financial regulations and standards.
            """
        # related jobs
        elif "Disregard context if it is not supplied. List related tasks or objectives that you have before, during, and after".lower() in prompt_lower:
            return """
            1. **Financial Advisor** - Provides financial planning and investment advice.
            2. **Loan Officer** - Evaluates and authorizes loan applications.
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
        # financial_metrics_of_purchasing_decision_makers
        elif "of a product or service evaluates competing offerings against a set of financial metrics when trying to decide which product or service to acquire.".lower() in prompt_lower:
            return """
            1. **Revenue Growth** - Increasing the company's income over time.
            2. **Profit Margins** - Enhancing the difference between revenue and costs.
            """
        # ideal job state
        elif "including its appearance, physical or tangible attributes, intangible attributes, its performance, what you want it to be free from, and what you would like to minimize or avoid in terms of maintenance, when using, installation, setup, risk, cost, time, waste, planning, and purchasing. Do not include solutions or activities in your output.".lower() in prompt_lower:
            return """
            1. **Seamless Integration** - Integrating financial tools effortlessly into existing systems.
            2. **Real-Time Analytics** - Providing immediate insights into financial data.
            """
        # potential_root_causes_preventing_the_ideal_state
        elif "potential root causes related to the inability of a(n)".lower() in prompt_lower:
            return """
            1. **Data Silos** - Fragmented data across different departments hindering comprehensive analysis.
            2. **Legacy Systems** - Outdated technology that is incompatible with modern financial tools.
            """
        else:
            return ""

    def verify_children(self, children, expected_children):
        """
        Helper method to verify that the actual children match the expected children.
        """
        self.assertEqual(len(children), len(expected_children), 
                         f"Expected {len(expected_children)} children, but found {len(children)}: {[child.name for child in children]}")
        for child, expected in zip(children, expected_children):
            self.assertEqual(child.name, expected['name'], 
                             f"Expected child name '{expected['name']}', but got '{child.name}'")
            self.assertEqual(child.description, expected['description'], 
                             f"Expected child description '{expected['description']}', but got '{child.description}'")
            self.assertFalse(child.processed, 
                             f"Child node '{child.name}' should not be processed yet.")

    def test_process_selected_jobs(self):
        """
        Integration test to verify processing selected jobs across all steps.
        """
        # Select specific job nodes to process
        selected_job_names = ["Personal Banker", "Account Manager"]
        selected_job_nodes = [node for node in PreOrderIter(self.root) if node.name in selected_job_names]

        # Diagnostic: Print selected job node names
        selected_names = [node.name for node in selected_job_nodes]
        print(f"Selected Job Nodes: {selected_names}")

        # Ensure selected_job_nodes are correctly identified
        self.assertEqual(len(selected_job_nodes), 2, 
                         f"Expected 2 nodes, but found {len(selected_job_nodes)}: {selected_names}")
        for node in selected_job_nodes:
            self.assertFalse(node.processed)

        # Define all processing steps
        steps = [
            {'method': 'process_job_contexts', 'args': {'n': 2, 'fidelity': self.hierarchy_builder.fidelity}},
            {'method': 'process_job_map', 'args': {'fidelity': self.hierarchy_builder.fidelity}},
            {'method': 'process_desired_outcomes', 'args': {'n': 2, 'fidelity': self.hierarchy_builder.fidelity}},
            {'method': 'process_themed_desired_outcomes', 'args': {'n': 2, 'fidelity': self.hierarchy_builder.fidelity}},
            {'method': 'process_situational_complexity_factors', 'args': {'n': 2, 'fidelity': self.hierarchy_builder.fidelity}},
            {'method': 'process_related_jobs', 'args': {'n': 2, 'fidelity': self.hierarchy_builder.fidelity}},
            {'method': 'process_emotional_jobs', 'args': {'n': 2, 'fidelity': self.hierarchy_builder.fidelity}},
            {'method': 'process_social_jobs', 'args': {'n': 2, 'fidelity': self.hierarchy_builder.fidelity}},
            {'method': 'process_financial_metrics', 'args': {'n': 2, 'temp': 0.1, 'fidelity': self.hierarchy_builder.fidelity}},
            {'method': 'process_ideal_job_state', 'args': {'n': 2, 'temp': 0.1, 'fidelity': self.hierarchy_builder.fidelity}},
            {'method': 'process_potential_root_causes', 'args': {'n': 2, 'temp': 0.1, 'fidelity': self.hierarchy_builder.fidelity}},
            # Add other steps as needed based on your DownstreamProcessor implementation
        ]

        # Process each selected job with all steps
        for job_node in selected_job_nodes:
            for step in steps:
                processing_method = getattr(self.downstream_processor, step['method'])
                processing_method(job_node, **step['args'])

        # Verify that the jobs are marked as processed
        for job_node in selected_job_nodes:
            self.assertTrue(job_node.processed)

        # Verify that downstream nodes are added correctly
        # For "Personal Banker"
        personal_banker_children = self.personal_banker.children
        expected_steps = [
            'job_contexts',
            'job_map',
            'desired_outcomes_(success_metrics)',
            'themed_desired_outcomes_(themed_success_metrics)',
            'situational_and_complexity_factors',
            'related_jobs',
            'emotional_jobs',
            'social_jobs',
            'financial_metrics_of_purchasing_decision_makers',
            'ideal_job_state',
            'potential_root_causes_preventing_the_ideal_state'
        ]
        # Each step adds 2 children
        expected_personal_banker_children = []
        for step in expected_steps:
            if step == 'financial_metrics_of_purchasing_decision_makers':
                expected_personal_banker_children.extend([
                    {
                        'name': 'Revenue Growth',
                        'description': "Increasing the company's income over time."
                    },
                    {
                        'name': 'Profit Margins',
                        'description': "Enhancing the difference between revenue and costs."
                    }
                ])
            elif step == 'job_map':
                expected_personal_banker_children.extend([
                    {
                        'name': 'Infrastructure Engineer',
                        'description': 'Designs and maintains the IT infrastructure.'
                    },
                    {
                        'name': 'DevOps Engineer',
                        'description': 'Bridges the gap between development and operations.'
                    }
                ])
            elif step == 'ideal_job_state':
                expected_personal_banker_children.extend([
                    {
                        'name': 'Seamless Integration',
                        'description': 'Integrating financial tools effortlessly into existing systems.'
                    },
                    {
                        'name': 'Real-Time Analytics',
                        'description': 'Providing immediate insights into financial data.'
                    }
                ])
            elif step == 'potential_root_causes_preventing_the_ideal_state':
                expected_personal_banker_children.extend([
                    {
                        'name': 'Data Silos',
                        'description': 'Fragmented data across different departments hindering comprehensive analysis.'
                    },
                    {
                        'name': 'Legacy Systems',
                        'description': 'Outdated technology that is incompatible with modern financial tools.'
                    }
                ])
            else:
                # Specific steps with known mock responses
                if step == 'job_contexts':
                    expected_personal_banker_children.extend([
                        {
                            'name': 'IT Managed Services Provider',
                            'description': 'A company looking to outsource the management of their IT infrastructure.'
                        },
                        {
                            'name': 'Network Security Specialist',
                            'description': "An individual focused on protecting the organization's network from cyber threats."
                        }
                    ])
                elif step == 'desired_outcomes_(success_metrics)':
                    expected_personal_banker_children.extend([
                        {
                            'name': 'Improved Efficiency',
                            'description': 'Streamlining operations to reduce costs and increase productivity.'
                        },
                        {
                            'name': 'Enhanced Security',
                            'description': 'Strengthening security measures to protect data and assets.'
                        }
                    ])
                elif step == 'themed_desired_outcomes_(themed_success_metrics)':
                    expected_personal_banker_children.extend([
                        {
                            'name': 'Customer Satisfaction',
                            'description': 'Ensuring customers are happy with the services provided.'
                        },
                        {
                            'name': 'Operational Excellence',
                            'description': 'Achieving high standards in operational processes.'
                        }
                    ])
                elif step == 'situational_and_complexity_factors':
                    expected_personal_banker_children.extend([
                        {
                            'name': 'Market Competition',
                            'description': 'The level of competition in the financial sector.'
                        },
                        {
                            'name': 'Regulatory Compliance',
                            'description': 'Adhering to financial regulations and standards.'
                        }
                    ])
                elif step == 'related_jobs':
                    expected_personal_banker_children.extend([
                        {
                            'name': 'Financial Advisor',
                            'description': 'Provides financial planning and investment advice.'
                        },
                        {
                            'name': 'Loan Officer',
                            'description': 'Evaluates and authorizes loan applications.'
                        }
                    ])
                elif step == 'emotional_jobs':
                    expected_personal_banker_children.extend([
                        {
                            'name': 'Building Trust',
                            'description': 'Establishing a trustworthy relationship with clients.'
                        },
                        {
                            'name': 'Reducing Anxiety',
                            'description': 'Helping clients feel secure about their financial decisions.'
                        }
                    ])
                elif step == 'social_jobs':
                    expected_personal_banker_children.extend([
                        {
                            'name': 'Networking',
                            'description': 'Connecting with industry peers and potential clients.'
                        },
                        {
                            'name': 'Community Engagement',
                            'description': 'Participating in community events and initiatives.'
                        }
                    ])

        # Similarly, for "Account Manager"
        account_manager_children = self.account_manager.children
        expected_account_manager_children = []
        for step in expected_steps:
            if step == 'financial_metrics_of_purchasing_decision_makers':
                expected_account_manager_children.extend([
                    {
                        'name': 'Revenue Growth',
                        'description': "Increasing the company's income over time."
                    },
                    {
                        'name': 'Profit Margins',
                        'description': "Enhancing the difference between revenue and costs."
                    }
                ])
            elif step == 'job_map':
                expected_account_manager_children.extend([
                    {
                        'name': 'Infrastructure Engineer',
                        'description': 'Designs and maintains the IT infrastructure.'
                    },
                    {
                        'name': 'DevOps Engineer',
                        'description': 'Bridges the gap between development and operations.'
                    }
                ])
            elif step == 'ideal_job_state':
                expected_account_manager_children.extend([
                    {
                        'name': 'Seamless Integration',
                        'description': 'Integrating financial tools effortlessly into existing systems.'
                    },
                    {
                        'name': 'Real-Time Analytics',
                        'description': 'Providing immediate insights into financial data.'
                    }
                ])
            elif step == 'potential_root_causes_preventing_the_ideal_state':
                expected_account_manager_children.extend([
                    {
                        'name': 'Data Silos',
                        'description': 'Fragmented data across different departments hindering comprehensive analysis.'
                    },
                    {
                        'name': 'Legacy Systems',
                        'description': 'Outdated technology that is incompatible with modern financial tools.'
                    }
                ])
            else:
                # Specific steps with known mock responses
                if step == 'job_contexts':
                    expected_account_manager_children.extend([
                        {
                            'name': 'IT Managed Services Provider',
                            'description': 'A company looking to outsource the management of their IT infrastructure.'
                        },
                        {
                            'name': 'Network Security Specialist',
                            'description': "An individual focused on protecting the organization's network from cyber threats."
                        }
                    ])
                elif step == 'desired_outcomes_(success_metrics)':
                    expected_account_manager_children.extend([
                        {
                            'name': 'Improved Efficiency',
                            'description': 'Streamlining operations to reduce costs and increase productivity.'
                        },
                        {
                            'name': 'Enhanced Security',
                            'description': 'Strengthening security measures to protect data and assets.'
                        }
                    ])
                elif step == 'themed_desired_outcomes_(themed_success_metrics)':
                    expected_account_manager_children.extend([
                        {
                            'name': 'Customer Satisfaction',
                            'description': 'Ensuring customers are happy with the services provided.'
                        },
                        {
                            'name': 'Operational Excellence',
                            'description': 'Achieving high standards in operational processes.'
                        }
                    ])
                elif step == 'situational_and_complexity_factors':
                    expected_account_manager_children.extend([
                        {
                            'name': 'Market Competition',
                            'description': 'The level of competition in the financial sector.'
                        },
                        {
                            'name': 'Regulatory Compliance',
                            'description': 'Adhering to financial regulations and standards.'
                        }
                    ])
                elif step == 'related_jobs':
                    expected_account_manager_children.extend([
                        {
                            'name': 'Financial Advisor',
                            'description': 'Provides financial planning and investment advice.'
                        },
                        {
                            'name': 'Loan Officer',
                            'description': 'Evaluates and authorizes loan applications.'
                        }
                    ])
                elif step == 'emotional_jobs':
                    expected_account_manager_children.extend([
                        {
                            'name': 'Building Trust',
                            'description': 'Establishing a trustworthy relationship with clients.'
                        },
                        {
                            'name': 'Reducing Anxiety',
                            'description': 'Helping clients feel secure about their financial decisions.'
                        }
                    ])
                elif step == 'social_jobs':
                    expected_account_manager_children.extend([
                        {
                            'name': 'Networking',
                            'description': 'Connecting with industry peers and potential clients.'
                        },
                        {
                            'name': 'Community Engagement',
                            'description': 'Participating in community events and initiatives.'
                        }
                    ])

        # Verify children for Personal Banker
        self.verify_children(personal_banker_children, expected_personal_banker_children)

        # Verify children for Account Manager
        self.verify_children(account_manager_children, expected_account_manager_children)

        # Optionally, verify that the hierarchy is saved correctly
        # This would involve checking if save_hierarchy_to_markdown was called with the correct parameters
        # Since save_hierarchy_to_markdown is called within the app, you might need to mock it if necessary

        # Example: Ensure that the hierarchy is still intact after processing
        hierarchy_dict = node_to_dict(self.root)
        reconstructed_root = dict_to_tree(hierarchy_dict)
        self.assertEqual(self.root.name, reconstructed_root.name)
        self.assertEqual(self.root.description, reconstructed_root.description)
        self.assertEqual(self.root.processed, reconstructed_root.processed)

        # Further assertions can be added based on specific requirements


if __name__ == '__main__':
    unittest.main()
