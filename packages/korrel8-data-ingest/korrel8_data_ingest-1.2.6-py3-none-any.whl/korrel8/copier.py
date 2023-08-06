import boto3
import os
import time

class Copier(object):
    s3 = None
    file_type = None

    def factory(file_type):
        if file_type == 'csv':
            return CsvCopier()
        elif file_type == 'json':
            return JsonCopier()
    
    def copy(self, from_bucket, path, target_bucket):
        self.s3 = boto3.resource('s3')
        copy_source = {
            'Bucket': from_bucket,
            'Key': path
        }
        key = '{}/{}/{}.{}'.format(self.file_type, 'demo_data', str(int(time.time())) + '_file', self.file_type)
        self.s3.Bucket(target_bucket).copy(copy_source, key)

    def set_file_type(self, file_type):
        self.file_type = file_type

    def get_file_extension(self, filename):
        return os.path.splitext(filename)[-1][1:]

    def print(self):
        print('Copier')

class CsvCopier(Copier):
    def __init__(self):
        self.file_type = 'csv'
        super().__init__()

    def print(self):
        print('CsvCopier')

class JsonCopier(Copier):
    def __init__(self):
       self.file_type = 'json'
       super().__init__()

    def print(self):
        print('JsonCopier')