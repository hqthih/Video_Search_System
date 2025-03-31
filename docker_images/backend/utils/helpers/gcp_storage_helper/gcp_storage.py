import json
import os
from google.cloud import storage
from typing import Dict, Any, Optional

class GCPStorageManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialize_storage()
        return cls._instance
    
    def initialize_storage(self):
        """Initialize storage with bucket name from environment variable"""
        self.bucket_name = os.getenv('GCP_BUCKET_NAME', 'video-search-keyframes-storage-hao')
        self.client = storage.Client()
        self.bucket = self.client.bucket(self.bucket_name)
    
    def load_json_file(self, json_path: str) -> Dict[int, Any]:
        """Load JSON file from GCP Storage.
        
        Args:
            json_path (str): Path to the JSON file in the bucket
            
        Returns:
            Dict[str, Any]: Loaded JSON data
        """
        js = self.load_json_with_cache(json_path)
        return {int(k):v for k,v in js.items()}

    def load_json(self, blob_path: str) -> Dict[str, Any]:
        """Load JSON file from GCP Storage.
        
        Args:
            blob_path (str): Path to the JSON file in the bucket
            
        Returns:
            Dict[str, Any]: Loaded JSON data
        """
        blob = self.bucket.blob(blob_path)
        content = blob.download_as_string()
        return json.loads(content)
    
    def load_json_with_cache(self, blob_path: str, cache_dir: str = "/tmp") -> Dict[str, Any]:
        """Load JSON file from GCP Storage with local caching.
        
        Args:
            blob_path (str): Path to the JSON file in the bucket
            cache_dir (str): Directory to store cached files
            
        Returns:
            Dict[str, Any]: Loaded JSON data
        """
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        # Generate cache file path
        cache_file = os.path.join(cache_dir, os.path.basename(blob_path))
        
        # Check if file exists in cache
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        # Download and cache the file
        data = self.load_json(blob_path)
        with open(cache_file, 'w') as f:
            json.dump(data, f)
            
        return data
    
    def list_files(self, prefix: str) -> list:
        """List files in a bucket with given prefix.
        
        Args:
            prefix (str): Prefix to filter files
            
        Returns:
            list: List of file names
        """
        blobs = self.bucket.list_blobs(prefix=prefix)
        return [blob.name for blob in blobs]
    
    def get_file_size(self, blob_path: str) -> int:
        """Get file size from GCP Storage.
        
        Args:
            blob_path (str): Path to the file in the bucket
            
        Returns:
            int: File size in bytes. Returns 0 if the blob doesn't exist or size is None.
        """
        blob = self.bucket.blob(blob_path)
        blob.reload()
        size = blob.size
        return size if size is not None else 0

    def download_blob_to_bytes(self, blob_path: str) -> bytes:
        """Download a blob's contents as bytes.

        Args:
            blob_path: Path to the blob in the bucket

        Returns:
            The blob's contents as bytes
        """
        blob = self.bucket.blob(blob_path)
        return blob.download_as_bytes()

    def blob_exists(self, blob_path: str) -> bool:
        """Check if a blob exists in the bucket."""
        blob = self.bucket.blob(blob_path)
        return blob.exists()

    def upload_from_string(self, blob_path: str, data: str):
        """Upload data from a string to a blob."""
        blob = self.bucket.blob(blob_path)
        blob.upload_from_string(data)

# Global storage manager instance
storage_manager = GCPStorageManager() 