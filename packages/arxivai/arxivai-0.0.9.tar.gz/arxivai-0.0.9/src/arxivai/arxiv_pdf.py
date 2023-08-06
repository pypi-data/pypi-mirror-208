import os

import fitz
from google.cloud import storage
from regex import P



def download(arxiv_id)->str:
    """
    Downloads a public blob from the bucket.
    __________
    bucket_name = "your-bucket-name"
    blob_name = "storage-object-name"
    file_name = "local/path/to/file"
    """
    file_name = f"dataset/pdf/{arxiv_id}.pdf"
    if not os.path.exists(file_name):
        bucket_name = "arxiv-dataset"
        blob_name = f"arxiv/arxiv/pdf/{arxiv_id.split('.')[0]}/{arxiv_id}.pdf"

        storage_client = storage.Client.create_anonymous_client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.download_to_filename(file_name)

    return file_name


def fulltext(file_name)-> str:
    with fitz.open(file_name) as doc: # type: ignore
        fulltext = ''
        for page in doc:
            text = page.get_text().encode("utf-8") # get plain text (is in UTF-8)
            fulltext += text.decode("utf-8")
    return fulltext


def subtitle(file_name):
    subtitles = []
    with fitz.open(file_name) as doc: # type: ignore
        toc = doc.get_toc(simple=False)
        for entry in toc:
            subtitles.append(entry[1])
    
    return subtitles


def delete(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)



if __name__ == '__main__':
    # file_name = download('2303.08774v3')
    file_name = download('2106.12423v4')
    subtitles = subtitle(file_name)
    text = fulltext(file_name)
    print(subtitles)
    print('------------------')
    print(text)
    delete(file_name)
