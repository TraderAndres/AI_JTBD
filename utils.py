# utils.py
import json

from anytree import Node, RenderTree


def node_to_dict(node):
    """
    Recursively converts AnyTree nodes to dictionaries.
    """
    return {
        "name": node.name,
        "description": node.description if hasattr(node, 'description') else "",
        "children": [node_to_dict(child) for child in node.children]
    }

def save_hierarchy_to_file(root, filename):
    def node_to_dict(node):
        return {
            "name": node.name,
            "description": node.description,
            "children": [node_to_dict(child) for child in node.children]
        }
    hierarchy_dict = node_to_dict(root)
    with open(filename, 'w') as f:
        json.dump(hierarchy_dict, f, indent=4)

def save_hierarchy_to_text(json_filename, text_filename):
    with open(json_filename, 'r') as f:
        hierarchy_dict = json.load(f)

    def dict_to_tree(node_dict, parent=None):
        node = Node(node_dict['name'], parent=parent, description=node_dict.get('description', ''))
        for child in node_dict.get('children', []):
            dict_to_tree(child, parent=node)
        return node

    root = dict_to_tree(hierarchy_dict)

    with open(text_filename, 'w') as f:
        for pre, fill, node in RenderTree(root):
            f.write(f"{pre}{node.name}\n")

# def save_hierarchy_to_file(root, filename):
#     """
#     Saves the hierarchy to a JSON file.
#     """
#     hierarchy = node_to_dict(root)
#     with open(filename, 'w', encoding='utf-8') as f:
#         json.dump(hierarchy, f, indent=4)

# def convert_hierarchy_to_text(node, level=0):
#     """
#     Recursively traverses the hierarchy and builds hierarchical text.
#     """
#     lines = []
#     indent = '    ' * level  # 4 spaces per level for indentation

#     # Format the current node's name and description
#     if node.get("description"):
#         # Combine the name and description with bold formatting for the name
#         lines.append(f"{indent}- **{node['name']}**: {node['description']}")
#     else:
#         # Only show the name if there's no description
#         lines.append(f"{indent}- **{node['name']}**")

#     # Recursively process children, if any
#     for child in node.get("children", []):
#         lines.extend(convert_hierarchy_to_text(child, level + 1))

#     return lines

# def save_hierarchy_to_text(json_filename, text_filename):
#     """
#     Loads the hierarchy from a JSON file, converts it to hierarchical text,
#     and saves it to a text file.
#     """
#     # Load the JSON content from the file
#     with open(json_filename, "r", encoding='utf-8') as file:
#         hierarchy_data = json.load(file)

#     # Build the hierarchical text
#     hierarchical_text = convert_hierarchy_to_text(hierarchy_data)

#     # Join the lines into a single string
#     final_output = "\n".join(hierarchical_text)

#     # Save the hierarchical text to a file
#     with open(text_filename, "w", encoding='utf-8') as output_file:
#         output_file.write(final_output)
