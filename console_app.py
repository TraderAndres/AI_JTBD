# console_app.py
import json
import logging
from anytree import Node, RenderTree, PreOrderIter
from downstream_processor import DownstreamProcessor
from hierarchy_builder import HierarchyBuilder
from llm_interface import LLMInterface
from prompt_builder import PromptBuilder
from utils import save_hierarchy_to_file, dict_to_tree
from method_mapping import STEP_NAME_TO_METHOD  # Import the mapping

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Load an existing JSON hierarchy or create a new one
def load_hierarchy(file_path="Finance_hierarchy_old.json"):
    try:
        with open(file_path, 'r') as f:
            hierarchy_dict = json.load(f)
            root_node = dict_to_tree(hierarchy_dict)
            logging.info(f"Hierarchy loaded successfully from {file_path}.")
            # After loading the root node
            # print("Full Paths of All Nodes:")
            # print_node_paths(root_node)
            return root_node
    except FileNotFoundError:
        logging.warning(f"{file_path} not found. Creating a new hierarchy from scratch.")
        return None
    except Exception as e:
        logging.error(f"Failed to load hierarchy: {e}")
        return None


# Function to print full paths for all nodes
def print_node_paths(root):
    """
    Prints the full paths for all nodes in the hierarchy to identify where 'High Level Jobs' might be.
    """
    for node in PreOrderIter(root):
        path = " -> ".join([ancestor.name for ancestor in node.path])
        print(f"{path} (Processed: {node.processed})")


# Save the hierarchy to a JSON file
def save_hierarchy(root, file_path="hierarchy.json"):
    save_hierarchy_to_file(root, file_path)
    logging.info(f"Hierarchy saved to {file_path}.")


# Display all leaf nodes (job nodes) in the hierarchy
def display_leaf_nodes(root):
    """
    Display all leaf nodes in the hierarchy with their full paths.
    """
    leaf_nodes = get_job_nodes(root)
    print(f"\nTotal Job Nodes (Leaf Nodes): {len(leaf_nodes)}\n")
    for node in leaf_nodes:
        # Print the full path for each leaf node
        path = " -> ".join([ancestor.name for ancestor in node.path])
        print(f"{path} (Processed: {node.processed})")



# Display the current hierarchy in the console
def display_hierarchy(root):
    if root is None:
        print("Hierarchy is empty or not loaded.")
    else:
        for pre, fill, node in RenderTree(root):
            print(f"{pre}{node.name}: {node.description} (Processed: {node.processed})")



# Get a list of all job nodes (leaf nodes)
def get_job_nodes(root):
    """
    Return a list of all leaf nodes, which represent the actual job nodes in the hierarchy.
    """
    return [node for node in PreOrderIter(root) if node.is_leaf]

# Allow user to select a job node for processing
def select_node_for_processing(root):
    job_nodes = get_job_nodes(root)
    if not job_nodes:
        print("No job nodes available for selection.")
        return None

    print("\nAvailable Job Nodes for Expansion:")
    for idx, job_node in enumerate(job_nodes):
        print(f"{idx + 1}. {job_node.name} - {job_node.description}")

    selection = input("Select a node number to process (or type 'q' to quit): ")
    if selection.lower() == 'q':
        return None

    try:
        selected_idx = int(selection) - 1
        if 0 <= selected_idx < len(job_nodes):
            return job_nodes[selected_idx]
        else:
            print("Invalid selection. Please choose a valid node number.")
            return None
    except ValueError:
        print("Invalid input. Please enter a number.")
        return None


def process_steps(current_node, steps_list, downstream_processor):
    """
    Processes the hierarchical steps defined in the `steps_list`.
    Recursively creates child nodes for each step and processes them accordingly.
    """
    for step in steps_list:
        step_name = step['step']
        n = step['n']
        # Check if the step_name has a direct mapping to a method name
        if step_name in STEP_NAME_TO_METHOD:
            method_name = STEP_NAME_TO_METHOD[step_name]
        else:
            # Construct the method name dynamically if no direct mapping is found
            method_name = f"process_{step_name.lower().replace(' ', '_').replace('(', '').replace(')', '')}"



        # Get the processing method from downstream_processor
        processing_method = getattr(downstream_processor, method_name, None)
        if processing_method:
            # Capture initial number of children *before* calling processing_method
            initial_children_count = len(current_node.children)

            # Log the processing step
            logging.debug(f"Processing step '{step_name}' under '{current_node.name}'")
            logging.debug(f"Attempting to call method: {method_name}")

            # Explicitly pass arguments as named parameters
            if method_name == "process_job_map":
                # Explicitly specify fidelity and temp for process_job_map
                processing_method(node=current_node, fidelity="med", temp=0.1)
            else:
                # Explicitly specify all arguments for other methods
                processing_method(node=current_node, n=n, fidelity="comprehensive", temp=0.1)

            # Get the new child node(s) added (assuming one child per step for simplicity)
            new_child = None
            if len(current_node.children) > initial_children_count:
                new_child = current_node.children[-1]
                logging.debug(f"Added '{new_child.name}' under '{current_node.name}'")
            else:
                logging.error(f"No new child added for step: {step_name}")
                continue
        else:
            logging.error(f"No processing method found for step: {step_name}")
            continue

        # Recursively process child steps if any
        if 'children_steps' in step and new_child:
            process_steps(new_child, step['children_steps'], downstream_processor)

    # Mark the node as processed **only after completing all steps**
    current_node.processed = True
    logging.debug(f"Marked '{current_node.name}' as processed.")


# Process a selected node using the downstream processor
def process_node(node, downstream_processor):
    """
    Processes a single job node by executing downstream steps in a hierarchical order.
    Constructs the following hierarchy:

    High Level Job
    ├── Job Contexts
    │   ├── Job Map
    │   │   ├── Desired Outcomes (success metrics)
    │   │   ├── Themed Desired Outcomes (Themed Success Metrics)
    │   ├── Situational and Complexity Factors
    │   ├── Related Jobs
    │   ├── Emotional Jobs
    │   ├── Social Jobs
    │   ├── Financial Metrics of Purchasing Decision Makers
    │   ├── Ideal Job State
    │   │   ├── Potential Root Causes Preventing the Ideal State
    """
    print(f"Processing node: {node.name}")

    # Define the hierarchical steps with nested child steps
    steps = [
        {
            'step': 'Job Contexts',
            'n': 10,
            'children_steps': [
                {
                    'step': 'Job Map',
                    'n': 0,
                    'children_steps': [
                        {'step': 'Desired Outcomes (success metrics)', 'n': 20},
                        {'step': 'Themed Desired Outcomes (Themed Success Metrics)', 'n': 10},
                    ]
                },
                {'step': 'Situational Complexity Factors', 'n': 10},
                {'step': 'Related Jobs', 'n': 10},
                {'step': 'Emotional Jobs', 'n': 10},
                {'step': 'Social Jobs', 'n': 10},
                {'step': 'Financial Metrics of Purchasing Decision Makers', 'n': 10},
                {
                    'step': 'Ideal Job State',
                    'n': 15,
                    'children_steps': [
                        {'step': 'Potential Root Causes Preventing the Ideal State', 'n': 15},
                    ]
                },
            ]
        }
    ]

    # Start processing from the root job_node
    process_steps(node, steps, downstream_processor)

    # After processing all steps, mark the job as processed
    node.processed = True
    print(f"Node '{node.name}' has been processed.")

def main():
    # Initialize components
    llm = LLMInterface()
    prompt_builder = PromptBuilder()
    downstream_processor = DownstreamProcessor(prompt_builder, llm)

    # Load or create the hierarchy
    root = load_hierarchy()
    if root is None:
        print("No existing hierarchy found. Exiting.")
        return

    # Display the full paths of all leaf nodes
    display_leaf_nodes(root)

    # Select a node to process
    selected_node = select_node_for_processing(root)
    if selected_node is None:
        print("No node selected for processing. Exiting.")
        return

    # Process the selected node
    process_node(selected_node, downstream_processor)

    # Save the updated hierarchy back to the file
    save_hierarchy(root)
    print("Node processing completed and hierarchy saved.")

if __name__ == "__main__":
    main()