# downstream_processor.py
import re

import streamlit as st

from prompt_builder import PromptBuilder
from llm_interface import LLMInterface


class DownstreamProcessor:
    def __init__(self, prompt_builder: PromptBuilder, llm: LLMInterface):
        self.prompt_builder = prompt_builder
        self.llm = llm

    def process_step(self, end_user, job, context, step, n, fidelity, temp=0.1):
        """
        General method to process any downstream step.
        """
        prompt = self.prompt_builder.build_prompt(end_user, job, context, step, n, fidelity)
        response = self.llm.get_response(prompt, temperature=temp)
        parsed_response = self.prompt_builder.parse_response(step, response)
        return parsed_response

    # Define specific methods for each downstream step if needed
    def process_job_contexts(self, end_user, job, context, n, fidelity, temp=0.1):
        prompt = self.prompt_builder.build_job_contexts_prompt(end_user, job, context, n)
        response = self.llm.get_response(prompt, temperature=temp)
        parsed_response = self.prompt_builder.parse_job_contexts(response)
        return parsed_response

    def process_job_map(self, end_user, job, context, fidelity, temp=0.1):
        prompt = self.prompt_builder.build_job_map_prompt(end_user, job, context, fidelity)
        response = self.llm.get_response(prompt, temperature=temp)
        parsed_response = self.prompt_builder.parse_job_map(response)
        return parsed_response

    # Add similar methods for other downstream steps...
