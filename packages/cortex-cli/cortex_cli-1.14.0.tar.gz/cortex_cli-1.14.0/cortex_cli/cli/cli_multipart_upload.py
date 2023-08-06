import os
import math
import requests

class MultipartUpload():
    UPLOAD_THRESHOLD = (1024 * 1024) * 8
    UPLOAD_PART_SIZE = (1024 * 1024) * 128

    def __init__(self, path: str, endpoint: str, headers: dict):
        self._file_path = path
        self._file_size = os.path.getsize(path)
        self._file_parts = math.ceil(self._file_size / self.UPLOAD_PART_SIZE)
        
        self._endpoint = endpoint
        self._headers  = headers
        
    @property
    def file_path(self) -> str:
        return self._file_path

    @property
    def file_size(self) -> int:
        return self._file_path

    @property
    def file_parts(self) -> int:
        return self._file_parts

    def upload(self):
        upload_id = self._upload_multipart_init()
        parts     = self._upload_multipart_parts(upload_id.text)
        self._upload_multipart_complete(upload_id.text, parts)

    def _upload_multipart_init(self):
        '''
        Begin the multi-part upload process.
        
        This returns an upload ID that is used to identify the upload. All
        subsequent actions will use this upload ID.
        '''
        return requests.post(
            url = f'{self._endpoint}/create',
            headers = self._headers,
            json = {
                'key': self._file_path
            }
        )

    def _upload_multipart_parts(self, upload_id):
        '''
        Upload the file, piece by piece.
        
        Uploads the file in pieces, dictated by the UPLOAD_PART_SIZE constant.
        Each part requests a signed URL, uploads the part, and then returns the
        hash/etag of the part.
        '''
        parts = []
        with open(self._file_path, 'rb') as file:
            print(f'Uploading {self._file_path}')
            
            while True:
                # read() will just read up to EOF - once it's out of data, it
                # will return an empty string
                data = file.read(self.UPLOAD_PART_SIZE)
                if not data:
                    return parts

                # We need to get a signed URL for each and every part
                response = requests.post(
                    url =  f'{self._endpoint}/url',
                    headers = self._headers,
                    json = {
                        'key': file.name,
                        'uploadId': upload_id,
                        'partNumber': len(parts) + 1
                    }
                )

                # Actually upload the part
                upload_response = requests.put(
                    url = response.text,
                    data = data
                )

                # The response from the upload will contain the hash/etag of the
                # part - this is used to complete the upload
                parts.append(
                    {
                        'PartNumber': len(parts) + 1, 
                        'ETag': upload_response.headers['ETag']
                    }
                )


    def _upload_multipart_complete(self, upload_id, parts):
        '''
        Signal that the upload is complete.
        '''
        requests.post(
            url =  f'{self._endpoint}/complete',
            headers = self._headers,
            json = {
                'key': self._file_path,
                'uploadId': upload_id,
                'parts': parts
            }
        )
