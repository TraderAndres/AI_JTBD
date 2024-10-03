# hierarchy_builder.py
import json
import logging
import os
import re
from anytree import Node, PreOrderIter

from llm_interface import LLMInterface  # Import your interface here
from prompt_builder import PromptBuilder  # Import your builder here
from utils import save_hierarchy_to_file, save_hierarchy_to_markdown  # Custom utility functions
from mongo_manager import MongoDBManager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class HierarchyBuilder:
    def __init__(self, llm_interface, prompt_builder, fidelity="comprehensive", save_path='saved_hierarchies', mongo_uri=None, db_name=None):
        self.llm = llm_interface
        self.prompt_builder = prompt_builder
        self.fidelity = fidelity
        self.job_nodes = []  # List to store all Job nodes
        self.root = None
        self.industry = None
        self.save_path = save_path
        self.mongo_manager = None

        # Initialize MongoDBManager if URI and DB name are provided
        if mongo_uri and db_name:
            self.mongo_manager = MongoDBManager(mongo_uri, db_name)
            self.mongo_manager.set_collection('hierarchy_entries')  # Define a default collection name

        os.makedirs(self.save_path, exist_ok=True)  # Ensure save directory exists


    def _get_save_file_path(self, industry):
        return os.path.join(self.save_path, f"{industry}_progress.json")

    def _load_saved_hierarchy(self, industry):
        save_file = self._get_save_file_path(industry)
        if os.path.exists(save_file):
            logging.info(f"Loading saved hierarchy from {save_file}")
            with open(save_file, 'r') as f:
                return json.load(f)
        return None

    def _save_current_hierarchy(self):
        """
        Save the current hierarchy to file incrementally.
        """
        if self.industry:
            save_file = self._get_save_file_path(self.industry)
            save_hierarchy_to_file(self.root, save_file)  # Use custom utility function for saving

            # Check if the file was created successfully before attempting further operations
            if os.path.exists(save_file):
                save_hierarchy_to_markdown(save_file, f"{self.industry}_hierarchy_output.md")  # Save markdown output
                logging.info(f"Hierarchy progress saved to '{save_file}'.")
            else:
                logging.error(f"Failed to save hierarchy to '{save_file}'")

    def _convert_hierarchy_to_dict(self, node):
        """
        Converts the hierarchy starting from a given node into a dictionary format for JSON serialization.
        """
        children = [self._convert_hierarchy_to_dict(child) for child in node.children]
        node_dict = {
            "name": node.name,
            "description": getattr(node, 'description', ''),
            "processed": getattr(node, 'processed', False),
            "children": children
        }
        return node_dict

    def _resume_from_saved_state(self, saved_hierarchy):
        """
        Rebuild the hierarchy tree from the saved state dictionary.
        """
        def build_tree(node_data, parent=None):
            node = Node(
                node_data['name'],
                parent=parent,
                description=node_data.get('description', ''),
                processed=node_data.get('processed', False)
            )
            for child_data in node_data.get('children', []):
                build_tree(child_data, node)
            return node

        self.root = build_tree(saved_hierarchy)
        # Populate job_nodes list for downstream processing
        self.job_nodes = [node for node in PreOrderIter(self.root) if node.name.startswith('Job')]
        logging.info(f"Hierarchy resumed with {len(self.job_nodes)} job nodes.")

    def build_hierarchy(self, industry, fidelity="comprehensive", n_end_users=10, n_jobs=10):
        """
        Constructs the full hierarchy from Industry to Jobs with incremental saving.
        """
        self.industry = industry
        self.fidelity = fidelity

        # Step 0: Check for saved progress and resume if possible
        saved_hierarchy = self._load_saved_hierarchy(industry)
        if saved_hierarchy:
            logging.info("Resuming hierarchy build from last saved state.")
            self._resume_from_saved_state(saved_hierarchy)
            if not self.root:  # Verify root node is set after resume
                raise ValueError("Failed to resume hierarchy. Root node is None.")
            return self.root   #need to update this because just leaves is partially formed

        # Step 1: Initialize hierarchy if not resuming
        self.root = Node(industry, description="Root node for industry hierarchy")
        logging.info(f"Starting hierarchy build for industry: {industry}")

        # Step 2: Retrieve sectors using a general get_prompt approach
        sectors_prompt = self.prompt_builder.get_prompt('sectors', industry=industry, fidelity=fidelity)
        print(f"Generated sectors prompt: {sectors_prompt}")  # Debugging print for sectors prompt
        sectors_response = self.llm.get_response(sectors_prompt)
        sectors = self.parse_list(sectors_response)
        

        for sector in sectors:
            sector_node = Node(sector["name"], parent=self.root, description=sector["description"])
            self._save_current_hierarchy()  # Save after each sector is added

            # Retrieve subsectors dynamically
            subsectors_prompt = self.prompt_builder.get_prompt('subsectors', industry=industry, sector=sector["name"], fidelity=fidelity)
            subsectors_response = self.llm.get_response(subsectors_prompt)
            subsectors = self.parse_list(subsectors_response)
            
            for subsector in subsectors:
                subsector_node = Node(subsector["name"], parent=sector_node, description=subsector["description"])
                self._save_current_hierarchy()  # Save after each subsector is added

                # Step 4: Retrieve end-users dynamically (providers and customers)
                end_users_provider_prompt = self.prompt_builder.get_prompt('end_users_provider', industry=industry, sector=sector["name"], subsector=subsector["name"], n=n_end_users, fidelity=fidelity)
                end_users_provider_response = self.llm.get_response(end_users_provider_prompt)
                end_users_providers = self.parse_roles(end_users_provider_response)
                
                providers_parent_node = Node("End Users - Providers", parent=subsector_node, description="End Users who provide services or products.")

                for provider in end_users_providers:
                    provider_node = Node(provider["role"], parent=providers_parent_node, description=provider["description"])
                    self._save_current_hierarchy()  # Save after each provider is added

                    # Step 5: Retrieve Jobs-to-be-Done for Providers
                    jobs_prompt = self.prompt_builder.get_prompt(
                        'jtbd_industry',
                        end_user=provider["role"],
                        industry=industry,
                        sector=sector["name"],
                        subsector=subsector["name"],
                        n=n_jobs
                    )
                    jobs_response = self.llm.get_response(jobs_prompt)
                    jobs = self.parse_jobs(jobs_response)

                    for job in jobs:
                        job_node = Node(job["job"], parent=provider_node, description=job["description"], processed=False)
                        self.job_nodes.append(job_node)  # Store Job node
                        self._save_current_hierarchy()  # Save after each job is added

                # Repeat for customer end users as well, following a similar structure as above
                end_users_customer_prompt = self.prompt_builder.get_prompt('end_users_customer', industry=industry, sector=sector["name"], subsector=subsector["name"], n=n_end_users, fidelity=fidelity)
                end_users_customer_response = self.llm.get_response(end_users_customer_prompt)
                end_users_customers = self.parse_roles(end_users_customer_response)

                customers_parent_node = Node("End Users - Customers", parent=subsector_node, description="End Users who purchase services or products.")

                for customer in end_users_customers:
                    customer_node = Node(customer["role"], parent=customers_parent_node, description=customer["description"])
                    self._save_current_hierarchy()  # Save after each customer is added

                    # Retrieve Jobs-to-be-Done for Customers
                    jtbd_customers_prompt = self.prompt_builder.get_prompt(
                        'jtbd_customers',
                        end_user=customer["role"],
                        industry=industry,
                        sector=sector["name"],
                        subsector=subsector["name"],
                        n=n_jobs
                    )
                    jtbd_customers_response = self.llm.get_response(jtbd_customers_prompt)
                    jtbd_customers = self.parse_jobs(jtbd_customers_response)

                    for jtbd in jtbd_customers:
                        jtbd_node = Node(jtbd["job"], parent=customer_node, description=jtbd["description"], processed=False)
                        self.job_nodes.append(jtbd_node)  # Store Job node
                        self._save_current_hierarchy()  # Save after each job is added

        logging.info("Hierarchy building completed.")
        self._save_current_hierarchy()  # Final save at the end of hierarchy build
        return self.root


    def parse_response(self, response, pattern, keys=("name", "description")):
        """
        General parsing function that extracts items from a given response based on a pattern.

        Args:
            response (str): The response text to be parsed.
            pattern (str): The regex pattern to match lines in the response.
            keys (tuple): A tuple of keys to assign to matched groups in the dictionary.

        Returns:
            list: A list of dictionaries with parsed information.
        """
        items = []
        lines = response.split('\n')
        regex = re.compile(pattern)

        for line in lines:
            match = regex.match(line)
            if match:
                # Map matched groups to the specified keys
                parsed_item = {key: match.group(i + 1).strip() for i, key in enumerate(keys)}
                items.append(parsed_item)
            else:
                logging.warning(f"Line did not match pattern: {line}")

        return items

    def parse_list(self, response):
        pattern = r'^\d+\.\s*\*\*(.+?)\*\*(?::\s*|)\s*(.+)$'
        logging.debug(f"Parsing response: {response}")  # Debugging print for incoming response
        parsed = self.parse_response(response, pattern)
        logging.debug(f"Parsed items: {parsed}")  # Debugging print for parsed items
        return parsed

    def parse_roles(self, response):
        pattern = r'^\d+\.\s+\*\*(.+?)\*\*:\s+(.+)$'
        return self.parse_response(response, pattern, keys=("role", "description"))

    def parse_jobs(self, response):
        pattern = r'^\d+\.\s+\*\*(.+?)\*\*\s+-\s+(.+)$'
        return self.parse_response(response, pattern, keys=("job", "description"))

