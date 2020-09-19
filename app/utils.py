from urllib.parse import urlparse, urljoin
from flask import request
from app import ALLOWED_EXTENSIONS


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


# def hash_file(file_stream):
#     BLOCK_SIZE = 65536
#     file_hash = hashlib.sha256()
#     fb = file_stream.read(BLOCK_SIZE)
#     while len(fb) > 0:
#         file_hash.update(fb)
#         fb = file_stream.read(BLOCK_SIZE)
#     return file_hash.hexdigest()


def get_extension_if_valid(filename):
    extension = filename.rsplit('.', 1)[1].lower()
    if '.' in filename and extension in ALLOWED_EXTENSIONS:
        return extension
