import logging
import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from anytree import Node

# Configure logging at the very beginning
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

def fetch_monolithic_document(mongo_uri, db_name, collection_name, industry="Finance"):
    """
    Fetch the single monolithic document from the MongoDB collection.
    """
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]
    document = collection.find_one({"industry": industry})
    return document

def create_node_documents(hierarchy_dict, parent_id=None, mongo_manager=None):
    """
    Recursively create separate MongoDB documents for each node in the hierarchy.

    Args:
        hierarchy_dict (dict): A dictionary representing the current node in the hierarchy.
        parent_id (str): The MongoDB ObjectId of the parent node (if any).
        mongo_manager (MongoClient): The MongoDB client to use for saving documents.

    Returns:
        str: The MongoDB ObjectId of the created document.
    """
    # Create a new document for the current node
    node_id = str(ObjectId())  # Generate a unique node_id for the document

    # Document for the current node
    node_document = {
        "node_id": node_id,
        "name": hierarchy_dict["name"],
        "description": hierarchy_dict.get("description", ""),
        "processed": hierarchy_dict.get("processed", False),
        "type": hierarchy_dict.get("type", ""),
        "industry": hierarchy_dict.get("industry", ""),
        "parent_id": parent_id,  # Set the parent_id (None for root nodes)
        "children_ids": []  # Initialize an empty list for children IDs
    }

    # Insert the node document into MongoDB
    result = mongo_manager.insert_one(node_document)
    logging.info(f"Inserted node '{node_document['name']}' with ID: {node_id}, parent ID: {parent_id}")

    # Recursively process all children of this node and add their IDs to children_ids
    for child in hierarchy_dict.get("children", []):
        child_id = create_node_documents(child, parent_id=node_id, mongo_manager=mongo_manager)
        node_document["children_ids"].append(child_id)

    # Update the node document in MongoDB with the updated children_ids
    if node_document["children_ids"]:
        mongo_manager.update_one({"_id": result.inserted_id}, {"$set": {"children_ids": node_document["children_ids"]}})
        logging.info(f"Updated node '{node_document['name']}' with children IDs: {node_document['children_ids']}")

    return node_id

def convert_monolithic_to_hierarchical(mongo_uri, db_name, source_collection, target_collection, industry="Finance"):
    """
    Converts a monolithic MongoDB hierarchy into a multi-document hierarchical structure.

    Args:
        mongo_uri (str): MongoDB URI for connecting to the database.
        db_name (str): Database name in MongoDB.
        source_collection (str): The name of the collection containing the monolithic document.
        target_collection (str): The name of the collection to save the new hierarchical documents.
        industry (str): Industry name to filter the document.

    Returns:
        None
    """
    # Initialize MongoDB client
    client = MongoClient(mongo_uri)
    db = client[db_name]
    source_col = db[source_collection]
    target_col = db[target_collection]

    # Fetch the monolithic document
    monolithic_document = fetch_monolithic_document(mongo_uri, db_name, source_collection, industry=industry)

    if not monolithic_document:
        print(f"No document found for industry '{industry}' in collection '{source_collection}'.")
        return

    # Ensure target collection is empty to avoid conflicts
    target_col.delete_many({"industry": industry})
    print(f"Cleared target collection '{target_collection}' for industry '{industry}'.")

    # Create the root node and recursively save all nodes
    print(f"Converting monolithic document for industry '{industry}' to hierarchical format...")
    root_id = create_node_documents(monolithic_document["hierarchy"], parent_id=None, mongo_manager=target_col)
    print(f"Conversion complete. Root node ID: {root_id}")

if __name__ == "__main__":
    # MongoDB connection details
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = os.getenv("MONGO_DB_NAME")
    SOURCE_COLLECTION = "jtbd_hierarchy"  # Replace with your source collection name
    TARGET_COLLECTION = "jtbd_hierarchy3"  # Replace with your target collection name

    # Convert the monolithic hierarchy to a multi-document hierarchical structure
    convert_monolithic_to_hierarchical(MONGO_URI, DB_NAME, SOURCE_COLLECTION, TARGET_COLLECTION, industry="Finance")
