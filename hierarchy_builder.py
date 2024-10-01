# hierarchy_builder.py
import json
import logging
import re

from anytree import Node, RenderTree, PreOrderIter

from llm_interface import LLMInterface
from prompt_builder import PromptBuilder
from utils import save_hierarchy_to_file, save_hierarchy_to_markdown


# Configure logging to display the time, log level, and message
logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s',  # Define the log message format
    datefmt='%Y-%m-%d %H:%M:%S'  # Define the date format
)


class HierarchyBuilder:

    def __init__(self,
                 llm_interface,
                 prompt_builder,
                 fidelity="comprehensive"):
        self.llm = llm_interface
        self.prompt_builder = prompt_builder
        self.fidelity = fidelity
        self.job_nodes = []  # List to store all Job nodes
        self.root = None
        self.industry = None

    def parse_list(self, response):
        """
        Parses a numbered markdown list and extracts the items.
        This version uses a modified regex pattern to capture multiple groups.
        """
        items = []

        # Normalize the response to ensure consistent line breaks and remove hidden characters
        response = response.replace('\n\n', '\n').replace('\r', '').replace(
            '\u00A0', ' ').replace('\u200B', '')

        # Split response into lines
        lines = response.split('\n')

        # Updated pattern to match a line with numbering, bold item name, and description as separate groups
        pattern = re.compile(r'\d+\.\s*\*\*(.+?)\*\*(?::\s*|)\s*(.+)')

        for line in lines:
            # Remove leading/trailing whitespace
            line = line.strip()
            logging.debug(f"Line being processed: {repr(line)}")

            # Try matching the cleaned line with the regex pattern
            match = pattern.match(line)
            if match:
                # Capture the item name and description separately
                name = match.group(1).strip()
                description = match.group(2).strip()
                items.append({"name": name, "description": description})
                logging.debug(f"Matched! Name: {name}, Description: {description}")
            else:
                logging.warning(f"No match found for line: {repr(line)}")

        # Debugging: Print the entire cleaned response if no items matched
        if not items:
            logging.error(
                f"No items matched. Check the cleaned response formatting: {repr(response)}"
            )

        return items

    def parse_roles(self, response):
        """
        Parses roles from the response.
        Expected format:
        1. **Role Name**: Description
        """
        roles = []
        lines = response.split('\n')
        pattern = re.compile(r'^\d+\.\s+\*\*(.+?)\*\*:\s+(.+)$')
        for line in lines:
            match = pattern.match(line)
            if match:
                role = match.group(1).strip()
                description = match.group(2).strip()
                roles.append({"role": role, "description": description})
        return roles

    def parse_jobs(self, response):
        """
        Parses jobs from the response.
        Expected format:
        1. **Job Name** - Description
        """
        jobs = []
        lines = response.split('\n')
        pattern = re.compile(r'^\d+\.\s+\*\*(.+?)\*\*\s+-\s+(.+)$')
        for line in lines:
            match = pattern.match(line)
            if match:
                job = match.group(1).strip()
                description = match.group(2).strip()
                jobs.append({"job": job, "description": description})
        return jobs

    def build_hierarchy(self,
                        industry,
                        fidelity="comprehensive",
                        n_end_users=10,
                        n_jobs=10):
        """
        Constructs the full hierarchy from Industry to Jobs.
        """
        self.industry = industry
        self.fidelity = fidelity
        self.root = Node(industry, description="Root node for industry hierarchy")
        logging.info(f"Starting hierarchy build for industry: {industry}")

        # Step 1: Get Sectors
        logging.info("Building sectors prompt.")
        sectors_prompt = self.prompt_builder.build_sectors_prompt(
            industry, fidelity)
        logging.info("Sending sectors prompt to LLM.")
        sectors_response = self.llm.get_response(sectors_prompt)
        logging.info("Received sectors response from LLM.")
        sectors = self.parse_list(sectors_response)

        for sector in sectors:
            sector_node = Node(sector["name"],
                               parent=self.root,
                               description=sector["description"])
            logging.info(f"Processing sector: {sector['name']}")

            # Concatenate sector name and description
            sector_info = f"{sector['name']}: {sector['description']}"

            # Step 2: Get Subsectors
            logging.info("Building subsectors prompt.")
            subsectors_prompt = self.prompt_builder.build_subsectors_prompt(
                industry, sector_info, fidelity)
            logging.info("Sending subsectors prompt to LLM.")
            subsectors_response = self.llm.get_response(subsectors_prompt)
            logging.info("Received subsectors response from LLM.")
            subsectors = self.parse_list(subsectors_response)

            for subsector in subsectors:
                subsector_node = Node(subsector["name"],
                                      parent=sector_node,
                                      description=subsector["description"])
                logging.info(f"Processing subsector: {subsector['name']}")

                # Concatenate subsector name and description
                subsector_info = f"{subsector['name']}: {subsector['description']}"

                # Step 3: Get End Users (Providers)
                logging.info("Building provider end users prompt.")
                end_users_provider_prompt = self.prompt_builder.build_end_users_provider_prompt(
                    industry, sector_info, subsector_info, n_end_users,
                    fidelity)
                logging.info("Sending provider end users prompt to LLM.")
                end_users_provider_response = self.llm.get_response(
                    end_users_provider_prompt)
                logging.info("Received provider end users response from LLM.")
                end_users_providers = self.parse_roles(
                    end_users_provider_response)

                # Create 'End Users - Providers' node
                providers_parent_node = Node(
                    "End Users - Providers",
                    parent=subsector_node,
                    description="End Users who provide services or products."
                )


                for provider in end_users_providers:
                    provider_node = Node(
                        provider["role"],
                        parent=providers_parent_node,
                        description=provider["description"]
                    )
                    logging.info(f"Processing provider end user: {provider['role']}")

                    # Step 4: Get Jobs-to-be-Done for Providers
                    logging.info("Building Jobs-to-be-Done prompt for provider.")
                    jobs_prompt = self.prompt_builder.build_jobs_prompt(
                        provider["role"], industry, sector_info, subsector_info, n_jobs)
                    logging.info("Sending Jobs-to-be-Done prompt to LLM.")
                    jobs_response = self.llm.get_response(jobs_prompt)
                    logging.info("Received Jobs-to-be-Done response from LLM.")
                    jobs = self.parse_jobs(jobs_response)

                    for job in jobs:
                        # When creating a job node, set processed=False
                        job_node = Node(
                            job["job"],
                            parent=provider_node,
                            description=job["description"],
                            processed=False
                        )
                        logging.info(f"Added JTBD for provider: {job['job']}")
                        self.job_nodes.append(job_node)  # Store Job node

                # Step 3.1: Get End Users (Customers)
                logging.info("Building customer end users prompt.")
                end_users_customer_prompt = self.prompt_builder.build_end_users_customer_prompt(
                    industry, sector_info, subsector_info, n_end_users, fidelity)
                logging.info("Sending customer end users prompt to LLM.")
                end_users_customer_response = self.llm.get_response(end_users_customer_prompt)
                logging.info("Received customer end users response from LLM.")
                end_users_customers = self.parse_roles(end_users_customer_response)

                # Create 'End Users - Customers' node
                customers_parent_node = Node(
                    "End Users - Customers",
                    parent=subsector_node,
                    description="End Users who purchase services or products."
                )


                for customer in end_users_customers:
                    customer_node = Node(
                        customer["role"],
                        parent=customers_parent_node,
                        description=customer["description"]
                    )
                    logging.info(f"Processing customer end user: {customer['role']}")

                    # Step 4.1: Get Jobs-to-be-Done for Customers
                    logging.info("Building Jobs-to-be-Done prompt for customer.")
                    jtbd_customers_prompt = self.prompt_builder.build_jtbd_customers_prompt(
                        customer["role"], industry, sector_info, subsector_info, n_jobs)
                    logging.info("Sending Jobs-to-be-Done prompt for customer to LLM.")
                    jtbd_customers_response = self.llm.get_response(jtbd_customers_prompt)
                    logging.info("Received Jobs-to-be-Done response for customer from LLM.")
                    jtbd_customers = self.parse_jobs(jtbd_customers_response)

                    for jtbd in jtbd_customers:
                        jtbd_node = Node(
                            jtbd["job"],
                            parent=customer_node,
                            description=jtbd["description"],
                            processed=False
                        )
                        logging.info(f"Added JTBD for customer: {jtbd['job']}")
                        self.job_nodes.append(jtbd_node)  # Store Job node


        # Validate all nodes have 'description' and 'processed' attributes
        for node in PreOrderIter(self.root):
            if not hasattr(node, 'description'):
                node.description = "No description provided"
            if not hasattr(node, 'processed'):
                node.processed = False

        return self.root

    def save_current_hierarchy(self):
        """
        Placeholder for saving the current hierarchy. Implement saving logic here.
        """
        json_filename = f"{self.industry}_hierarchy.json"
        save_hierarchy_to_file(self.root, json_filename)
        save_hierarchy_to_markdown(json_filename, f"{self.industry}_hierarchy_output.md")
