import io
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor


import boto3
import botocore

logger = logging.getLogger(__name__)


class FileSystemManager:
    """Methods for interacting with files."""

    def __init__(self, config):
        self.config = config

        self.aws_endpoint_url = self.config.get("aws_endpoint_url")
        self.replacement_host = None

        self.client_config = botocore.config.Config(
            max_pool_connections=100,
            signature_version=self.config.get("LQS_SIG_VER", "s3v4"),
        )

        self.store_session = True
        self.session = None
        self.clients = {}
        self.resources = {}

    # S3 Methods

    def set_store_session(self, value):
        self.store_session = value

    def get_boto_session(self):
        if self.session is not None:
            return self.session
        session = boto3.session.Session(
            aws_access_key_id=self.config.get("aws_access_key_id"),
            aws_secret_access_key=self.config.get("aws_secret_access_key"),
            region_name=self.config.get("aws_region"),
            aws_session_token=self.config.get("aws_session_token"),
        )
        if self.store_session:
            self.session = session
        return session

    def get_boto_client(self, service_name, session=None, replacement_host=None):
        if replacement_host is None:
            if service_name in self.clients:
                return self.clients[service_name]
        else:
            if f"{service_name}:{replacement_host}" in self.clients:
                return self.clients[f"{service_name}:{replacement_host}"]

        if session is None:
            session = self.get_boto_session()
        endpoint_url = self.aws_endpoint_url
        if replacement_host is not None:
            endpoint_url = replacement_host
        client = session.client(
            service_name=service_name,
            endpoint_url=endpoint_url,
            config=self.client_config,
        )

        if self.store_session:
            if replacement_host is None:
                self.clients[service_name] = client
            else:
                self.clients[f"{service_name}:{replacement_host}"] = client
        return client

    def get_boto_resource(self, service_name, session=None):
        if service_name in self.resources:
            return self.resources[service_name]
        if session is None:
            session = self.get_boto_session()
        resource = session.resource(
            service_name=service_name,
            endpoint_url=self.aws_endpoint_url,
            config=self.client_config,
        )
        if self.store_session:
            self.resources[service_name] = resource
        return resource

    def prepare_s3_key(self, s3_key):
        if not s3_key.startswith(self.key_prefix or ""):
            s3_key = self.key_prefix + s3_key
        return s3_key

    def get_data(self, s3_bucket, s3_key, start_offset=None, end_offset=None):
        s3_resource = self.get_boto_resource("s3")
        s3_object = s3_resource.Object(bucket_name=s3_bucket, key=s3_key)
        if start_offset is not None and end_offset is not None:
            range_header = f"bytes={start_offset}-{end_offset}"
            return s3_object.get(Range=range_header)["Body"].read()
        else:
            return s3_object.get()["Body"].read()

    def download_file(self, s3_bucket, s3_key, filepath):
        s3_client = self.get_boto_client("s3")
        download_dir = "/".join(filepath.split("/")[:-1])
        Path(download_dir).mkdir(parents=True, exist_ok=True)
        response = s3_client.download_file(s3_bucket, s3_key, filepath)
        logger.debug(response)
        return response

    def put_data(self, data, s3_bucket, s3_key, tags=None):
        s3_client = self.get_boto_client("s3")
        params = dict(Body=data, Bucket=s3_bucket, Key=s3_key)
        if tags is not None and self.enable_tagging:
            tagging = "&".join([f"{k}={v}" for k, v in tags.items()])
            params["Tagging"] = tagging
        response = s3_client.put_object(**params)
        logger.debug(response)
        return response

    def upload_file(self, filepath, s3_bucket, s3_key):
        s3_client = self.get_boto_client("s3")
        response = s3_client.upload_file(filepath, s3_bucket, s3_key)
        logger.debug(response)
        return response

    def upload_fileobj(self, data, s3_bucket, s3_key):
        s3_client = self.get_boto_client("s3")
        response = s3_client.upload_fileobj(data, s3_bucket, s3_key)
        logger.debug(response)
        return response

    def head_data(self, s3_bucket, s3_key, fail_on_404=False):
        try:
            s3_client = self.get_boto_client("s3")
            response = s3_client.head_object(Bucket=s3_bucket, Key=s3_key)
            logger.debug(response)
            return response
        except botocore.exceptions.ClientError as e:
            if not fail_on_404 and e.response["Error"]["Code"] == "404":
                return None
            else:
                raise e

    def list_data(self, s3_bucket, s3_prefix):
        s3_client = self.get_boto_client("s3")
        response = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=s3_prefix)
        logger.debug(response)
        return response

    def delete_data(self, s3_bucket, s3_key):
        s3_client = self.get_boto_client("s3")
        response = s3_client.delete_object(Bucket=s3_bucket, Key=s3_key)
        logger.debug(response)
        return response

    def get_object_size(self, s3_bucket, s3_key):
        s3_resource = self.get_boto_resource("s3")
        s3_object = s3_resource.Object(bucket_name=s3_bucket, key=s3_key)
        return s3_object.content_length

    def create_bucket(self, bucket_name):
        s3_resource = self.get_boto_resource("s3")
        return s3_resource.create_bucket(Bucket=bucket_name)

    def generate_presigned_url(self, params, client_method="get_object"):
        s3_client = self.get_boto_client("s3", replacement_host=self.replacement_host)
        url = s3_client.generate_presigned_url(
            ClientMethod=client_method, Params=params, ExpiresIn=self.url_expiration
        )
        if self.replacement_host is not None:
            url = url.replace(self.aws_endpoint_url, self.replacement_host)
        logger.debug(f"presigned url: {url[:10]}...{url[-5:]}")
        return url

    def get_object_chunk(
        self, barray, s3_object, range_header, data_offset, chunk_size
    ):
        response = s3_object.get(Range=range_header)
        barray[data_offset : data_offset + chunk_size] = response["Body"].read()

    def get_object_body(self, s3_bucket, s3_key, offset=0, size=-1):
        s3_resource = self.get_boto_resource("s3")
        s3_object = s3_resource.Object(bucket_name=s3_bucket, key=s3_key)

        offset = int(offset)
        size = int(size)
        if size < 2e9:
            # if it's small enough, just download it directly
            if size > 0:
                data = bytearray(size)
            else:
                data = bytearray(s3_object.content_length - offset)
            range_header = f"bytes={offset}-"
            if size > 0:
                range_end = str(offset + int(size - 1))
                range_header += range_end
            response = s3_object.get(Range=range_header)
            data[:] = response["Body"].read()
        else:
            data = bytearray(size)
            data_offset = 0
            download_size = int(1.28e8)  # 128 MB
            max_workers = 4
            # download_size = int(1e9) # 1 GB
            chunk_count = int(size // download_size)
            chunk_offset = offset
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                for chunk_idx in range(chunk_count + 1):
                    chunk_size = int(
                        min(download_size, size - (chunk_idx * download_size))
                    )
                    range_header = (
                        f"bytes={chunk_offset}-"
                        f"{str(chunk_offset + int(chunk_size - 1))}"
                    )
                    if int(chunk_size - 1) < 1:
                        logger.warn(f"Skipping last byte: {range_header}")
                        continue
                    logger.info(
                        (
                            f"Downloading Chunk {chunk_idx}/{chunk_count}: "
                            f"{range_header}"
                        )
                    )
                    chunk_offset += chunk_size
                    executor.submit(
                        self.get_object_chunk,
                        data,
                        s3_object,
                        range_header,
                        data_offset,
                        chunk_size,
                    )
                    data_offset += chunk_size
        return data

    def create_presigned_url(self, method, params):
        return {
            "method": method,
            "params": params,
            "url": self.generate_presigned_url(params=params, client_method=method),
        }
