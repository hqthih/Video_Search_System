import os
import glob
import faiss
import numpy as np
from tqdm import tqdm
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection

# Load the FAISS index from the binary file
index = faiss.read_index("/mnt/data/Video-Search-System-Infra/Video-Search-System-App/docker_images/dataset_extraction/faiss_clipv2_cosine.bin")

# Get total number of vectors and dimension
total_vectors = index.ntotal
vector_dim = index.d

print(f"Total vectors: {total_vectors}, dimension: {vector_dim}")

# Connect to Milvus
connections.connect("default", host="localhost", port="19530")

# Define the schema for the collection
collection_name = "clipv2"
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=vector_dim)
]
schema = CollectionSchema(fields, collection_name)

# Create a collection
collection = Collection(collection_name, schema)

# # Process and insert data in batches
# batch_size = 1000  # Increased batch size for better performance while maintaining memory efficiency
# for start_idx in tqdm(range(0, total_vectors, batch_size), desc="Processing vectors"):
#     end_idx = min(start_idx + batch_size, total_vectors)
    
#     # Reconstruct only the current batch of vectors
#     batch_vectors = index.reconstruct_n(start_idx, end_idx - start_idx)
#     batch_ids = np.arange(start_idx, end_idx, dtype=np.int64)
    
#     # Prepare and insert the batch
#     data_batch = [
#         batch_ids.tolist(),
#         batch_vectors.tolist()
#     ]
#     collection.insert(data_batch)
    
#     # Force garbage collection after each batch (optional, uncomment if needed)
#     # import gc
#     # gc.collect()

# Create an index on the vector field
index_params = {
    "index_type": "IVF_FLAT",
    "metric_type": "COSINE",
    "params": {"nlist": 128}
}
collection.create_index("vector", index_params)

# Load the collection into memory
collection.load()

print("start search")
# Perform a basic search to verify
query_vectors = np.random.random([1, vector_dim]).tolist()
search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
results = collection.search(query_vectors, "vector", search_params, limit=3)

# Print the search results
for result in results:
    print(result)