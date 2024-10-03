# tests/test_mongo_manager.py

import unittest
from unittest.mock import MagicMock, patch
from mongo_manager import MongoDBManager


class TestMongoDBManager(unittest.TestCase):
    def setUp(self):
        # Create a mock MongoDB client and database
        self.mock_client = MagicMock()
        self.mock_db = self.mock_client['test_db']
        self.mongo_manager = MongoDBManager(uri="mongodb://localhost:27017", db_name="test_db")
        self.mongo_manager.client = self.mock_client  # Replace client with mock
        self.mongo_manager.db = self.mock_db

        # Set the collection to a mock collection
        self.mongo_manager.set_collection("test_collection")
        self.mock_collection = self.mongo_manager.db['test_collection']

    def test_set_collection(self):
        self.mongo_manager.set_collection("new_collection")
        self.assertEqual(self.mongo_manager.collection_name, "new_collection")

    def test_insert_entry(self):
        entry = {"key": "value"}
        # Mock the insert_one return value to simulate an insertion result
        self.mock_collection.insert_one.return_value.inserted_id = "mock_id"

        inserted_id = self.mongo_manager.insert_entry(entry)
        self.mock_collection.insert_one.assert_called_once_with(entry)
        self.assertEqual(inserted_id, "mock_id")

    def test_find_entry(self):
        query = {"key": "value"}
        mock_entry = {"key": "value", "name": "Test Entry"}
        self.mock_collection.find_one.return_value = mock_entry

        found_entry = self.mongo_manager.find_entry(query)
        self.mock_collection.find_one.assert_called_once_with(query)
        self.assertEqual(found_entry, mock_entry)

    def test_update_entry(self):
        query = {"key": "value"}
        new_values = {"name": "Updated Entry"}
        self.mock_collection.update_one.return_value.modified_count = 1

        update_result = self.mongo_manager.update_entry(query, new_values)
        self.mock_collection.update_one.assert_called_once_with(query, {"$set": new_values})
        self.assertEqual(update_result.modified_count, 1)

    def test_delete_entry(self):
        query = {"key": "value"}
        self.mock_collection.delete_one.return_value.deleted_count = 1

        delete_result = self.mongo_manager.delete_entry(query)
        self.mock_collection.delete_one.assert_called_once_with(query)
        self.assertEqual(delete_result.deleted_count, 1)

    def test_get_all_entries(self):
        mock_entries = [
            {"key": "value1", "name": "Entry 1"},
            {"key": "value2", "name": "Entry 2"}
        ]
        self.mock_collection.find.return_value = mock_entries

        entries = self.mongo_manager.get_all_entries()
        self.mock_collection.find.assert_called_once()
        self.assertEqual(entries, mock_entries)

    def test_insert_without_collection_set(self):
        self.mongo_manager.collection_name = None
        with self.assertRaises(ValueError) as context:
            self.mongo_manager.insert_entry({"key": "value"})
        self.assertEqual(str(context.exception), "Collection name is not set.")

    def test_find_without_collection_set(self):
        self.mongo_manager.collection_name = None
        with self.assertRaises(ValueError) as context:
            self.mongo_manager.find_entry({"key": "value"})
        self.assertEqual(str(context.exception), "Collection name is not set.")

    def test_update_without_collection_set(self):
        self.mongo_manager.collection_name = None
        with self.assertRaises(ValueError) as context:
            self.mongo_manager.update_entry({"key": "value"}, {"name": "New Value"})
        self.assertEqual(str(context.exception), "Collection name is not set.")

    def test_delete_without_collection_set(self):
        self.mongo_manager.collection_name = None
        with self.assertRaises(ValueError) as context:
            self.mongo_manager.delete_entry({"key": "value"})
        self.assertEqual(str(context.exception), "Collection name is not set.")

    def test_get_all_without_collection_set(self):
        self.mongo_manager.collection_name = None
        with self.assertRaises(ValueError) as context:
            self.mongo_manager.get_all_entries()
        self.assertEqual(str(context.exception), "Collection name is not set.")


if __name__ == '__main__':
    unittest.main()
