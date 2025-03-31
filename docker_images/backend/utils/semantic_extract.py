import os
import glob
import torch
import json
import numpy as np
import sys
from typing import List
import torch.nn.functional as F
import faiss
from transformers import AutoTokenizer, AutoModel
import gc
from tqdm import tqdm
import io
from utils.helpers.gcp_storage_helper.gcp_storage import GCPStorageManager


class semantic_extract:
    """A class for extracting semantic information from text or images.

    This class provides methods for semantic analysis and feature extraction,
    typically used in the video search system to process and understand content
    semantically. It can be used to extract meaningful features and representations
    from input data for search and comparison purposes.
    """
    def __init__(
            self,
            model = 'sentence-transformers/stsb-xlm-r-multilingual',
            context_path = "dict/captions",
            context_vector_path = "data/TransNetDatabase/CaptionFeatures/context_vector.npy",
            input_datatype = 'txt',
            output_datatype = 'torch',
    ):
        # Get singleton instance of GCPStorageManager
        self.storage_manager = GCPStorageManager()
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = AutoModel.from_pretrained(model).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.context_path = context_path
        self.context_vector_path = context_vector_path
        
        if not self.storage_manager.blob_exists(context_vector_path):
            self.raw_data = self.generate_context_embedding(context_path, context_vector_path, output_datatype, input_datatype)
        else:
            self.raw_data = self.generate_raw_data(context_path, input_datatype)

    def get_embedding(
            self,
            inputs:List,
    ):
        encode_inputs = self.tokenizer(inputs, padding=True, truncation=True, return_tensors='pt', return_token_type_ids=True, return_attention_mask =True,)
        with torch.no_grad():
            model_output = self.model(
                input_ids = encode_inputs['input_ids'].to(self.device),
                attention_mask = encode_inputs['attention_mask'].to(self.device),
                token_type_ids = encode_inputs['token_type_ids'].to(self.device),
            )
            sentences_embed = self.mean_pooling(model_output, encode_inputs['attention_mask'].to(self.device))
            sentences_embed = F.normalize(sentences_embed, p=2, dim=1)
        gc.collect()
        torch.cuda.empty_cache()
        return sentences_embed
    
    @staticmethod
    def mean_pooling(model_output, attention_mask):
        token_embeddings = model_output[0] #First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    
    def generate_raw_data(
            self,
            context_path,
            type_input:str='txt',
    ):
        raw_data = []
        if type_input=='txt':
            # List files in GCP bucket with given prefix
            data_paths = self.storage_manager.list_files(context_path)
            data_paths.sort()
            for path in data_paths:
                if path.endswith('.txt'):
                    # Download and read text content from GCP
                    content = self.storage_manager.download_blob_to_bytes(path).decode('utf-8')
                    data = content.splitlines()
                    data = [word.strip() for word in data]
                    raw_data.extend(data)
        elif type_input=='json':
            # List files in GCP bucket with given prefix
            context_paths = self.storage_manager.list_files(context_path)
            context_paths.sort()
            for cxx_context_path in context_paths:
                # Get all .json files in this directory
                paths = [p for p in self.storage_manager.list_files(cxx_context_path) if p.endswith('.json')]
                paths.sort(reverse=False, key=lambda x: int(x[-8:-5]))
                for path in paths:
                    # Download and parse JSON from GCP
                    content = self.storage_manager.download_blob_to_bytes(path).decode('utf-8')
                    data = ["nan" if (x =='' or x==[]) else x for x in json.loads(content)]
                    raw_data += data
        else:
            print(f'not support reading {type_input}')
            sys.exit()
        return raw_data

    def generate_context_embedding(
            self,
            context_path,
            save_tensor_path,
            type_output:str,
            type_input:str='txt',
    ):
        raw_data = self.generate_raw_data(context_path, type_input)
        chunk_range = 100
        context_embedding = []
        print('running embedding: ')
        for i in tqdm(range(0, len(raw_data), chunk_range)):
            context_embedding.append(self.get_embedding(raw_data[i:i+chunk_range]))
        context_embedding = torch.cat(context_embedding)
        
        if type_output=='numpy':
            numpy_context_embedding = context_embedding.cpu().numpy()
            with io.BytesIO() as buffer:
                np.save(buffer, numpy_context_embedding)
                self.storage_manager.upload_from_string(save_tensor_path, buffer.getvalue())
        elif type_output=='torch':
            torch_context_embedding = context_embedding.cpu()
            with io.BytesIO() as buffer:
                torch.save(torch_context_embedding, buffer)
                self.storage_manager.upload_from_string(save_tensor_path, buffer.getvalue())
        elif type_output=='bin':
            index = faiss.IndexFlatL2(context_embedding.shape[-1])
            print('running save faiss: ')
            for vector in tqdm(context_embedding.cpu().numpy()):
                index.add(vector.reshape(1, -1))
            with io.BytesIO() as buffer:
                faiss.write_index(index, buffer)
                self.storage_manager.upload_from_string(save_tensor_path, buffer.getvalue())
        return raw_data