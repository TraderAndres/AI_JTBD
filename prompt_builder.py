import os
import logging
import re
import yaml

logging.basicConfig(level=logging.DEBUG)


class PromptBuilder:
    def __init__(self, prompts_dir='prompts'):
        self.prompts = {}
        self.load_prompts(prompts_dir)

    def load_prompts(self, prompts_dir):
        """
        Recursively load all YAML prompt files from the prompts directory and its subdirectories.
        """
        # Walk through all files and subdirectories in the prompts_dir
        for root, _, files in os.walk(prompts_dir):
            for filename in files:
                if filename.endswith('.yaml') or filename.endswith('.yml'):
                    path = os.path.join(root, filename)
                    with open(path, 'r') as file:
                        content = yaml.safe_load(file)
                        # Create the prompt name based on the relative path (excluding the file extension)
                        # relative_path = os.path.relpath(path, prompts_dir)
                        # prompt_name = os.path.splitext(relative_path)[0].replace(os.sep, '_')
                        prompt_name = os.path.splitext(filename)[0]

                        # Store the template and parameters for each prompt
                        self.prompts[prompt_name] = {
                            'template': content['prompt'],
                            'parameters': content.get('parameters', {})
                        }
                        logging.info(f"Loaded prompt: {prompt_name} from {path}")

        # Debug: List all loaded prompts
        logging.debug(f"Available prompts: {list(self.prompts.keys())}")

    def get_prompt(self, prompt_name, **kwargs):
        """
        Retrieve and format a prompt by name with provided keyword arguments.
        """
        prompt_data = self.prompts.get(prompt_name)
        if not prompt_data:
            raise ValueError(f"Prompt '{prompt_name}' not found.")

        template = prompt_data['template']
        parameters = prompt_data.get('parameters', {})

        # Extract default values from the YAML parameters
        default_values = {}
        for param, details in parameters.items():
            if 'default' in details:
                default_values[param] = details['default']

        # Merge provided kwargs with default values
        final_kwargs = {**default_values, **kwargs}

        # Identify missing required parameters
        missing_params = [
            param for param, details in parameters.items()
            if details.get('required', False) and param not in final_kwargs
        ]
        if missing_params:
            raise ValueError(
                f"Missing required parameters for prompt '{prompt_name}': {', '.join(missing_params)}"
            )

        try:
            return template.format(**final_kwargs)
        except KeyError as e:
            missing_key = e.args[0]
            raise KeyError(
                f"Missing key '{missing_key}' for prompt '{prompt_name}'. "
                f"Ensure it's provided in the YAML or as an argument."
            )

    # Specific prompt-building methods using the YAML configuration
    def build_job_contexts_prompt(self, end_user, job, context, n):
        return self.get_prompt('job_contexts', end_user=end_user, job=job, context=context, n=n)

    def build_job_map_prompt(self, end_user, job, context, fidelity):
        return self.get_prompt('job_map', end_user=end_user, job=job, context=context, fidelity=fidelity)

    def build_desired_outcomes_prompt(self, end_user, job, context, step, n):
        return self.get_prompt('desired_outcomes', end_user=end_user, job=job, context=context, step=step, n=n)

    def build_themed_desired_outcomes_prompt(self, end_user, job, context, step, n):
        return self.get_prompt('themed_desired_outcomes', end_user=end_user, job=job, context=context, step=step, n=n)

    def build_situational_and_complexity_factors_prompt(self, end_user, job, context, n):
        return self.get_prompt('situational_and_complexity_factors', end_user=end_user, job=job, context=context, n=n)

    def build_related_jobs_prompt(self, end_user, job, context, n):
        return self.get_prompt('related_jobs', end_user=end_user, job=job, context=context, n=n)

    def build_emotional_jobs_prompt(self, end_user, job, context, n):
        return self.get_prompt('emotional_jobs', end_user=end_user, job=job, context=context, n=n)

    def build_social_jobs_prompt(self, end_user, job, context, n):
        return self.get_prompt('social_jobs', end_user=end_user, job=job, context=context, n=n)

    def build_financial_metrics_of_purchasing_decision_makers_prompt(self, end_user, job, context, n, temp):
        return self.get_prompt('financial_metrics_of_purchasing_decision_makers', end_user=end_user, job=job, context=context, n=n, temp=temp)

    def build_ideal_job_state_prompt(self, end_user, job, context, n, temp):
        return self.get_prompt('ideal_job_state', end_user=end_user, job=job, context=context, n=n, temp=temp)

    def build_potential_root_causes_preventing_the_ideal_state_prompt(self, end_user, job, context, ideal, n, temp):
        return self.get_prompt('potential_root_causes_preventing_the_ideal_state', end_user=end_user, job=job, context=context, ideal=ideal, n=n, temp=temp)


class PromptParser:
    def _parse_list_response(self, response):
        """
        Helper method to parse a numbered markdown list into a list of dictionaries.
        Each dictionary contains 'name' and 'description'.
        """
        parsed_items = []
        lines = response.strip().split('\n')

        # Updated regex pattern to handle different separators and name formatting styles
        pattern = re.compile(r'^\s*\d+\.\s*(?:\*\*(.+?)\*\*|(.+?))\s*[:\-–—]\s*(.+)$')

        for line in lines:
            if line.strip():
                match = pattern.match(line)
                if match:
                    # Use the first capture group (bold name) if it exists, otherwise the second group (non-bold name)
                    name = match.group(1) if match.group(1) else match.group(2)
                    description = match.group(3).strip()
                    parsed_items.append({"name": name.strip(), "description": description})

                else:
                    logging.warning(f"Line did not match any known pattern and was skipped: '{line}'")

        return parsed_items

    # Refactored parsing methods for each prompt response
    def parse_job_contexts(self, response):
        return self._parse_list_response(response)

    def parse_job_map(self, response):
        return self._parse_list_response(response)

    def parse_desired_outcomes(self, response):
        return self._parse_list_response(response)

    def parse_themed_desired_outcomes(self, response):
        return self._parse_list_response(response)

    def parse_situational_and_complexity_factors(self, response):
        return self._parse_list_response(response)

    def parse_related_jobs(self, response):
        return self._parse_list_response(response)

    def parse_emotional_jobs(self, response):
        return self._parse_list_response(response)

    def parse_social_jobs(self, response):
        return self._parse_list_response(response)

    def parse_financial_metrics_of_purchasing_decision_makers(self, response):
        return self._parse_list_response(response)

    def parse_ideal_job_state(self, response):
        return self._parse_list_response(response)

    def parse_potential_root_causes_preventing_the_ideal_state(self, response):
        return self._parse_list_response(response)
