# utils.py
import json
from anytree import Node, RenderTree


def node_to_dict(node):
    """
    Recursively converts AnyTree nodes to dictionaries, including all relevant attributes.
    """
    return {
        "name": node.name,
        "description": getattr(node, 'description', "No description provided"),
        "processed": getattr(node, 'processed', False),
        "children": [node_to_dict(child) for child in node.children]
    }


def save_hierarchy_to_file(root, filename):
    """
    Saves the hierarchy to a JSON file.
    """
    hierarchy_dict = node_to_dict(root)
    with open(filename, 'w') as f:
        json.dump(hierarchy_dict, f, indent=4)


def update_hierarchy_in_file(root, filename):
    """
    Updates the hierarchy JSON file incrementally based on the root node's current state.
    """
    hierarchy_dict = node_to_dict(root)
    with open(filename, 'w') as f:
        json.dump(hierarchy_dict, f, indent=4)


def dict_to_tree(node_dict, parent=None):
    """
    Recursively converts a dictionary to an AnyTree Node.
    """
    node = Node(node_dict['name'],
                parent=parent,
                description=node_dict.get('description', ''),
                processed=node_dict.get('processed', False))
    for child in node_dict.get('children', []):
        dict_to_tree(child, parent=node)
    return node


def render_hierarchy_markdown(root):
    """
    Renders the hierarchy as a formatted Markdown string.
    """
    lines = []
    for node in root.descendants:
        depth = node.depth  # Root node has depth 0
        indent = '    ' * depth  # 4 spaces per level
        line = f"{indent}- **{node.name}**: {node.description}"
        lines.append(line)
    # Include the root node
    root_line = f"- **{root.name}**: {root.description}"
    lines.insert(0, root_line)
    return "\n".join(lines) + "\n"  # Add trailing newline


def save_hierarchy_to_markdown(hierarchy_root, markdown_filename):
    """
    Converts the hierarchy from a tree structure to Markdown and saves it to a Markdown file.

    Args:
        hierarchy_root (Node): The root node of the hierarchy tree structure.
        markdown_filename (str): The name of the Markdown file to save the output.
    """
    # Convert the hierarchy tree to Markdown format
    markdown_text = render_hierarchy_markdown(hierarchy_root)

    # Save the Markdown text to a file
    with open(markdown_filename, 'w') as f:
        f.write(markdown_text)


def save_json_hierarchy_to_markdown(json_filename, markdown_filename):
    """
    Loads the hierarchy from a JSON file, converts it to Markdown, and saves it to a Markdown file.
    """
    with open(json_filename, 'r') as f:
        hierarchy_dict = json.load(f)

    root = dict_to_tree(hierarchy_dict)

    with open(markdown_filename, 'w') as f:
        markdown_text = render_hierarchy_markdown(root)
        f.write(markdown_text)
