# -*- coding: utf-8 -*-

from mimetypes import guess_extension
from urlparse import urljoin

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client


class COS(object):
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        secret_id = app.config['COS_SECRET_ID']
        secret_key = app.config['COS_SECRET_KEY']
        region = app.config['COS_REGION']
        token = None # 使用临时密钥需要传入 Token，默认为空，可不填
        scheme = 'https' # 指定使用 http/https 协议来访问 COS，默认为 https，可不填
        self.host = app.config['COS_HOST']
        self.bucket = app.config['COS_BUCKET']

        config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
		# 2. 获取客户端对象
        self.client = CosS3Client(config)

    def upload_file(self, file, cos_path, bucket=None):
        """
        """
        if not bucket:
            bucket = self.bucket

        response = self.client.upload_file(
                    Bucket=bucket,
                    LocalFilePath=file,
                    Key=cos_path,
                    PartSize=1,
                    MAXThread=1)

        return response

    def get_url(self, key):
        return urljoin(self.host, key)
