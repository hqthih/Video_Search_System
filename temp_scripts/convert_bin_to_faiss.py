import os
import glob
import faiss
import numpy as np
from tqdm import tqdm


import faiss
import numpy as np
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection

# Load the FAISS index from the binary file
index = faiss.read_index("/mnt/data/Video-Search-System-App/faiss_clip_cosine.bin")

# Extract vectors and IDs from the FAISS index
vectors = index.reconstruct_n(0, index.ntotal)
ids = np.arange(index.ntotal)

# Validate the data
assert vectors.shape[0] == ids.shape[0], "Number of vectors and IDs must match"
assert vectors.dtype == np.float32, "Vectors must be of type float32"
assert ids.dtype == np.int64, "IDs must be of type int64"

print(vectors.shape[1])
# Connect to Milvus
connections.connect("default", host="localhost", port="19530")

# Drop the existing collection
collection_name = "clip"
# existing_collection = Collection(collection_name)
# existing_collection.drop()

# Define the schema for the collection
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=vectors.shape[1])
]
schema = CollectionSchema(fields, collection_name)

# Create a collection
collection = Collection(collection_name, schema)

# Insert vectors into the collection
data = [
    ids.tolist(),  # id field
    vectors.tolist()  # vector field
]


# Insert data in batches with progress tracking
batch_size = 100
num_vectors = vectors.shape[0]
for i in tqdm(range(0, num_vectors, batch_size), desc="Inserting data"):
    batch_vectors = vectors[i:i + batch_size].tolist()
    batch_ids = ids[i:i + batch_size].tolist()
    data_batch = [
        batch_ids,  # id field
        batch_vectors  # vector field
    ]
    collection.insert(data_batch)


# collection.insert(data)

# Create an index on the vector field
index_params = {
    "index_type": "IVF_FLAT",
    "metric_type": "COSINE",
    "params": {"nlist": 128}
}
collection.create_index("vector", index_params)

# Load the collection into memory
collection.load()

# Perform a basic search to verify
query_vectors = np.random.random([1, vectors.shape[1]]).tolist()
search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
results = collection.search(query_vectors, "vector", search_params, limit=3)

# Print the search results
for result in results:
    print(result)