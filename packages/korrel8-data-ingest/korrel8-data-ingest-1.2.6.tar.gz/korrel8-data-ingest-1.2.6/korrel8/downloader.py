import boto3
import os

class Downloader(object):
    s3 = None
    file_type = None

    def factory(file_type):
        if file_type == 'csv':
            return CsvDownloader()
        elif file_type == 'json':
            return JsonDownloader()
    
    def download(self, bucket, prefix):
        self.s3 = boto3.resource('s3')
        self.s3.Object(bucket, prefix).download_file(prefix.split('/')[-1])

    def set_file_type(self, file_type):
        self.file_type = file_type

    def get_file_extension(self, filename):
        return os.path.splitext(filename)[-1][1:]

    def print(self):
        print('Downloader')

class CsvDownloader(Downloader):
    def __init__(self):
        self.file_type = 'csv'
        super().__init__()

    def print(self):
        print('CsvDownloader')

class JsonDownloader(Downloader):
    def __init__(self):
       self.file_type = 'json'
       super().__init__()

    def print(self):
        print('JsonDownloader')