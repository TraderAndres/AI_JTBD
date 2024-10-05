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
logger = logging.getLogger("MongoDBManager")
logger.setLevel(logging.WARNING)  # Set to WARNING to suppress DEBUG/INFO logs

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
            self.mongo_manager.set_collection('jtbd_hierarchy2')  # Define a default collection name

        os.makedirs(self.save_path, exist_ok=True)  # Ensure save directory exists


    def _get_save_file_path(self, industry):
        return os.path.join(self.save_path, f"{industry}_progress.json")

    def _load_saved_hierarchy(self, industry):
        """
        Load the saved hierarchy from MongoDB.
        """
        if self.mongo_manager:
            query = {"industry": industry}
            saved_entry = self.mongo_manager.find_entry(query)
            if saved_entry:
                logging.info(f"Loading saved hierarchy from MongoDB for industry '{industry}'")
                return saved_entry.get("hierarchy")
        return None

    def _save_current_hierarchy(self):
        """
        Save the current hierarchy to MongoDB incrementally.
        """
        if self.industry and self.mongo_manager:
            hierarchy_dict = self._convert_hierarchy_to_dict(self.root)
            query = {"industry": self.industry}
            entry = {
                "industry": self.industry,
                "hierarchy": hierarchy_dict
            }
            # Update if exists, insert if not
            if self.mongo_manager.find_entry(query):
                self.mongo_manager.update_entry(query, entry)
            else:
                self.mongo_manager.insert_entry(entry)
            logging.info(f"Hierarchy progress saved to MongoDB for industry '{self.industry}'.")


    def _convert_hierarchy_to_dict(self, node):
        """
        Converts the hierarchy starting from a given node into a dictionary format for JSON serialization.
        """
        children = [self._convert_hierarchy_to_dict(child) for child in node.children]
        node_dict = {
            "name": node.name,
            "description": getattr(node, 'description', ''),
            "processed": getattr(node, 'processed', False),
            "type": getattr(node, 'type', ''), 
            "children": children
        }
        return node_dict

    def _resume_from_saved_state(self, saved_hierarchy):
        """
        Rebuild the hierarchy tree from the saved state dictionary.
        """
        def build_tree(node_data, parent=None):
            """
            Recursively build the tree structure from saved hierarchy data.
            """
            node = Node(
                node_data['name'],
                parent=parent,
                description=node_data.get('description', ''),
                processed=node_data.get('processed', False),  # Use the 'processed' attribute
                type=node_data.get('type', ''),  # Include 'type' attribute if it exists
            )

            # Recursively build children nodes
            for child_data in node_data.get('children', []):
                build_tree(child_data, node)

            return node

        # Ensure the saved_hierarchy has the correct structure
        if not saved_hierarchy or "name" not in saved_hierarchy:
            raise ValueError("Saved hierarchy is either empty or incorrectly formatted")

        logging.info("Resuming hierarchy build from saved state...")

        # Build the tree starting from the saved hierarchy root
        self.root = build_tree(saved_hierarchy)

        # Populate job_nodes list for downstream processing using the 'processed' flag
        self.job_nodes = [node for node in PreOrderIter(self.root) if not node.processed]

        # Debugging: Print job nodes information
        logging.info(f"Hierarchy resumed with {len(self.job_nodes)} unprocessed job nodes.")


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

            # Resume processing from unprocessed nodes
            unprocessed_nodes = [node for node in PreOrderIter(self.root) if not getattr(node, 'processed', False)]
            if unprocessed_nodes:
                logging.info(f"Resuming hierarchy build with {len(unprocessed_nodes)} unprocessed nodes.")
                # Continue hierarchy building from the highest unprocessed node
                self.process_hierarchy(unprocessed_nodes, n_end_users=n_end_users, n_jobs=n_jobs)
                return self.root
            else:
                logging.info("All nodes have been processed. No further work needed.")
                return self.root

        # Step 1: Initialize hierarchy if not resuming
        self.root = Node(industry, description="Root node for industry hierarchy", type="Industry", processed=False)
        logging.info(f"Starting hierarchy build for industry: {industry}")

        # Start building from scratch or from the root
        self._process_node(self.root, n_end_users, n_jobs)

        logging.info("Hierarchy building completed.")
        self._save_current_hierarchy()  # Final save at the end of hierarchy build

        return self.root


    def process_hierarchy(self, unprocessed_nodes, n_end_users=10, n_jobs=10):
        """
        Process the hierarchy starting from the list of unprocessed nodes.
        This function re-enters the hierarchy-building process from the point of the highest unprocessed node.
        """
        for node in unprocessed_nodes:
            # Check if the node has children that need processing
            if not node.processed:
                logging.info(f"Resuming processing for node: {node.name} (Type: {node.type})")
                self._process_node(node, n_end_users=n_end_users, n_jobs=n_jobs)


    def _process_node(self, node, n_end_users=10, n_jobs=10):
        """
        Process a given node by generating its children and marking it as processed when done.
        This method handles the recursive generation of children and ensures proper saving at each step.
        """
        node_type = getattr(node, "type", None)
        if node_type == "Industry":
            # Root node -> Generate sectors
            self._generate_and_process_children(
                parent_node=node,
                prompt_type='sectors',
                child_type="Sector",
                n_end_users=n_end_users,
                n_jobs=n_jobs
            )

        elif node_type == "Sector":
            # Sector node -> Generate subsectors
            self._generate_and_process_children(
                parent_node=node,
                prompt_type='subsectors',
                child_type="Sub-sector",
                n_end_users=n_end_users,
                n_jobs=n_jobs
            )

        elif node_type == "Sub-sector":
            # Sub-sector node -> Generate end users
            self._process_end_users(node, n_end_users, n_jobs)
            node.processed = True
            self._save_current_hierarchy()  # Save the state after processing end users


    def _generate_and_process_children(self, parent_node, prompt_type, child_type, n_end_users=10, n_jobs=10):
        """
        Generic function to generate child nodes based on the given parent node and prompt type.
        This function will handle generating, saving, and processing child nodes.

        Args:
            parent_node (Node): The parent node for which to generate children.
            prompt_type (str): The type of prompt to generate (e.g., 'sectors', 'subsectors').
            child_type (str): The type of the child nodes being created.
            n_end_users (int): Number of end-users to process for each child node.
            n_jobs (int): Number of jobs to process for each end-user node.
        """
        # Use both name and description for the prompt input to provide more context
        parent_input = f"{parent_node.name} - ({parent_node.description})" if parent_node.description else parent_node.name
        prompt = self.prompt_builder.get_prompt(prompt_type, industry=self.industry, sector=parent_input, fidelity=self.fidelity)

        # Generate prompt and parse the response
        response = self.llm.get_response(prompt)
        children_data = self.parse_list(response)

        # Create child nodes and save them before processing further
        for child in children_data:
            child_node = Node(
                child["name"], 
                parent=parent_node, 
                description=child["description"], 
                type=child_type, 
                processed=False
            )
        self._save_current_hierarchy()  # Save all child nodes together before further processing

        # Mark parent node as processed after all children have been saved
        parent_node.processed = True
        self._save_current_hierarchy()
        logging.info(f"Parent node '{parent_node.name}' marked as processed after saving all {child_type.lower()} nodes.")

        # Process each child node independently
        for child_node in parent_node.children:
            if not child_node.processed:
                self._process_node(child_node, n_end_users, n_jobs)


    def _process_end_users(self, node, n_end_users, n_jobs):
        """
        Process the end users (providers and customers) for a given sub-sector node.
        """
        # Use both name and description for the prompt input to provide more context
        sector_input = f"{node.parent.name} - ({node.parent.description})" if node.parent.description else node.parent.name
        subsector_input = f"{node.name} - ({node.description})" if node.description else node.name

        # Generate and save providers
        self._generate_and_process_end_user_type(
            parent_node=node,
            prompt_type='end_users_provider',
            parent_node_name="End Users - Providers",
            user_type="Provider",
            sector_input=sector_input,
            subsector_input=subsector_input,
            n_end_users=n_end_users,
            n_jobs=n_jobs
        )

        # Generate and save customers
        self._generate_and_process_end_user_type(
            parent_node=node,
            prompt_type='end_users_customer',
            parent_node_name="End Users - Customers",
            user_type="Customer",
            sector_input=sector_input,
            subsector_input=subsector_input,
            n_end_users=n_end_users,
            n_jobs=n_jobs
        )


    def _generate_and_process_end_user_type(self, parent_node, prompt_type, parent_node_name, user_type, sector_input, subsector_input, n_end_users, n_jobs):
        """
        Generate and process a specific type of end user (Provider or Customer).

        Args:
            parent_node (Node): The parent sub-sector node.
            prompt_type (str): The type of prompt (e.g., 'end_users_provider', 'end_users_customer').
            parent_node_name (str): The name for the parent end user node (e.g., "End Users - Providers").
            user_type (str): The type of end user (e.g., "Provider" or "Customer").
            sector_input (str): Combined sector name and description for the prompt.
            subsector_input (str): Combined subsector name and description for the prompt.
            n_end_users (int): Number of end users to generate.
            n_jobs (int): Number of jobs to generate for each end user.
        """
        # Generate prompt and parse response
        prompt = self.prompt_builder.get_prompt(prompt_type, industry=self.industry, sector=sector_input, subsector=subsector_input, n=n_end_users, fidelity=self.fidelity)
        response = self.llm.get_response(prompt)
        end_users = self.parse_roles(response)

        # Create parent node for this end user type
        end_user_parent_node = Node(parent_node_name, parent=parent_node, description=f"End Users who are {user_type.lower()}s.", type=parent_node_name, processed=False)

        for end_user in end_users:
            # Save the name and description separately in the end-user node
            end_user_node = Node(
                name=end_user["role"],  # Save only the role name
                parent=end_user_parent_node,
                description=end_user["description"],  # Keep the description separate
                type="End User",
                processed=False
            )
            self._save_current_hierarchy()  # Save after each end user node is created

            # Generate jobs for each end user
            self._process_jobs(end_user_node, n_jobs)

            # Mark end user node as processed
            end_user_node.processed = True
            self._save_current_hierarchy()

        # Mark parent end user node as processed once all end users are done
        end_user_parent_node.processed = True
        self._save_current_hierarchy()
        logging.info(f"{user_type} parent node '{end_user_parent_node.name}' marked as processed after saving all end user nodes.")



    def _process_jobs(self, end_user_node, n_jobs):
        """
        Process the jobs for a given end-user node (provider or customer).

        Args:
            end_user_node (Node): The node representing the end-user for whom jobs are being processed.
            n_jobs (int): The number of jobs to generate for this end-user.
        """
        try:
            # Correctly extract the relevant information for the prompt by going up the hierarchy
            # Go up two levels to get to the Sub-sector
            subsector_node = end_user_node.parent.parent
            subsector_name = subsector_node.name
            subsector_description = subsector_node.description

            # Go up three levels to get to the Sector
            sector_node = subsector_node.parent
            sector_name = sector_node.name
            sector_description = sector_node.description

            # Use the end user node's name and description
            end_user_role = end_user_node.name
            end_user_description = end_user_node.description

            # Concatenate the name and description for each element to provide additional context
            sector_input = f"{sector_name} - ({sector_description})" if sector_description else sector_name
            subsector_input = f"{subsector_name} - ({subsector_description})" if subsector_description else subsector_name
            end_user_input = f"{end_user_role} - ({end_user_description})" if end_user_description else end_user_role

            # Build the prompt to retrieve jobs-to-be-done for this end user
            jtbd_prompt = self.prompt_builder.get_prompt(
                'jtbd_industry',
                end_user=end_user_input,  # Use the concatenated end user name and description
                industry=self.industry,
                sector=sector_input,  # Use the concatenated sector name and description
                subsector=subsector_input,  # Use the concatenated subsector name and description
                n=n_jobs
            )

            # Send prompt to LLM and parse the response
            jtbd_response = self.llm.get_response(jtbd_prompt)
            jobs = self.parse_jobs(jtbd_response)

            # Create job nodes as children of the end_user_node
            for job in jobs:
                job_node = Node(
                    job["job"],
                    parent=end_user_node,
                    description=job["description"],
                    type="Job",
                    processed=True  # Job nodes can be marked as processed immediately since they are leaves
                )
                # Save state after adding each job
                self._save_current_hierarchy()
                logging.info(f"Added job '{job_node.name}' to end user '{end_user_node.name}'.")

            # Once all jobs are processed, log a message
            logging.info(f"All jobs for end user '{end_user_node.name}' have been processed.")

        except Exception as e:
            logging.error(f"Error processing jobs for end user '{end_user_node.name}': {e}")


     

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

