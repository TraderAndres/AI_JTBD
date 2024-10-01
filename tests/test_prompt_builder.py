# tests/test_prompt_builder.py

import unittest

from prompt_builder import PromptBuilder

class TestPromptBuilder(unittest.TestCase):
    def setUp(self):
        self.prompt_builder = PromptBuilder(prompts_dir='prompts')

    def test_load_prompts(self):
        # Ensure prompts are loaded
        self.assertIn('job_contexts', self.prompt_builder.prompts)
        self.assertIn('job_map', self.prompt_builder.prompts)
        # Add more as needed

    def test_get_prompt(self):
        prompt = self.prompt_builder.get_prompt('job_contexts', end_user='DevOps Engineer', job='Building Systems', n=10)
        self.assertIn('Act as a(n) DevOps Engineer', prompt)
        self.assertIn('List 10 contexts', prompt)

    def test_parse_job_contexts(self):
        response = """
        1. **IT Managed Services Provider** - A company looking to outsource the management of their IT infrastructure.
        2. **Network Security Specialist** - An individual focused on protecting the organization's network from cyber threats.
        """
        expected = [
            {
                "name": "IT Managed Services Provider",
                "description": "A company looking to outsource the management of their IT infrastructure."
            },
            {
                "name": "Network Security Specialist",
                "description": "An individual focused on protecting the organization's network from cyber threats."
            }
        ]
        result = self.prompt_builder.parse_job_contexts(response)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
