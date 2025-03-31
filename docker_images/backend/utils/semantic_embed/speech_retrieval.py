import os
import faiss
import pickle
import numpy as np
import scipy
import io
from ..semantic_extract import semantic_extract
from ..object_retrieval_engine.object_retrieval import load_file
from ..combine_utils import merge_searching_results_by_addition
from utils.common import PROJECT_ROOT
from utils.helpers.gcp_storage_helper.gcp_storage import GCPStorageManager


class speech_retrieval(semantic_extract, load_file):
    def __init__(
            self,
            model = 'sentence-transformers/stsb-xlm-r-multilingual',
            context_path = "dict/audio",
            context_vector_path = "dict/bin/audio_bin",
            input_datatype = 'json',
            output_datatype = 'bin',
            test_mode = False, # Enable to load raw data for debugging mode
            enable_semantic = False,
    ):
        # Get singleton instance of GCPStorageManager
        self.storage_manager = GCPStorageManager()

        self.enable_semantic = enable_semantic
        if enable_semantic:
            semantic_extract.__init__(
                self,
                model=model,
                context_path=context_path,
                context_vector_path=os.path.join(context_vector_path, 'embed_audio.bin'),
                input_datatype=input_datatype,
                output_datatype=output_datatype,
            )
            # Load index from GCP Storage
            index_bytes = self.storage_manager.download_blob_to_bytes(os.path.join(context_vector_path, 'embed_audio.bin'))
            self.index = faiss.read_index(io.BytesIO(index_bytes))
        elif (not self.storage_manager.blob_exists(os.path.join(context_vector_path, f'tfidf_transform_speech.pkl'))) or test_mode:
            self.raw_data = semantic_extract.generate_raw_data(context_path, input_datatype)
        else:
            self.raw_data = None
        
        load_file.__init__(
            self,
            clean_data_path=None,  # clean_data_path and context can't not be None at the same time
            save_tfids_object_path=context_vector_path,
            update=False,
            all_datatpye=['speech'],
            context_data = self.raw_data,
            ngram_range = (1, 3),
            input_datatype = 'json',
        )
        
        # Load TF-IDF transformer from GCP Storage
        tfidf_bytes = self.storage_manager.download_blob_to_bytes(os.path.join(context_vector_path, 'tfidf_transform_speech.pkl'))
        self.tfidf_transform = pickle.loads(tfidf_bytes)
        
        # Load sparse matrix from GCP Storage
        sparse_matrix_bytes = self.storage_manager.download_blob_to_bytes(os.path.join(context_vector_path, f'sparse_context_matrix_speech.npz'))
        self.context_matrix = scipy.sparse.load_npz(io.BytesIO(sparse_matrix_bytes))

    def __call__(
            self,
            query:str,
            k:int=3,
            index=None,
            semantic:bool=True,
            keyword:bool=True,
    ):
        merge_scores = []
        merge_idx_image = []
        
        if semantic and self.enable_semantic:
            scores, idx_image = self.caculate_semantic(query, k, index)
            scores = scores.flatten()
            idx_image = idx_image.flatten() 
            merge_scores.append(scores)
            merge_idx_image.append(idx_image)
        
        if keyword:
            scores, idx_image = self.caculate_sparse(query, k, index)
            merge_scores.append(scores)
            merge_idx_image.append(idx_image)

        if semantic and keyword and self.enable_semantic:
            scores, idx_image = merge_searching_results_by_addition(merge_scores, merge_idx_image)
        
        return scores, idx_image
    
    def caculate_semantic(
            self,
            query:str,
            k:int=3,
            index=None,
    ):
        query_embed = self.get_embedding([query]).to('cpu').numpy()
        if index==None:
            scores, sorted_index = self.index.search(query_embed, k)
        else:
            id_selector = faiss.IDSelectorArray(index)
            scores, sorted_index = self.index.search(query_embed, k, params=faiss.SearchParametersIVF(sel=id_selector))
        return scores, sorted_index

    def caculate_sparse(
            self,
            query:str,
            k:int,
            index=None,
    ):
        vectorize = self.tfidf_transform.transform([query])
        if index is None: 
            scores = vectorize.dot(self.context_matrix.T).toarray()[0]
            sort_index = np.argsort(scores)[::-1][:k]
            scores = scores[sort_index]
        else:
            scores = vectorize.dot(self.context_matrix[index,:].T).toarray()[0]
            sort_index = np.argsort(scores)[::-1][:k]
            scores = scores[sort_index]
            sort_index = np.array(index)[sort_index]
        return scores, sort_index


if __name__ == '__main__':
    obj = speech_retrieval()
    print(obj("một người đàn ông đang đi bộ trên cầu", 3))
    pass