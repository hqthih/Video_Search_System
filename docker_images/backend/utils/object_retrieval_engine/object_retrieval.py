import os
import sys
import glob
import scipy
import pickle
import numpy as np
import json
import re
import io
from sklearn.feature_extraction.text import TfidfVectorizer
from utils.helpers.gcp_storage_helper.gcp_storage import GCPStorageManager
from utils.combine_utils import merge_searching_results_by_addition


class load_file:
    """A class for loading and preprocessing text data and creating TF-IDF matrices.
    
    This class handles:
    1. Loading text data from different sources (txt or json files)
    2. Creating and saving TF-IDF vectorizers for different data types
    3. Transforming text data into sparse matrices for efficient similarity search
    
    Attributes:
        clean_data_path: Path to the cleaned data files
        save_tfids_object_path: Path to save TF-IDF transformers and matrices
        update: Boolean flag for updating existing transformers
        all_datatpye: List of data types to process (bbox, class, color, tag, number)
        context_data: Optional pre-loaded context data
        ngram_range: Range of n-grams to use in TF-IDF
        input_datatype: Type of input files ('txt' or 'json')
    """
    def __init__(
            self,
            clean_data_path,  # clean_data_path and context can't not be None at the same time
            save_tfids_object_path,
            update:bool,
            all_datatpye,
            context_data = None,
            ngram_range = (1, 1),
            input_datatype = 'txt',
    ):
        # Get singleton instance of GCPStorageManager
        self.storage_manager = GCPStorageManager()
        
        # Initialize dictionaries to store TF-IDF transformers and context matrices for each data type
        tfidf_transform = {}
        context_matrix = {}
        for data_type in all_datatpye:
            # Check if TF-IDF transformer exists in GCP Storage
            if not self.storage_manager.blob_exists(os.path.join(save_tfids_object_path, f'tfidf_transform_{data_type}.pkl')):
                if context_data is None:
                    # Load context data from files if not provided directly
                    clean_data_paths =  clean_data_path[data_type]
                    context = self.load_context(clean_data_paths, input_datatype)
                    print(data_type)
                    print(context[0][:100])
                else:
                    context = context_data
                # Create and fit TF-IDF vectorizer for this data type
                tfidf_transform[data_type] = TfidfVectorizer(input = 'content', ngram_range = ngram_range, token_pattern=r"(?u)\b[\w\d]+\b")
                context_matrix[data_type] = tfidf_transform[data_type].fit_transform(context).tocsr()
                print(tfidf_transform[data_type].get_feature_names_out()[:10])
                print(context_matrix[data_type].shape)

                # Save to GCP Storage instead of local files
                # Save TF-IDF transformer
                with io.BytesIO() as buffer:
                    pickle.dump(tfidf_transform[data_type], buffer)
                    self.storage_manager.upload_from_string(
                        os.path.join(save_tfids_object_path, f'tfidf_transform_{data_type}.pkl'),
                        buffer.getvalue()
                    )

                # Save sparse matrix
                with io.BytesIO() as buffer:
                    scipy.sparse.save_npz(buffer, context_matrix[data_type])
                    self.storage_manager.upload_from_string(
                        os.path.join(save_tfids_object_path, f'sparse_context_matrix_{data_type}.npz'),
                        buffer.getvalue()
                    )

    def load_context(self, clean_data_paths, input_datatype):
        # Load and preprocess text data from GCP Storage
        context = []
        if input_datatype == 'txt':
            # Handle text files
            data_paths = []
            # List files in GCP bucket with given prefix
            cxx_data_paths = self.storage_manager.list_files(clean_data_paths)
            cxx_data_paths.sort()
            for cxx_data_path in cxx_data_paths:
                # Get all .txt files in this directory
                data_path = [p for p in self.storage_manager.list_files(cxx_data_path) if p.endswith('.txt')]
                data_path.sort(reverse=False, key=lambda s:int(s[-7:-4]))
                data_paths += data_path
            for path in data_paths:
                # Download and read text content from GCP
                content = self.storage_manager.download_blob_to_bytes(path).decode('utf-8')
                data = content.splitlines()
                data = [item.strip() for item in data]
                context += data
        elif input_datatype == 'json':
            # Handle JSON files
            context_paths = self.storage_manager.list_files(clean_data_paths)
            context_paths.sort()
            for cxx_context_path in context_paths:
                # Get all .json files in this directory
                paths = [p for p in self.storage_manager.list_files(cxx_context_path) if p.endswith('.json')]
                paths.sort(reverse=False, key=lambda x: int(x[-8:-5]))
                for path in paths:
                    # Download and parse JSON from GCP
                    content = self.storage_manager.download_blob_to_bytes(path).decode('utf-8')
                    json_data = json.loads(content)
                    context += [self.preprocess_text(' '.join(line)) for line in json_data]
        else:
            print(f'not support reading the {input_datatype}')
            sys.exit()
        return context
    
    @staticmethod
    def preprocess_text(text:str):
        # Preprocess text by lowercasing and removing special characters
        text = text.lower()
        # keep letter and number remove all remain
        reg_pattern = '[^a-z0-9A-Z_ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễếệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ\s]'
        output = re.sub(reg_pattern, '', text)
        output = output.strip()
        return output

class object_retrieval(load_file):
    """A class for retrieving similar objects based on text queries using TF-IDF similarity.
    
    This class provides:
    1. Text-based search functionality for different object attributes
    2. Similarity scoring using TF-IDF and cosine similarity
    3. Support for multiple data types (bbox, class, color, tag, number)
    4. Filtered search using pre-defined indices
    
    Key methods:
    - transform_input: Converts user query to TF-IDF vector
    - find_similar_score: Finds similar items using cosine similarity
    - __call__: Main search method combining results from different data types
    """
    def __init__(
            self,
            clean_data_path={
                'bbox': 'dict/context_encoded/bboxes_encoded/*',
                'class': 'dict/context_encoded/classes_encoded/*',
                'color': 'dict/context_encoded/colors_encoded/*',
                'tag': 'dict/context_encoded/tags_encoded/*',
                'number': 'dict/context_encoded/number_encoded/*',
            },
            update:bool=False,
            save_tfids_object_path = 'dict/bin/contexts_bin',  # Path in GCP Storage
            save_corpus_path = 'dict/tag/tag_corpus.txt'
    ):
        # Get list of data types that have valid paths
        all_datatpye = [key for key in clean_data_path.keys() if clean_data_path[key] is not None]
        super().__init__(
            clean_data_path=clean_data_path,
            save_tfids_object_path=save_tfids_object_path,
            update=update,
            all_datatpye=all_datatpye,
        )
        # Load saved TF-IDF transformers and context matrices from GCP Storage
        self.tfidf_transform = {}
        self.context_matrix = {}
        for data_type in all_datatpye:
            # Load TF-IDF transformer
            bytes_data = self.storage_manager.download_blob_to_bytes(
                os.path.join(save_tfids_object_path, f'tfidf_transform_{data_type}.pkl')
            )
            self.tfidf_transform[data_type] = pickle.loads(bytes_data)

            # Load sparse matrix
            matrix_data = self.storage_manager.download_blob_to_bytes(
                os.path.join(save_tfids_object_path, f'sparse_context_matrix_{data_type}.npz')
            )
            with io.BytesIO(matrix_data) as buffer:
                self.context_matrix[data_type] = scipy.sparse.load_npz(buffer)

        self.clean_data_path = clean_data_path
        # Get vocabulary from tag transformer
        self.tag_corpus = self.tfidf_transform['tag'].get_feature_names_out()
        if not self.storage_manager.blob_exists(save_corpus_path):
            corpus = [' '.join(words.split('_')) for words in self.tag_corpus]
            corpus = '\n'.join(corpus) + '\n'
            self.storage_manager.upload_from_string(save_corpus_path, corpus)

    def transform_input(
            self,
            input_query:str,
            transform_type:str,
    ):
        '''
        This function transform input take from user to tf-idf array
        It remove all word not in the vocabulary/corpus
        
        input:
        input: a string text used as query take from user
        
        output:
        numpy array converted from query with tf-idf
        '''
        # Transform input query using appropriate TF-IDF transformer
        if transform_type in ['bbox', 'class', 'color', 'tag', 'number']:
            vectorize = self.tfidf_transform[transform_type].transform([input_query])
        else:
            print('this type does not support')
            sys.exit()
        return vectorize
    
    def __call__(
            self,
            texts,
            k=100,
            index=None,
    ):
        # Process each data type and combine results
        scores, idx_image = [], []
        for input_type in ['bbox', 'color', 'class', 'tag', 'number']:
            if texts[input_type] is not None:
                scores_, idx_image_ = self.find_similar_score(texts[input_type], input_type, k, index=index)
                scores.append(scores_)
                idx_image.append(idx_image_)
        
        # Merge results from different data types
        scores, idx_image = merge_searching_results_by_addition(scores, idx_image)
        return scores, idx_image

    def find_similar_score(
            self,
            text:str,
            transform_type:str,
            k:int,
            index,
    ):
        # Transform input query to TF-IDF vector
        vectorize = self.transform_input(text, transform_type)
        if index is None: #awesome_cossim_topn(a, b, N, 0.01, use_threads=True, n_jobs=4, return_best_ntop=True)
            # Calculate similarity scores with all items
            scores = vectorize.dot(self.context_matrix[transform_type].T).toarray()[0]
            sort_index = np.argsort(scores)[::-1][:k]
            scores = scores[sort_index]
        else:
            # Calculate similarity scores with subset of items
            scores = vectorize.dot(self.context_matrix[transform_type][index,:].T).toarray()[0]
            sort_index = np.argsort(scores)[::-1][:k]
            scores = scores[sort_index]
            sort_index = np.array(index)[sort_index]
        return scores, sort_index

if __name__ == '__main__':
    inputs = {
        'bbox': "a0kite b0kite",
        'class': "people1 tv1",
        'color':None,
        'tag':None,
        'number':None,
    }
    obj = object_retrieval()
    #list_answer = obj(inputs, k=3)
    #print(list_answer)
    # obj.transform_input('query', 'input_type') # input_type is bbox, color, class, tag
    # context_vector = obj.get_context_vector() # get context vector
    pass