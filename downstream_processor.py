# downstream_processor.py
import logging

import streamlit as st
from anytree import Node

from prompt_builder import PromptBuilder
from llm_interface import LLMInterface
from utils import update_hierarchy_in_file

logging.basicConfig(level=logging.DEBUG)


class DownstreamProcessor:

    def __init__(self, prompt_builder: PromptBuilder, llm: LLMInterface):
        self.prompt_builder = prompt_builder
        self.llm = llm
        # Define step to prompt name mapping
        self.step_to_prompt = {
            'Job Contexts': 'job_contexts',
            'Job Map': 'job_map',
            'Desired Outcomes (success metrics)': 'desired_outcomes',
            'Themed Desired Outcomes (Themed Success Metrics)': 'themed_desired_outcomes',
            'Situational and Complexity Factors': 'situational_and_complexity_factors',
            'Related Jobs': 'related_jobs',
            'Emotional Jobs': 'emotional_jobs',
            'Social Jobs': 'social_jobs',
            'Financial Metrics of Purchasing Decision Makers': 'financial_metrics_of_purchasing_decision_makers',
            'Ideal Job State': 'ideal_job_state',
            'Potential Root Causes Preventing the Ideal State': 'potential_root_causes_preventing_the_ideal_state'
        }

    def process_step(self, node, step, n, fidelity, temp=0.1):
        """
        General method to process any downstream step.
        """
        # Check if node is already processed; log additional context on skipping behavior
        if node.processed:
            if len(node.children) > 0:
                logging.info(f"Node '{node.name}' has already been processed and has children. Skipping redundant processing for step '{step}'.")
            else:
                logging.warning(f"Node '{node.name}' is marked as processed but has no children. Consider re-processing step '{step}' for completeness.")
            return
            
        logging.debug(f"Processing step: {step} for node: {node.name}")

        # Determine prompt name based on step
        # Replace special characters like parentheses to ensure consistency
        prompt_name = step.lower().replace(" ", "_").replace("(", "").replace(")", "")
        if prompt_name not in self.step_to_prompt.values():
            logging.error(f"No prompt mapping found for step '{step}'.")
            st.error(f"No prompt mapping found for step '{step}'.")
            return
        prompt_method = f'build_{prompt_name}_prompt'
        parse_method = f'parse_{prompt_name}'

        # Existing logging statements to confirm prompt and parse method names
        logging.debug(f"Generated prompt method: {prompt_method}")
        logging.debug(f"Generated parse method: {parse_method}")

        # Additional logging to verify existence before accessing attributes
        if not hasattr(self.prompt_builder, prompt_method):
            logging.error(f"Prompt method '{prompt_method}' not found in PromptBuilder. Available methods: {dir(self.prompt_builder)}")
        if not hasattr(self.prompt_builder, parse_method):
            logging.error(f"Parse method '{parse_method}' not found in PromptBuilder. Available methods: {dir(self.prompt_builder)}")


        # Check if methods exist
        if not hasattr(self.prompt_builder, prompt_method):
            logging.error(f"Prompt method '{prompt_method}' is not defined in PromptBuilder.")
            st.error(f"Prompt method '{prompt_method}' is not defined.")
            return
        if not hasattr(self.prompt_builder, parse_method):
            logging.error(f"Parse method '{parse_method}' is not defined in PromptBuilder.")
            st.error(f"Parse method '{parse_method}' is not defined.")
            return

        # Build prompt with necessary parameters
        if prompt_name == 'job_map':
            prompt = getattr(self.prompt_builder,
                             prompt_method)(end_user=node.parent.parent.name,
                                            job=node.name,
                                            context=node.description,
                                            fidelity=fidelity)
        elif prompt_name == 'financial_metrics_of_purchasing_decision_makers':
            prompt = getattr(self.prompt_builder, prompt_method)(
                end_user=node.parent.parent.name,
                job=node.name,
                context=node.description,
                n=n,
                temp=temp  # Pass 'temp' here
            )
        elif prompt_name == 'job_contexts':
            prompt = getattr(self.prompt_builder,
                             prompt_method)(end_user=node.parent.parent.name,
                                            job=node.name,
                                            context=node.description,
                                            n=n)
        elif prompt_name == 'desired_outcomes_(success_metrics)':
            prompt = getattr(self.prompt_builder,
                             prompt_method)(end_user=node.parent.parent.name,
                                            job=node.name,
                                            context=node.description,
                                            n=n)
        elif prompt_name == 'themed_desired_outcomes_(themed_success_metrics)':
            prompt = getattr(self.prompt_builder,
                             prompt_method)(end_user=node.parent.parent.name,
                                            job=node.name,
                                            context=node.description,
                                            n=n)
        elif prompt_name == 'situational_and_complexity_factors':
            prompt = getattr(self.prompt_builder,
                             prompt_method)(end_user=node.parent.parent.name,
                                            job=node.name,
                                            context=node.description,
                                            n=n)
        elif prompt_name == 'related_jobs':
            prompt = getattr(self.prompt_builder,
                             prompt_method)(end_user=node.parent.parent.name,
                                            job=node.name,
                                            context=node.description,
                                            n=n)
        elif prompt_name == 'emotional_jobs':
            prompt = getattr(self.prompt_builder,
                             prompt_method)(end_user=node.parent.parent.name,
                                            job=node.name,
                                            context=node.description,
                                            n=n)
        elif prompt_name == 'social_jobs':
            prompt = getattr(self.prompt_builder,
                             prompt_method)(end_user=node.parent.parent.name,
                                            job=node.name,
                                            context=node.description,
                                            n=n)
        elif prompt_name == 'ideal_job_state':
            prompt = getattr(self.prompt_builder,
                             prompt_method)(end_user=node.parent.parent.name,
                                            job=node.name,
                                            context=node.description,
                                            n=n,
                                            temp=temp)
        elif prompt_name == 'potential_root_causes_preventing_the_ideal_state':
            # Find the 'Ideal Job State' node among the children
            ideal_job_state_node = next(
                (child for child in node.children if child.name.lower() == 'ideal_job_state'), None
            )
            if not ideal_job_state_node:
                logging.warning(f"'Ideal Job State' node not found under '{node.name}'. Skipping step '{step}'.")
                return
    
            ideal_job_state_name = ideal_job_state_node.name
            prompt = getattr(self.prompt_builder, prompt_method)(
                end_user=node.parent.parent.name,
                job=node.name,
                context=node.description,
                ideal=ideal_job_state_name,  # Correctly reference 'Ideal Job State'
                n=n,
                temp=temp
            )
        else:
            # Handle other prompts accordingly
            prompt_kwargs = {
                'end_user': node.parent.parent.name,
                'job': node.name,
                'context': node.description,
                'n': n
            }
            # Add additional parameters if required by specific prompts
            if prompt_name == 'ideal_job_state':
                prompt_kwargs['temp'] = temp
            prompt = getattr(self.prompt_builder,
                             prompt_method)(**prompt_kwargs)
        # # Consolidate prompt building using a dictionary for parameter flexibility
        # prompt_kwargs = {
        #     'end_user': node.parent.parent.name,
        #     'job': node.name,
        #     'context': node.description,
        #     'n': n,  # Default n value
        #     'temp': temp  # Default temp value
        # }

        # # Adjust prompt_kwargs for specific prompt requirements
        # if prompt_name == 'job_map':
        #     prompt_kwargs['fidelity'] = fidelity
        # elif prompt_name == 'financial_metrics_of_purchasing_decision_makers':
        #     prompt_kwargs.pop('temp')  # Remove temp if not needed for this prompt

        # # Use prompt_kwargs to build the prompt
        # prompt = getattr(self.prompt_builder, prompt_method)(**prompt_kwargs)

        

        # Get response from LLM
        try:
            response = self.llm.get_response(prompt) #, temperature=temp)
            logging.debug(f"Received response from LLM: {response}")
        except Exception as e:
            logging.exception(f"Error getting response from LLM for step '{step}': {e}")
            return

        # Parse response
        try:
            parsed_response = getattr(self.prompt_builder, parse_method)(response)
            logging.debug(f"Parsed response: {parsed_response}")
        except Exception as e:
            logging.exception(f"Error parsing response for step '{step}': {e}")
            return

        # Add downstream nodes
        if not parsed_response:
            logging.warning(f"No parsed items for step '{step}' on node '{node.name}'. No children added.")
        try:
            for item in parsed_response:
                child_node = Node(
                    name=item['name'],
                    parent=node,
                    description=item.get('description', ''),  # Changed from 'explanation' to 'description'
                    processed=False  # New nodes are unprocessed
                )
                logging.debug(f"Added child node: {child_node.name}")
        except Exception as e:
            logging.exception(f"Error adding child nodes for step '{step}': {e}")
            return

        # After successful processing, mark node as processed only if it has children
        if len(node.children) > 0:
            node.processed = True
            logging.debug(f"Marked node '{node.name}' as processed.")
            
        # # After successful processing, mark as processed
        # node.processed = True
        # # # Update JSON file or database with the new state
        # # update_hierarchy_in_file(root_node, "current_hierarchy.json")

    def process_job_contexts(self, node, n, fidelity, temp=0.1):
        logging.debug(f"Adding 'Job Contexts' under '{node.name}'")
        self.process_step(node, 'Job Contexts', n, fidelity, temp)

    def process_job_map(self, node, fidelity, temp=0.1):
        logging.debug(f"Adding 'Job Map' under '{node.name}'")
        self.process_step(node, 'Job Map', n=0, fidelity=fidelity, temp=temp)

    def process_desired_outcomes(self, node, n, fidelity, temp=0.1):
        logging.debug(f"Adding 'Desired Outcomes (success metrics)' under '{node.name}'")
        self.process_step(node, 'Desired Outcomes (success metrics)', n,
                          fidelity, temp)

    def process_themed_desired_outcomes(self, node, n, fidelity, temp=0.1):
        logging.debug(f"Adding 'Themed Desired Outcomes (Themed Success Metrics)' under '{node.name}'")
        self.process_step(node,
                          'Themed Desired Outcomes (Themed Success Metrics)',
                          n, fidelity, temp)

    def process_situational_complexity_factors(self,
                                               node,
                                               n,
                                               fidelity,
                                               temp=0.1):
        logging.debug(f"Adding 'Situational and Complexity Factors' under '{node.name}'")
        self.process_step(node, 'Situational and Complexity Factors', n,
                          fidelity, temp)

    def process_related_jobs(self, node, n, fidelity, temp=0.1):
        logging.debug(f"Adding 'Related Jobs' under '{node.name}'")
        self.process_step(node, 'Related Jobs', n, fidelity, temp)

    def process_emotional_jobs(self, node, n, fidelity, temp=0.1):
        logging.debug(f"Adding 'Emotional Jobs' under '{node.name}'")
        self.process_step(node, 'Emotional Jobs', n, fidelity, temp)

    def process_social_jobs(self, node, n, fidelity, temp=0.1):
        logging.debug(f"Adding 'Social Jobs' under '{node.name}'")
        self.process_step(node, 'Social Jobs', n, fidelity, temp)

    def process_financial_metrics(self, node, n, fidelity, temp=0.1):
        logging.debug(f"Adding 'Financial Metrics of Purchasing Decision Makers' under '{node.name}'")
        self.process_step(node,
                          'Financial Metrics of Purchasing Decision Makers', n,
                          fidelity, temp)

    def process_ideal_job_state(self, node, n, fidelity, temp=0.1):
        logging.debug(f"Adding 'Ideal Job State' under '{node.name}'")
        self.process_step(node, 'Ideal Job State', n, fidelity, temp)

    def process_potential_root_causes(self, node, n, fidelity, temp=0.1):
        logging.debug(f"Adding 'Potential Root Causes Preventing the Ideal State' under '{node.name}'")
        self.process_step(node,
                          'Potential Root Causes Preventing the Ideal State',
                          n, fidelity, temp)
