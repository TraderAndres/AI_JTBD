from pymongo import MongoClient

# Replace <username> and <password> with your credentials
uri = "mongodb+srv://newmediamavericks:FwPWSonHO5nVD9Jn@clusterjtbd.qtbt9.mongodb.net/?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true"

try:
    client = MongoClient(uri)
    # Check if the connection is established
    client.server_info()  # This will throw an exception if it can't connect
    print("MongoDB connection successful!")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
