# test_conversion.py
import os
from pymongo import MongoClient
from anytree import Node, RenderTree
from anytree.exporter import DictExporter
from utils import render_hierarchy_markdown  # Assuming you have this function for Markdown rendering

def fetch_nodes_from_mongo(mongo_uri, db_name, collection_name, industry="Finance"):
    """
    Fetches all nodes related to a specified industry from the MongoDB collection.

    Args:
        mongo_uri (str): The URI for connecting to MongoDB.
        db_name (str): The database name in MongoDB.
        collection_name (str): The collection name to fetch the nodes from.
        industry (str): The industry name to filter the nodes.

    Returns:
        list: A list of node documents from MongoDB.
    """
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    # Fetch all documents for the specified industry
    nodes = collection.find({"industry": industry})
    return list(nodes)

def build_hierarchy_from_nodes(nodes):
    """
    Rebuilds a tree hierarchy from a list of node documents fetched from MongoDB.

    Args:
        nodes (list): List of node documents.

    Returns:
        Node: The root node of the reconstructed hierarchy.
    """
    # Create a lookup table for all nodes by their node_id
    node_lookup = {node['node_id']: node for node in nodes}

    # Create a lookup table for AnyTree nodes by node_id
    anytree_lookup = {}

    # Create AnyTree nodes and establish parent-child relationships
    for node_id, node_data in node_lookup.items():
        # Create AnyTree node
        anytree_node = Node(
            node_data["name"],
            description=node_data.get("description", ""),
            type=node_data.get("type", ""),
            node_id=node_id
        )
        anytree_lookup[node_id] = anytree_node

    # Print to verify the node creation
    print(f"Created {len(anytree_lookup)} AnyTree nodes.")

    # Establish parent-child relationships
    for node_id, node_data in node_lookup.items():
        parent_id = node_data.get("parent_id")
        if parent_id:
            if parent_id in anytree_lookup:
                anytree_node = anytree_lookup[node_id]
                parent_node = anytree_lookup[parent_id]
                anytree_node.parent = parent_node
            else:
                print(f"Warning: Parent ID {parent_id} not found for node ID {node_id}.")

    # Find the root node (node with no parent)
    root_nodes = [node for node in anytree_lookup.values() if node.is_root]
    print(f"Number of root nodes found: {len(root_nodes)}")

    if not root_nodes:
        raise ValueError("No root node found in the hierarchy data.")
    elif len(root_nodes) > 1:
        raise ValueError("Multiple root nodes found in the hierarchy data.")

    return root_nodes[0]

def save_hierarchy_to_markdown(root_node, markdown_filename):
    """
    Converts the AnyTree hierarchy to a Markdown format and saves it to a Markdown file.

    Args:
        root_node (Node): The root node of the hierarchy.
        markdown_filename (str): The filename for saving the Markdown representation.
    """
    markdown_text = render_hierarchy_markdown(root_node)
    with open(markdown_filename, 'w') as f:
        f.write(markdown_text)

def render_hierarchy_markdown(root_node):
    """
    Render the AnyTree hierarchy into Markdown format.

    Args:
        root_node (Node): The root node of the hierarchy.

    Returns:
        str: The hierarchy as a Markdown string.
    """
    lines = []

    def add_node_lines(node, depth=0):
        indent = ' ' * depth * 2  # 2 spaces per depth level
        lines.append(f"{indent}- {node.name}: {node.description}")
        for child in node.children:
            add_node_lines(child, depth + 1)

    add_node_lines(root_node)
    return "\n".join(lines)

def test_conversion():
    # Pull MongoDB connection details from environment variables
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB_NAME")
    collection_name = "jtbd_hierarchy3"

    if not all([mongo_uri, db_name, collection_name]):
        print("Error: MongoDB connection details are not set in environment variables.")
        return

    # Fetch nodes from MongoDB
    nodes = fetch_nodes_from_mongo(mongo_uri, db_name, collection_name)

    if nodes:
        # Rebuild hierarchy from nodes
        root_node = build_hierarchy_from_nodes(nodes)

        # Save the hierarchy to Markdown format
        text_output = "TESTMONGO3_hierarchy_output.md"
        save_hierarchy_to_markdown(root_node, text_output)
        print(f"Hierarchical text saved to '{text_output}'.")
    else:
        print("No hierarchy data found in MongoDB.")

if __name__ == "__main__":
    test_conversion()
