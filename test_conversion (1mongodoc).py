# test_conversion.py
import os
import json
from pymongo import MongoClient
from utils import dict_to_tree, render_hierarchy_markdown

def fetch_hierarchy_from_mongo(mongo_uri, db_name, collection_name, industry="Finance"):
    """
    Fetches the hierarchy from the MongoDB collection based on the specified industry.
    """
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]
    # Find the hierarchy for the specified industry
    hierarchy = collection.find_one({"industry": industry})
    if hierarchy and "hierarchy" in hierarchy:
        return hierarchy["hierarchy"]  # Return only the 'hierarchy' field content
    return None

def save_hierarchy_to_markdown(hierarchy_dict, markdown_filename):
    """
    Converts a hierarchy dictionary directly to Markdown and saves it to a Markdown file.
    """
    # Convert dictionary to a tree structure
    root = dict_to_tree(hierarchy_dict)

    # Save the Markdown representation of the hierarchy
    with open(markdown_filename, 'w') as f:
        markdown_text = render_hierarchy_markdown(root)
        f.write(markdown_text)

def test_conversion():
    # Pull MongoDB connection details from environment variables
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB_NAME")
    collection_name = "jtbd_hierarchy2"

    if not all([mongo_uri, db_name, collection_name]):
        print("Error: MongoDB connection details are not set in environment variables.")
        return

    # Fetch the hierarchy from MongoDB
    hierarchy_data = fetch_hierarchy_from_mongo(mongo_uri, db_name, collection_name)

    if hierarchy_data:
        # Save the hierarchy to Markdown format
        text_output = "TESTMONGO_hierarchy_output.md"
        save_hierarchy_to_markdown(hierarchy_data, text_output)
        print(f"Hierarchical text saved to '{text_output}'.")
    else:
        print("No hierarchy data found in MongoDB.")

if __name__ == "__main__":
    test_conversion()
