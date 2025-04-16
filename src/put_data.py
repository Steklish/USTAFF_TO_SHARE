from .ChromaDataBase import ChromaDB
import os

ChromaDBClient = ChromaDB()
# Get all files in the data directory
data_dir = "data"
for filename in os.listdir(data_dir):
    file_path = os.path.join(data_dir, filename)
    if os.path.isfile(file_path):
        ChromaDBClient.add_document(file_path)
# d.add_document("data/filename")