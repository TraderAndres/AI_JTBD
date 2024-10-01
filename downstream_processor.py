# downstream_processor.py
import logging

from prompt_builder import PromptBuilder
from llm_interface import LLMInterface
import streamlit as st
from anytree import Node

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
        logging.debug(f"Processing step: {step} for node: {node.name}")

        # Determine prompt name based on step
        prompt_name = step.lower().replace(" ", "_")
        if not prompt_name:
            logging.error(f"No prompt mapping found for step '{step}'.")
            st.error(f"No prompt mapping found for step '{step}'.")
            return
        prompt_method = f'build_{prompt_name}_prompt'
        parse_method = f'parse_{prompt_name}'

        logging.debug(f"Prompt Name: {prompt_name}")
        logging.debug(f"Prompt Method: {prompt_method}")
        logging.debug(f"Parse Method: {parse_method}")

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
                (child for child in node.children
                 if child.name.lower() == 'ideal_job_state'), None)
            ideal_job_state_name = ideal_job_state_node.name if ideal_job_state_node else 'Ideal Job State'

            prompt = getattr(self.prompt_builder, prompt_method)(
                end_user=node.parent.parent.name,
                job=node.name,
                context=node.description,
                ideal=
                ideal_job_state_name,  # Correctly reference 'Ideal Job State'
                n=n,
                temp=temp)
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

        # Mark the node as processed
        node.processed = True

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
