# tree_builder.py
import json
from anytree import Node, RenderTree

class TreeBuilder:
    def __init__(self, llm_interface, prompt_builder):
        self.llm = llm_interface
        self.prompt_builder = prompt_builder

    def parse_response(self, response):
        try:
            data = json.loads(response)
            if isinstance(data, list):
                return data
            else:
                print("Unexpected response format. Expected a list.")
                return []
        except json.JSONDecodeError:
            print("Failed to parse JSON response.")
            return []

    def build_tree(self, initial_response, depth):
        root = Node("Root")
        first_level_items = self.parse_response(initial_response)
        for item in first_level_items:
            child = Node(item, parent=root)
            self._recursive_build(child, current_depth=1, max_depth=depth)
        return root

    def _recursive_build(self, node, current_depth, max_depth):
        if current_depth >= max_depth:
            return
        prompt = self.prompt_builder.build_recursive_prompt(node.name, current_depth + 1)
        response = self.llm.get_response(prompt)
        child_items = self.parse_response(response)
        for item in child_items:
            child = Node(item, parent=node)
            self._recursive_build(child, current_depth + 1, max_depth)
