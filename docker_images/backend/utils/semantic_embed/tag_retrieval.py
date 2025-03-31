import os
import faiss
import io
import numpy as np
import tempfile
from ..semantic_extract import semantic_extract
from utils.helpers.gcp_storage_helper.gcp_storage import GCPStorageManager


class tag_retrieval(semantic_extract):
    def __init__(
            self,
            model = 'sentence-transformers/stsb-xlm-r-multilingual',
            context_path = "dict/tag/tag_corpus.txt",
            context_vector_path = "dict/bin/tag_bin/tag_embedding.bin",
            input_datatype='txt',
            output_datatype = 'bin',
    ):
        # Get singleton instance of GCPStorageManager
        self.storage_manager = GCPStorageManager()

        super().__init__(
            model,
            context_path,
            context_vector_path,
            input_datatype,
            output_datatype,
        )

        # Download index bytes from GCP Storage
        index_bytes = self.storage_manager.download_blob_to_bytes(context_vector_path)
        
        # Create a temporary file to load the index
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(index_bytes)
            temp_file_path = temp_file.name
        
        try:
            # Load the index from the temporary file
            self.index = faiss.read_index(temp_file_path)
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    def __call__(
            self,
            query:str,
            k:int=3,
    ):
        query_embed = self.get_embedding([query]).to('cpu').numpy()
        _, index = self.index.search(query_embed, k)
        result = [self.raw_data[idx] for idx in index[0]]
        return result

if __name__ == '__main__':
    obj = tag_retrieval()
    print(obj("một người đàn ông đang đi bộ trên cầu", 3))
    pass