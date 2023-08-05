from typing import Optional
from urllib.parse import urlparse

import boto3

from datamorphairflow.datamorph_constants import DEFAULT_AWS_REGION
from datamorphairflow.helper_classes import S3url


class S3FileSystem:
    def __init__(
            self,
            context: dict,
            region_name: Optional[str] = DEFAULT_AWS_REGION,
            aws_access_key_id: Optional[str] = None,
            aws_secret_access_key: Optional[str] = None,
            aws_session_token: Optional[str] = None,
    ) -> None:
        self.context = context
        self.s3client = boto3.client("s3",
                                     region_name=region_name,
                                     aws_secret_access_key=aws_secret_access_key,
                                     aws_access_key_id=aws_access_key_id,
                                     aws_session_token=aws_session_token)
        self.s3resource = boto3.resource("s3",
                                         region_name=region_name,
                                         aws_secret_access_key=aws_secret_access_key,
                                         aws_access_key_id=aws_access_key_id,
                                         aws_session_token=aws_session_token)
        self.s3session = boto3.session


    def urlparse(self,s3url:str) -> S3url:
        s3urlparse = urlparse(s3url, allow_fragments=False)
        parsedURL = S3url(s3urlparse.netloc, s3urlparse.path.lstrip('/'))
        return parsedURL


    def copyFromS3ToLocal(self, sourcePath:str, destPath:str):
        s3path: S3url = self.urlparse(sourcePath)
        self.s3client.download_file(s3path.bucket,s3path.key,destPath)

    def copyFromS3ToTempLocal(self, sourcePath:str):
        s3path: S3url = self.urlparse(sourcePath)
        dag_id = self.context['dag'].dag_id
        task_id = self.context['task'].task_id
        # creating a temp location for the file using dag id and task id
        dest_path = "/tmp/" + dag_id + '_' + task_id + '_' + sourcePath.rsplit('/', 1)[1]

        self.s3client.download_file(s3path.bucket,s3path.key,dest_path)
        return dest_path

    def copyFromS3ToS3(self,sourcePath:str, destPath:str):
        return True




