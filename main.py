# main.py
import logging
import os

from hierarchy_builder import HierarchyBuilder
from llm_interface import LLMInterface
from prompt_builder import PromptBuilder
from utils import save_hierarchy_to_file, save_hierarchy_to_text
from visualizer import Visualizer

# Configure logging at the very beginning
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def get_user_inputs():
    industry = input("Enter the industry you want to analyze (e.g., Finance): ").strip()
    fidelity = input("Enter the fidelity of analysis (e.g., comprehensive): ").strip().lower()
    return industry, fidelity

def list_jobs(hierarchy_builder):
    """
    Lists all Jobs with unique IDs.
    """
    print("\nAvailable Jobs for Further Processing:")
    print("---------------------------------------")
    for idx, job_node in enumerate(hierarchy_builder.job_nodes, start=1):
        # Retrieve the full path to the Job node for better context
        path = "/".join([ancestor.name for ancestor in job_node.path])
        print(f"{idx}. {path}")
    print("---------------------------------------")

def get_job_selection(total_jobs):
    """
    Prompts the user to select Jobs by entering their numbers.
    """
    selection = input(f"Enter the numbers of the Jobs you want to process (comma-separated, e.g., 1,3,5): ")
    selected_indices = []
    try:
        selected_indices = [int(num.strip()) for num in selection.split(",") if num.strip().isdigit()]
    except ValueError:
        pass  # Invalid input will result in empty selection

    # Validate selection
    selected_indices = [num for num in selected_indices if 1 <= num <= total_jobs]
    if not selected_indices:
        print("No valid selections made. Exiting selection process.")
    return selected_indices

def process_selected_jobs(selected_jobs, hierarchy_builder, prompt_builder, llm):
    """
    Processes the selected Jobs by running downstream prompts.
    """
    for job_node in selected_jobs:
        print(f"\nProcessing Job: {job_node.name}")
        # Here, you can implement the downstream processing steps.
        # For example:
        # - Run additional prompts
        # - Generate desired outcomes
        # - etc.
        # This is a placeholder for your actual processing logic.
        # Example:
        # desired_outcomes = run_desired_outcomes_prompt(job_node)
        pass  # Replace with actual processing
        
def main():
    # Step 0: Get User Inputs
    industry, fidelity = get_user_inputs()

    # Initialize components
    llm = LLMInterface()
    prompt_builder = PromptBuilder()
    hierarchy_builder = HierarchyBuilder(llm,
                                         prompt_builder,
                                         fidelity=fidelity)
    visualizer = Visualizer()

    # Step 1-4: Build Hierarchy
    logging.info("Starting hierarchy generation.  This may take a few minutes...")
    hierarchy_root = hierarchy_builder.build_hierarchy(industry,
                                                        fidelity=fidelity,
                                                        n_end_users=2,
                                                        n_jobs=2)
    logging.info("Hierarchy generation completed.")

    # Step 2: Visualize Hierarchy
    logging.info("Displaying generated hierarchy.")
    visualizer.display_hierarchy(hierarchy_root)

    # Step 3: Save Hierarchy to JSON File
    json_filename = f"{industry}_hierarchy.json"
    save_hierarchy_to_file(hierarchy_root, json_filename)
    logging.info(f"Hierarchy saved to '{json_filename}'.")

    # Step 4: Convert and Save Hierarchy to Text File
    text_filename = f"{industry}_hierarchy_output.txt"
    save_hierarchy_to_text(json_filename, text_filename)
    logging.info(f"Hierarchical text saved to '{text_filename}'. You can now copy and paste this into Coda or Notion.")

    # Step 5: List all Jobs and Allow User to Select
    if hierarchy_builder.job_nodes:
        list_jobs(hierarchy_builder)
        selected_indices = get_job_selection(len(hierarchy_builder.job_nodes))
        if selected_indices:
            selected_jobs = [hierarchy_builder.job_nodes[idx - 1] for idx in selected_indices]
            process_selected_jobs(selected_jobs, hierarchy_builder, prompt_builder, llm)
        else:
            logging.info("No Jobs selected for further processing.")
    else:
        logging.info("No Jobs found in the hierarchy.")




if __name__ == "__main__":
    # Ensure OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: The environment variable OPENAI_API_KEY is not set.")
        print(
            "Please set it using 'export OPENAI_API_KEY=your_api_key' and try again."
        )
    else:
        main()
