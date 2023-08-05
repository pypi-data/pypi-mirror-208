import os
import time
import logging
from uuid import UUID
from enum import Enum
from typing import Optional, Union, List

logging.basicConfig(
    level=os.getenv("LQS_LOG_LEVEL") or logging.INFO,
    format="%(asctime)s  (%(levelname)s - %(name)s): %(message)s",
)
logger = logging.getLogger(__name__)

import lz4.frame
import requests
import xmltodict
from urllib.parse import unquote

from .fs import FileSystemManager


class S3Method(str, Enum):
    abort_multipart_upload = "abort_multipart_upload"
    complete_multipart_upload = "complete_multipart_upload"
    create_multipart_upload = "create_multipart_upload"
    delete_object = "delete_object"
    get_object = "get_object"
    head_object = "head_object"
    list_multipart_uploads = "list_multipart_uploads"
    list_object_versions = "list_object_versions"
    list_objects_v2 = "list_objects_v2"
    list_parts = "list_parts"
    put_object = "put_object"
    restore_object = "restore_object"
    upload_part = "upload_part"


class S3Resource(str, Enum):
    extraction = "extraction"
    ingestion = "ingestion"
    log = "log"
    record = "record"
    topic = "topic"


class S3:
    def __init__(self, config, getter, creator):
        self._config = config
        self._getter = getter
        self._creator = creator

        self._retry_count = config["retry_count"]
        self._retry_delay = config["retry_delay"]
        self._retry_aggressive = config["retry_aggressive"]

        self.fs = FileSystemManager(config)

    def _handle_retries(self, func, retry_count=None):
        if retry_count is None:
            retry_count = self._retry_count
        for i in range(retry_count + 1):
            try:
                return func()
            except Exception as e:
                if not self._retry_aggressive:
                    lqs_expected_error_codes = [
                        "[BadRequest]",
                        "[Forbidden]",
                        "[NotFound]",
                        "[Conflict]",
                        "[Locked]",
                    ]
                    for code in lqs_expected_error_codes:
                        if code in str(e):
                            raise e
                if retry_count > 0 and i < retry_count:
                    # exponential backoff
                    backoff = self._retry_delay * (2**i)
                    logger.error(f"Error: {e}")
                    logger.info(f"Retrying in {backoff} seconds")
                    time.sleep(backoff)
                else:
                    raise e

    def generate_presigned_url(
        self,
        method: S3Method,
        resource: S3Resource,
        params: dict,
        resource_id: UUID = None,
        timestamp: Optional[float] = None,
    ):
        if resource == "extraction":
            presigned_url = self._creator.extraction_presigned_url(
                extraction_id=resource_id, method=method, params=params
            )
        elif resource == "ingestion":
            presigned_url = self._creator.ingestion_presigned_url(
                ingestion_id=resource_id, method=method, params=params
            )
        elif resource == "log":
            presigned_url = self._creator.log_presigned_url(
                log_id=resource_id, method=method, params=params
            )
        elif resource == "record":
            if timestamp is None:
                raise ValueError("timestamp is required.")
            presigned_url = self._creator.record_presigned_url(
                topic_id=resource_id, timestamp=timestamp, method=method, params=params
            )
        elif resource == "topic":
            presigned_url = self._creator.topic_presigned_url(
                topic_id=resource_id, method=method, params=params
            )
        else:
            raise ValueError(f"Unknown resource {resource}.")
        url = presigned_url["url"]
        used_params = presigned_url["params"]
        return url, used_params

    def abort_multi_part_upload(
        self,
        resource: S3Resource,
        resource_id: Union[str, dict],
        key: str,
        upload_id: str,
    ):
        if resource in ["record"]:
            if (
                isinstance(resource_id, str)
                or "topic_id" not in resource_id
                or "timestamp" not in resource_id
            ):
                raise ValueError(
                    "When resource is 'record', resource_id must be a dict with values 'topic_id' and 'timestamp'."
                )
            timestamp = resource_id["timestamp"]
            resource_id = resource_id["topic_id"]
        else:
            timestamp = None
        params = {
            "Key": key,
            "UploadId": upload_id,
        }

        def make_requests():
            url, used_params = self.generate_presigned_url(
                method="abort_multipart_upload",
                resource=resource,
                params=params,
                resource_id=resource_id,
                timestamp=timestamp,
            )

            r = requests.delete(url)
            return r.headers, used_params, None

        return self._handle_retries(make_requests)

    def complete_multipart_upload(
        self,
        resource: S3Resource,
        resource_id: Union[str, dict],
        key: str,
        upload_id: str,
        parts: List[dict],
        convert_to_dict: bool = True,
        decode_response: bool = True,
    ):
        if resource in ["record"]:
            if (
                isinstance(resource_id, str)
                or "topic_id" not in resource_id
                or "timestamp" not in resource_id
            ):
                raise ValueError(
                    "When resource is 'record', resource_id must be a dict with values 'topic_id' and 'timestamp'."
                )
            timestamp = resource_id["timestamp"]
            resource_id = resource_id["topic_id"]
        else:
            timestamp = None
        params = {
            "Key": key,
            "UploadId": upload_id,
        }

        complete_multipart_payload = "<CompleteMultipartUpload>"
        for part in parts:
            if "ETag" not in part or "PartNumber" not in part:
                raise ValueError("Part must contain 'ETag' and 'PartNumber'.")
            part["ETag"] = part["ETag"].strip('"')
            complete_multipart_payload += f"""
            <Part>
                <PartNumber>{part["PartNumber"]}</PartNumber>
                <ETag>{part["ETag"]}</ETag>
            </Part>
            """
        complete_multipart_payload += "</CompleteMultipartUpload>"

        def make_requests():
            url, used_params = self.generate_presigned_url(
                method="complete_multipart_upload",
                resource=resource,
                params=params,
                resource_id=resource_id,
                timestamp=timestamp,
            )
            r = requests.post(url, data=complete_multipart_payload)
            if decode_response:
                response_text = unquote(r.text)
            else:
                response_text = r.text
            response_content = (
                xmltodict.parse(response_text) if convert_to_dict else response_text
            )
            return r.headers, used_params, response_content

        return self._handle_retries(make_requests)

    def create_multipart_upload(
        self,
        resource: S3Resource,
        resource_id: Union[str, dict],
        key: str,
        convert_to_dict: bool = True,
        decode_response: bool = True,
    ):
        if resource in ["record"]:
            if (
                isinstance(resource_id, str)
                or "topic_id" not in resource_id
                or "timestamp" not in resource_id
            ):
                raise ValueError(
                    "When resource is 'record', resource_id must be a dict with values 'topic_id' and 'timestamp'."
                )
            timestamp = resource_id["timestamp"]
            resource_id = resource_id["topic_id"]
        else:
            timestamp = None
        params = {"Key": key}

        def make_requests():
            url, used_params = self.generate_presigned_url(
                method="create_multipart_upload",
                resource=resource,
                params=params,
                resource_id=resource_id,
                timestamp=timestamp,
            )
            r = requests.post(url)
            if decode_response:
                response_text = unquote(r.text)
            else:
                response_text = r.text
            response_content = (
                xmltodict.parse(response_text) if convert_to_dict else response_text
            )
            return r.headers, used_params, response_content

        return self._handle_retries(make_requests)

    def delete_object(
        self,
        resource: S3Resource,
        resource_id: Union[str, dict],
        key: str,
        version_id: Optional[str] = None,
    ):
        if resource in ["record"]:
            if (
                isinstance(resource_id, str)
                or "topic_id" not in resource_id
                or "timestamp" not in resource_id
            ):
                raise ValueError(
                    "When resource is 'record', resource_id must be a dict with values 'topic_id' and 'timestamp'."
                )
            timestamp = resource_id["timestamp"]
            resource_id = resource_id["topic_id"]
        else:
            timestamp = None
        params = {"Key": key}
        if version_id is not None:
            params["VersionId"] = version_id

        def make_requests():
            url, used_params = self.generate_presigned_url(
                method="delete_object",
                resource=resource,
                params=params,
                resource_id=resource_id,
                timestamp=timestamp,
            )
            r = requests.delete(url)
            return r.headers, used_params, None

        return self._handle_retries(make_requests)

    def get_object(
        self,
        resource: S3Resource,
        resource_id: Union[str, dict],
        key: str,
        part_number: Optional[int] = None,
    ):
        if resource in ["record"]:
            if (
                isinstance(resource_id, str)
                or "topic_id" not in resource_id
                or "timestamp" not in resource_id
            ):
                raise ValueError(
                    "When resource is 'record', resource_id must be a dict with values 'topic_id' and 'timestamp'."
                )
            timestamp = resource_id["timestamp"]
            resource_id = resource_id["topic_id"]
        else:
            timestamp = None
        params = {"Key": key}
        if part_number is not None:
            params["PartNumber"] = part_number

        def make_requests():
            url, used_params = self.generate_presigned_url(
                method="get_object",
                resource=resource,
                params=params,
                resource_id=resource_id,
                timestamp=timestamp,
            )
            r = requests.get(url)
            return r.headers, used_params, r.content

        return self._handle_retries(make_requests)

    def head_object(
        self,
        resource: S3Resource,
        resource_id: Union[str, dict],
        key: str,
        part_number: Optional[int] = None,
        version_id: Optional[str] = None,
    ):
        if resource in ["record"]:
            if (
                isinstance(resource_id, str)
                or "topic_id" not in resource_id
                or "timestamp" not in resource_id
            ):
                raise ValueError(
                    "When resource is 'record', resource_id must be a dict with values 'topic_id' and 'timestamp'."
                )
            timestamp = resource_id["timestamp"]
            resource_id = resource_id["topic_id"]
        else:
            timestamp = None
        params = {"Key": key}
        if part_number is not None:
            params["PartNumber"] = part_number
        if version_id is not None:
            params["VersionId"] = version_id

        def make_requests():
            url, used_params = self.generate_presigned_url(
                method="head_object",
                resource=resource,
                params=params,
                resource_id=resource_id,
                timestamp=timestamp,
            )
            r = requests.head(url)
            # TODO: may need to return a status code as well
            # for now, we'll just return it as the body
            return r.headers, used_params, {"exists": r.status_code == 200}

        return self._handle_retries(make_requests)

    def list_multipart_uploads(
        self,
        resource: S3Resource,
        resource_id: Union[str, dict],
        convert_to_dict: bool = True,
        decode_response: bool = True,
    ):
        if resource in ["record"]:
            if (
                isinstance(resource_id, str)
                or "topic_id" not in resource_id
                or "timestamp" not in resource_id
            ):
                raise ValueError(
                    "When resource is 'record', resource_id must be a dict with values 'topic_id' and 'timestamp'."
                )
            timestamp = resource_id["timestamp"]
            resource_id = resource_id["topic_id"]
        else:
            timestamp = None
        params = {}

        def make_requests():
            url, used_params = self.generate_presigned_url(
                method="list_multipart_uploads",
                resource=resource,
                params=params,
                resource_id=resource_id,
                timestamp=timestamp,
            )
            r = requests.get(url)
            if decode_response:
                response_text = unquote(r.text)
            else:
                response_text = r.text
            response_content = (
                xmltodict.parse(response_text) if convert_to_dict else response_text
            )
            return r.headers, used_params, response_content

        return self._handle_retries(make_requests)

    def list_object_versions(
        self,
        resource: S3Resource,
        resource_id: Union[str, dict],
        convert_to_dict: bool = True,
        decode_response: bool = True,
    ):
        if resource in ["record"]:
            if (
                isinstance(resource_id, str)
                or "topic_id" not in resource_id
                or "timestamp" not in resource_id
            ):
                raise ValueError(
                    "When resource is 'record', resource_id must be a dict with values 'topic_id' and 'timestamp'."
                )
            timestamp = resource_id["timestamp"]
            resource_id = resource_id["topic_id"]
        else:
            timestamp = None
        params = {}

        def make_requests():
            url, used_params = self.generate_presigned_url(
                method="list_object_versions",
                resource=resource,
                params=params,
                resource_id=resource_id,
                timestamp=timestamp,
            )
            r = requests.get(url)
            if decode_response:
                response_text = unquote(r.text)
            else:
                response_text = r.text
            response_content = (
                xmltodict.parse(response_text) if convert_to_dict else response_text
            )
            return r.headers, used_params, response_content

        return self._handle_retries(make_requests)

    def list_objects_v2(
        self,
        resource: S3Resource,
        resource_id: Union[str, dict],
        continuation_token: Optional[str] = None,
        convert_to_dict: bool = True,
        decode_response: bool = True,
    ):
        if resource in ["record"]:
            if (
                isinstance(resource_id, str)
                or "topic_id" not in resource_id
                or "timestamp" not in resource_id
            ):
                raise ValueError(
                    "When resource is 'record', resource_id must be a dict with values 'topic_id' and 'timestamp'."
                )
            timestamp = resource_id["timestamp"]
            resource_id = resource_id["topic_id"]
        else:
            timestamp = None
        params = {}
        if continuation_token is not None:
            params["ContinuationToken"] = continuation_token

        def make_requests():
            url, used_params = self.generate_presigned_url(
                method="list_objects_v2",
                resource=resource,
                params=params,
                resource_id=resource_id,
                timestamp=timestamp,
            )
            r = requests.get(url)
            if decode_response:
                response_text = unquote(r.text)
            else:
                response_text = r.text
            response_content = (
                xmltodict.parse(response_text) if convert_to_dict else response_text
            )
            return r.headers, used_params, response_content

        return self._handle_retries(make_requests)

    def list_parts(
        self,
        resource: S3Resource,
        resource_id: Union[str, dict],
        key: str,
        upload_id: str,
        part_number_marker: Optional[int] = None,
        convert_to_dict: bool = True,
        decode_response: bool = True,
    ):
        if resource in ["record"]:
            if (
                isinstance(resource_id, str)
                or "topic_id" not in resource_id
                or "timestamp" not in resource_id
            ):
                raise ValueError(
                    "When resource is 'record', resource_id must be a dict with values 'topic_id' and 'timestamp'."
                )
            timestamp = resource_id["timestamp"]
            resource_id = resource_id["topic_id"]
        else:
            timestamp = None
        params = {"Key": key, "UploadId": upload_id}
        if part_number_marker is not None:
            params["PartNumberMarker"] = part_number_marker

        def make_requests():
            url, used_params = self.generate_presigned_url(
                method="list_parts",
                resource=resource,
                params=params,
                resource_id=resource_id,
                timestamp=timestamp,
            )
            r = requests.get(url)
            if decode_response:
                response_text = unquote(r.text)
            else:
                response_text = r.text
            response_content = (
                xmltodict.parse(response_text) if convert_to_dict else response_text
            )
            return r.headers, used_params, response_content

        return self._handle_retries(make_requests)

    def put_object(
        self, resource: S3Resource, resource_id: Union[str, dict], key: str, body: bytes
    ):
        if resource in ["record"]:
            if (
                isinstance(resource_id, str)
                or "topic_id" not in resource_id
                or "timestamp" not in resource_id
            ):
                raise ValueError(
                    "When resource is 'record', resource_id must be a dict with values 'topic_id' and 'timestamp'."
                )
            timestamp = resource_id["timestamp"]
            resource_id = resource_id["topic_id"]
        else:
            timestamp = None
        params = {"Key": key}

        def make_requests():
            url, used_params = self.generate_presigned_url(
                method="put_object",
                resource=resource,
                params=params,
                resource_id=resource_id,
                timestamp=timestamp,
            )
            r = requests.put(url, data=body)
            return r.headers, used_params, None

        return self._handle_retries(make_requests)

    def restore_object(self):
        raise NotImplementedError("Restore object is not implemented yet.")

    def upload_part(
        self,
        resource: S3Resource,
        resource_id: Union[str, dict],
        key: str,
        body: bytes,
        part_number: int,
        upload_id: str,
    ):
        if resource in ["record"]:
            if (
                isinstance(resource_id, str)
                or "topic_id" not in resource_id
                or "timestamp" not in resource_id
            ):
                raise ValueError(
                    "When resource is 'record', resource_id must be a dict with values 'topic_id' and 'timestamp'."
                )
            timestamp = resource_id["timestamp"]
            resource_id = resource_id["topic_id"]
        else:
            timestamp = None
        params = {"Key": key, "PartNumber": part_number, "UploadId": upload_id}

        def make_requests():
            url, used_params = self.generate_presigned_url(
                method="upload_part",
                resource=resource,
                params=params,
                resource_id=resource_id,
                timestamp=timestamp,
            )
            r = requests.put(url, data=body)
            return r.headers, used_params, None

        return self._handle_retries(make_requests)

    def get_message_data_from_record(
        self, record, s3_bucket=None, s3_key=None, ingestion_id=None
    ):
        if s3_bucket is None or s3_key is None:
            s3_bucket = record["s3_bucket"]
            s3_key = record["s3_key"]
            if s3_bucket is None or s3_key is None:
                ingestion_id = record["ingestion_id"]
                if ingestion_id is None:
                    raise ValueError("Missing ingestion_id and s3_bucket/s3_key")
                ingestion = self._getter.ingestion(ingestion_id=ingestion_id)["data"]
                s3_bucket = ingestion["s3_bucket"]
                s3_key = ingestion["s3_key"]

        chunk_compression = record["chunk_compression"]
        data_offset = record["data_offset"]
        data_length = record["data_length"]
        if chunk_compression != "none" and chunk_compression is not None:
            chunk_offset = record["chunk_offset"]
            chunk_length = record["chunk_length"]

            chunk_data = self.fs.get_data(
                s3_bucket=s3_bucket,
                s3_key=s3_key,
                start_offset=chunk_offset,
                end_offset=chunk_offset + chunk_length,
            )

            if chunk_compression == "lz4":
                message_data = lz4.frame.decompress(chunk_data)

            message_data = chunk_data[data_offset : data_offset + data_length]
        else:
            message_data = self.fs.get_data(
                s3_bucket=s3_bucket,
                s3_key=s3_key,
                start_offset=data_offset,
                end_offset=data_offset + data_length,
            )
        return message_data
