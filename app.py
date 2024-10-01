# app.py
# app.py
import json
import logging
import os
import streamlit as st
from anytree import PreOrderIter, Node
import inspect


from downstream_processor import DownstreamProcessor
from hierarchy_builder import HierarchyBuilder
from llm_interface import LLMInterface
from prompt_builder import PromptBuilder
from visualizer import Visualizer
from utils import save_hierarchy_to_file, save_hierarchy_to_markdown

logging.basicConfig(level=logging.DEBUG)

# Set the page layout to wide
st.set_page_config(layout="wide")

def main():
    st.title("Industry Hierarchy Builder")

    # Sidebar for options
    st.sidebar.header("Options")
    option = st.sidebar.selectbox("Choose an action", ["Generate New Hierarchy", "Load Existing Hierarchy"])

    # Initialize components
    llm = LLMInterface()
    prompt_builder = PromptBuilder()
    hierarchy_builder = HierarchyBuilder(llm, prompt_builder)
    visualizer = Visualizer()
    downstream_processor = DownstreamProcessor(prompt_builder, llm)

    if option == "Generate New Hierarchy":
        generate_new_hierarchy(hierarchy_builder, downstream_processor, visualizer)
    elif option == "Load Existing Hierarchy":
        load_existing_hierarchy(hierarchy_builder, downstream_processor, visualizer)


def generate_new_hierarchy(hierarchy_builder, downstream_processor, visualizer):
    st.header("Generate a New Hierarchy")

    industry = st.text_input("Enter the Industry", value="Finance")
    fidelity = st.selectbox("Select Fidelity", ["low", "med", "high", "short list of 3"])
    n_end_users = st.number_input("Number of End Users per Category", min_value=1, max_value=10, value=2)
    n_jobs = st.number_input("Number of Jobs per End User", min_value=1, max_value=20, value=2)

    if st.button("Build Hierarchy"):
        with st.spinner("Building hierarchy..."):
            hierarchy_root = hierarchy_builder.build_hierarchy(industry, fidelity, n_end_users, n_jobs)
            visualizer.display_hierarchy(hierarchy_root)
            # Save hierarchy
            json_filename = f"{industry}_hierarchy.json"
            save_hierarchy_to_file(hierarchy_root, json_filename)
            save_hierarchy_to_markdown(json_filename, f"{industry}_hierarchy_output.md")
            st.success(f"Hierarchy built and saved to {json_filename} and {industry}_hierarchy_output.txt")
            # Provide download links
            with open(json_filename, 'r') as f:
                json_data = f.read()
            st.download_button("Download JSON", json_data, file_name=json_filename, mime="application/json")
            with open(f"{industry}_hierarchy_output.txt", 'r') as f:
                text_data = f.read()
            st.download_button("Download Hierarchical Text", text_data, file_name=f"{industry}_hierarchy_output.txt", mime="text/plain")
            # Proceed to job selection
            display_job_selection(hierarchy_builder, downstream_processor, visualizer)

def load_existing_hierarchy(hierarchy_builder, downstream_processor, visualizer):
    st.header("Load an Existing Hierarchy")

    uploaded_file = st.file_uploader("Upload Hierarchy JSON", type=["json"])

    if uploaded_file is not None:
        with st.spinner("Loading hierarchy..."):
            try:
                hierarchy_data = json.load(uploaded_file)
                # Convert JSON to anytree Node structure
                hierarchy_root = json_to_anytree(hierarchy_data)
                hierarchy_builder.job_nodes = get_job_nodes(hierarchy_root)
                visualizer.display_hierarchy(hierarchy_root)
                st.success("Hierarchy loaded successfully.")
                # Proceed to job selection
                display_job_selection(hierarchy_builder, downstream_processor, visualizer)
            except Exception as e:
                st.error(f"Error loading hierarchy: {e}")

def json_to_anytree(data, parent=None):
    # Check if data is None or empty
    if not data:
        return None

    try:
        # Create a new node if data is valid
        node = Node(
            data['name'],
            parent=parent,
            description=data.get('description', ''),
            processed=data.get('processed', False)
        )
    except KeyError as e:
        st.error(f"Missing key in data: {e}. Data: {data}")
        return None  # Return None if the node cannot be created

    for child in data.get('children', []):
        json_to_anytree(child, parent=node)

    return node

def get_job_nodes(root):
    job_nodes = []
    for node in PreOrderIter(root):
        # Assuming Jobs are leaf nodes (no children)
        if not node.children:
            job_nodes.append(node)
    return job_nodes

def display_job_selection(hierarchy_builder, downstream_processor, visualizer):
    st.header("Select Jobs for Further Processing")

    if not hierarchy_builder.job_nodes:
        st.warning("No Jobs available for selection.")
        return

    # Create a list of job paths for display
    job_paths = ["/".join([ancestor.name for ancestor in job_node.path]) for job_node in hierarchy_builder.job_nodes]

    # Ensure job_paths is a real list for testing purposes
    job_paths = list(job_paths)  # Convert to list in case it's a generator or mock

    # Search box
    search_query = st.text_input("Search Jobs")
    if search_query:
        filtered_jobs = [path for path in job_paths if search_query.lower() in path.lower()]
    else:
        filtered_jobs = job_paths

    # Convert filtered_jobs to a real list and total_jobs to an integer
    filtered_jobs = list(filtered_jobs)
    total_jobs = len(filtered_jobs)
    assert isinstance(total_jobs, int), "total_jobs must be an integer"

    # # Pagination variables
    # page_size = 10
    # total_jobs = len(filtered_jobs)
    # total_pages = (total_jobs + page_size - 1) // page_size
    # current_page = st.number_input("Page", min_value=1, max_value=max(total_pages, 1), value=1)

    # start_idx = (current_page - 1) * page_size
    # end_idx = min(start_idx + page_size, total_jobs)
    # paginated_jobs = filtered_jobs[start_idx:end_idx]

    # Multiselect with job paths
    selected_jobs = st.multiselect("Select Jobs to Process", options=filtered_jobs)

    if st.button("Process Selected Jobs"):
        if not selected_jobs:
            st.warning("No Jobs selected.")
            return
        with st.spinner("Processing selected Jobs..."):
            # Retrieve selected Job nodes
            selected_job_nodes = [node for node, path in zip(hierarchy_builder.job_nodes, job_paths) if path in selected_jobs]
            for job_node in selected_job_nodes:
                process_job(job_node, downstream_processor, hierarchy_builder, visualizer)
            # Save updated hierarchy
            json_filename = f"{hierarchy_builder.industry}_hierarchy.json"
            save_hierarchy_to_file(hierarchy_builder.root, json_filename)
            save_hierarchy_to_markdown(json_filename, 
                                   f"{hierarchy_builder.industry}_hierarchy_output.md"
                                  )
            st.success("Selected Jobs have been processed and hierarchy updated.")
            # Refresh visualization
            visualizer.display_hierarchy(hierarchy_builder.root)

# # def process_job(job_node, downstream_processor, hierarchy_builder, visualizer):
#     """
#     Processes a single job node by executing all downstream steps in hierarchical order.
#     """
#     # Define the hierarchical order of steps
#     steps = [
#         {'step': 'Job Contexts', 'n': 20},
#         {'step': 'Job Map', 'n': 0},
#         {'step': 'Desired Outcomes (success metrics)', 'n': 10},
#         {'step': 'Themed Desired Outcomes (Themed Success Metrics)', 'n': 10},
#         {'step': 'Situational and Complexity Factors', 'n': 15},
#         {'step': 'Related Jobs', 'n': 10},
#         {'step': 'Emotional Jobs', 'n': 10},
#         {'step': 'Social Jobs', 'n': 10},
#         {'step': 'Financial Metrics of Purchasing Decision Makers', 'n': 10},
#         {'step': 'Ideal Job State', 'n': 15},
#         {'step': 'Potential Root Causes Preventing the Ideal State', 'n': 15},
#     ]
#     fidelity = hierarchy_builder.fidelity
#     temp = 0.1  # or fetch dynamically

#     for s in steps:
#         step = s['step']
#         n = s['n']
#         if step == 'Job Contexts':
#             downstream_processor.process_job_contexts(job_node, n, fidelity, temp)
#         elif step == 'Job Map':
#             downstream_processor.process_job_map(job_node, fidelity, temp)
#         elif step == 'Desired Outcomes (success metrics)':
#             downstream_processor.process_desired_outcomes(job_node, n, fidelity, temp)
#         elif step == 'Themed Desired Outcomes (Themed Success Metrics)':
#             downstream_processor.process_themed_desired_outcomes(job_node, n, fidelity, temp)
#         elif step == 'Situational and Complexity Factors':
#             downstream_processor.process_situational_complexity_factors(job_node, n, fidelity, temp)
#         elif step == 'Related Jobs':
#             downstream_processor.process_related_jobs(job_node, n, fidelity, temp)
#         elif step == 'Emotional Jobs':
#             downstream_processor.process_emotional_jobs(job_node, n, fidelity, temp)
#         elif step == 'Social Jobs':
#             downstream_processor.process_social_jobs(job_node, n, fidelity, temp)
#         elif step == 'Financial Metrics of Purchasing Decision Makers':
#             downstream_processor.process_financial_metrics(job_node, n, fidelity, temp)
#         elif step == 'Ideal Job State':
#             downstream_processor.process_ideal_job_state(job_node, n, fidelity, temp)
#         elif step == 'Potential Root Causes Preventing the Ideal State':
#             downstream_processor.process_potential_root_causes(job_node, n, fidelity, temp)

#     # After processing all steps, mark the job as processed
#     job_node.processed = True

#     # Optionally, update the hierarchy visualization
#     visualizer.display_hierarchy(hierarchy_builder.root)

def process_job(job_node, downstream_processor, hierarchy_builder, visualizer):
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
    fidelity = hierarchy_builder.fidelity
    temp = 0.1  # or fetch dynamically

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

    def process_steps(current_node, steps_list):
        for step in steps_list:
            step_name = step['step']
            n = step['n']
            # Dynamically construct the method name
            method_name = f"process_{step_name.lower().replace(' ', '_').replace('(', '').replace(')', '')}"
            
            # Get the processing method from downstream_processor
            processing_method = getattr(downstream_processor, method_name, None)
            if processing_method:
                # Get current number of children before processing
                initial_children_count = len(current_node.children)
                # Log the processing step
                logging.debug(f"Processing step '{step_name}' under '{current_node.name}'")
                # Pass only the required arguments
                if method_name == "process_job_map":
                    # process_job_map requires only (node, fidelity, temp)
                    processing_method(current_node, fidelity, temp)
                else:
                    # Default case: Pass (node, n, fidelity, temp) if method expects those arguments
                    processing_method(current_node, n, fidelity, temp)
                # Get the new child added (assumes one child per step)
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
            if 'children_steps' in step:
                process_steps(new_child, step['children_steps'])

            # After processing, mark the node as processed to prevent reprocessing
            new_child.processed = True
            logging.debug(f"Marked '{new_child.name}' as processed.")

    # Start processing from the root job_node
    process_steps(job_node, steps)

    # After processing all steps, mark the job as processed
    job_node.processed = True

    # Optionally, update the hierarchy visualization
    visualizer.display_hierarchy(hierarchy_builder.root)


def handle_user_selection(downstream_processor, root_node, visualizer):
    # Display current hierarchy
    visualizer.display_hierarchy(root_node)

    # Display selection options for further expansion
    st.header("Select Nodes for Expansion")
    unprocessed_nodes = [node for node in PreOrderIter(root_node) if not node.processed]
    options = [node.name for node in unprocessed_nodes]

    selected_option = st.selectbox("Choose a node to expand further", options)
    if selected_option:
        # Find and process the selected node
        selected_node = next(node for node in PreOrderIter(root_node) if node.name == selected_option)
        process_job(selected_node, downstream_processor, root_node, visualizer)
        

def main_app():
    main()

if __name__ == "__main__":
    main_app()
