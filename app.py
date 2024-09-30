# app.py
import json
import os

import streamlit as st
from anytree import PreOrderIter, Node

from downstream_processor import DownstreamProcessor
from hierarchy_builder import HierarchyBuilder
from llm_interface import LLMInterface
from prompt_builder import PromptBuilder
from visualizer import Visualizer
from utils import save_hierarchy_to_file, save_hierarchy_to_text


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
        generate_new_hierarchy(hierarchy_builder, visualizer)
    elif option == "Load Existing Hierarchy":
        load_existing_hierarchy(hierarchy_builder, visualizer)


def generate_new_hierarchy(hierarchy_builder, visualizer):
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
            save_hierarchy_to_text(json_filename, f"{industry}_hierarchy_output.txt")
            st.success(f"Hierarchy built and saved to {json_filename} and {industry}_hierarchy_output.txt")
            # Provide download links
            with open(json_filename, 'r') as f:
                json_data = f.read()
            st.download_button("Download JSON", json_data, file_name=json_filename, mime="application/json")
            with open(f"{industry}_hierarchy_output.txt", 'r') as f:
                text_data = f.read()
            st.download_button("Download Hierarchical Text", text_data, file_name=f"{industry}_hierarchy_output.txt", mime="text/plain")
            # Proceed to job selection
            display_job_selection(hierarchy_builder, visualizer)

def load_existing_hierarchy(hierarchy_builder, visualizer):
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
                display_job_selection(hierarchy_builder, visualizer)
            except Exception as e:
                st.error(f"Error loading hierarchy: {e}")

def json_to_anytree(data, parent=None):
    node = Node(data['name'], parent=parent, description=data.get('description', ''))
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

def display_job_selection(hierarchy_builder, visualizer):
    st.header("Select Jobs for Further Processing")

    if not hierarchy_builder.job_nodes:
        st.warning("No Jobs available for selection.")
        return

    # Create a list of job paths for display
    job_paths = ["/".join([ancestor.name for ancestor in job_node.path]) for job_node in hierarchy_builder.job_nodes]

    # Search box
    search_query = st.text_input("Search Jobs")
    if search_query:
        filtered_jobs = [path for path in job_paths if search_query.lower() in path.lower()]
    else:
        filtered_jobs = job_paths

    # Pagination variables
    page_size = 10
    total_jobs = len(filtered_jobs)
    total_pages = (total_jobs + page_size - 1) // page_size
    current_page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)

    start_idx = (current_page - 1) * page_size
    end_idx = min(start_idx + page_size, total_jobs)
    paginated_jobs = filtered_jobs[start_idx:end_idx]

    # Multiselect with job paths
    selected_jobs = st.multiselect("Select Jobs to Process", options=job_paths)

    if st.button("Process Selected Jobs"):
        if not selected_jobs:
            st.warning("No Jobs selected.")
            return
        with st.spinner("Processing selected Jobs..."):
            # Retrieve selected Job nodes
            selected_job_nodes = [node for node, path in zip(hierarchy_builder.job_nodes, job_paths) if path in selected_jobs]
            process_selected_jobs(selected_job_nodes, hierarchy_builder, visualizer)
            st.success("Selected Jobs have been processed.")
            # Optionally, provide download links or display results

def process_selected_jobs(selected_jobs, hierarchy_builder, visualizer):
    """
    Processes the selected Jobs by running downstream prompts.
    """
    # Initialize downstream processor
    prompt_builder = hierarchy_builder.prompt_builder
    llm = hierarchy_builder.llm
    downstream_processor = DownstreamProcessor(prompt_builder, llm)

    for job_node in selected_jobs:
        st.write(f"### Processing Job: {job_node.name}")
        st.write(f"**Description:** {job_node.description}")

        # Define the downstream steps you want to process
        downstream_steps = [
            "Job Contexts",
            "Job Map",
            "Desired Outcomes",
            # Add other steps as needed
        ]

        # Example: Processing "Job Contexts"
        for step in downstream_steps:
            st.subheader(step)
            if step == "Job Contexts":
                n = 10  # Number of contexts to generate
                fidelity = "high"  # Example fidelity
                contexts = downstream_processor.process_job_contexts(
                    end_user="DevOps Engineer",
                    job="Building Operationally Efficient and Secure Enterprise Systems",
                    context="",
                    n=n,
                    fidelity=fidelity,
                    temp=0.1
                )
                # Display the contexts
                for ctx in contexts:
                    st.markdown(f"**{ctx['context_name']}** - {ctx['explanation']}")
            elif step == "Job Map":
                fidelity = "high"
                job_map = downstream_processor.process_job_map(
                    end_user="DevOps Engineer",
                    job="Building Operationally Efficient and Secure Enterprise Systems",
                    context="",
                    fidelity=fidelity,
                    temp=0.1
                )
                # Display the job map
                for jm in job_map:
                    st.markdown(f"**{jm['step_name']}** - {jm['explanation']}")
            elif step == "Desired Outcomes":
                n = 20
                desired_outcomes = downstream_processor.process_desired_outcomes(
                    end_user="DevOps Engineer",
                    job="Building Operationally Efficient and Secure Enterprise Systems",
                    context="",
                    step="Desired Outcomes",
                    n=n,
                    fidelity="high",
                    temp=0.1
                )
                for outcome in desired_outcomes:
                    st.markdown(f"- **{outcome['statement']}** - {outcome['description']}")
            # Implement other steps similarly...

        # Optionally, you can store the results back into the hierarchy or another data structure
        # For example, adding attributes to the job_node
        # job_node.contexts = contexts
        # job_node.job_map = job_map
        # job_node.desired_outcomes = desired_outcomes

    # After processing all jobs, you can visualize or save the results as needed

def main_app():
    main()

if __name__ == "__main__":
    main_app()
