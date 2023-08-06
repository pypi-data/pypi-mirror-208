import boto3
import os
import time

class Uploader(object):
    s3 = None
    file_type = None

    def factory(file_type):
        if file_type == 'csv':
            return CsvUploader()
        elif file_type == 'json':
            return JsonUploader()
    
    def upload(self, bucket, path):
        self.s3 = boto3.resource('s3')
        data = open(path, 'rb')
        key = '{}/{}/{}.{}'.format(self.file_type, 'demo_data', str(int(time.time())) + '_file', self.file_type)
        self.s3.Bucket(bucket).put_object(Key=key, Body=data)

    def set_file_type(self, file_type):
        self.file_type = file_type

    def get_file_extension(self, filename):
        return os.path.splitext(filename)[-1][1:]

    def print(self):
        print('Uploader')

class CsvUploader(Uploader):
    def __init__(self):
        self.file_type = 'csv'
        super().__init__()

    def print(self):
        print('CsvUploader')

class JsonUploader(Uploader):
    def __init__(self):
       self.file_type = 'json'
       super().__init__()

    def print(self):
        print('JsonUploader')