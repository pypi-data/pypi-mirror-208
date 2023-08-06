from google.cloud import storage


def download(arxiv_id)->str:
    """
    Downloads a public blob from the bucket.
    __________
    bucket_name = "your-bucket-name"
    blob_name = "storage-object-name"
    file_name = "local/path/to/file"
    """
    bucket_name = "arxiv-dataset"
    blob_name = f"arxiv/arxiv/pdf/{arxiv_id.split('.')[0]}/{arxiv_id}.pdf"
    file_name = f"temp/{arxiv_id}.pdf"

    storage_client = storage.Client.create_anonymous_client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(file_name)

    return file_name
