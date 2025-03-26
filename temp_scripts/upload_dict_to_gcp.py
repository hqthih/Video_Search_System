import os
import argparse
from google.cloud import storage
from tqdm import tqdm

def upload_directory_to_gcp(local_dir: str, bucket_name: str, prefix: str = ""):
    """Upload a directory to GCP Storage.
    
    Args:
        local_dir (str): Local directory path
        bucket_name (str): GCP Storage bucket name
        prefix (str): Prefix for the files in the bucket
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    # Get all files in the directory
    for root, _, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)
            # Calculate relative path from local_dir
            relative_path = os.path.relpath(local_path, local_dir)
            # Create blob path with prefix
            blob_path = os.path.join(prefix, relative_path).replace("\\", "/")
            
            # Upload file
            blob = bucket.blob(blob_path)
            print(f"Uploading {local_path} to {blob_path}")
            blob.upload_from_filename(local_path)

def main():
    parser = argparse.ArgumentParser(description="Upload dict files to GCP Storage")
    parser.add_argument("--bucket", required=True, help="GCP Storage bucket name")
    parser.add_argument("--dict-dir", default="../dict", help="Local dict directory path")
    parser.add_argument("--prefix", default="dict", help="Prefix for files in the bucket")
    
    args = parser.parse_args()
    
    # Upload dict directory
    upload_directory_to_gcp(args.dict_dir, args.bucket, args.prefix)
    print("Upload completed successfully!")

if __name__ == "__main__":
    main() 