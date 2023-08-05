from uuid import UUID
from typing import Optional

from .common import RESTInterface, UserRole, LogFormat, output_decorator


class Creator(RESTInterface):
    def __init__(self, config):
        super().__init__(config)

    @output_decorator
    def api_key(self, user_id: UUID, name: str):
        args = locals()
        data = self._get_payload_data(args, [])
        result = self._create_resource(f"apiKeys", data)
        return result

    @output_decorator
    def extraction(
        self, log_id: UUID, name: Optional[str] = None, note: Optional[str] = None
    ):
        args = locals()
        data = self._get_payload_data(args, [])
        result = self._create_resource(f"extractions", data)
        return result

    @output_decorator
    def extraction_presigned_url(self, extraction_id: UUID, method: str, params: dict):
        args = locals()
        data = self._get_payload_data(args, ["extraction_id"])
        result = self._create_resource(
            f"extractions/{extraction_id}/presignedUrls", data
        )
        return result

    @output_decorator
    def extraction_topic(
        self,
        extraction_id: UUID,
        topic_id: UUID,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        frequency: Optional[float] = None,
    ):
        args = locals()
        data = self._get_payload_data(args, ["extraction_id"])
        result = self._create_resource(f"extractions/{extraction_id}/topics", data)
        return result

    @output_decorator
    def group(self, name: str):
        args = locals()
        data = self._get_payload_data(args, [])
        result = self._create_resource(f"groups", data)
        return result

    @output_decorator
    def group_association(self, user_id: UUID, group_id: UUID, role: UserRole):
        args = locals()
        data = self._get_payload_data(args, [])
        result = self._create_resource(f"groupAssociations", data)
        return result

    @output_decorator
    def ingestion(
        self,
        log_id: UUID,
        format: LogFormat,
        s3_bucket: Optional[str] = None,
        s3_key: Optional[str] = None,
        name: Optional[str] = None,
        start_offset: Optional[int] = None,
        end_offset: Optional[int] = None,
        note: Optional[str] = None,
        queued: Optional[bool] = False,
    ):
        args = locals()
        data = self._get_payload_data(args, [])
        result = self._create_resource(f"ingestions", data)
        return result

    @output_decorator
    def ingestion_presigned_url(self, ingestion_id: UUID, method: str, params: dict):
        args = locals()
        data = self._get_payload_data(args, ["ingestion_id"])
        result = self._create_resource(f"ingestions/{ingestion_id}/presignedUrls", data)
        return result

    @output_decorator
    def log(self, group_id: UUID, name: str, note: Optional[str] = None):
        args = locals()
        data = self._get_payload_data(args, [])
        result = self._create_resource(f"logs", data)
        return result

    @output_decorator
    def log_presigned_url(self, log_id: UUID, method: str, params: dict):
        args = locals()
        data = self._get_payload_data(args, ["log_id"])
        result = self._create_resource(f"logs/{log_id}/presignedUrls", data)
        return result

    @output_decorator
    def message_type(
        self,
        group_id: UUID,
        name: str,
        definition: str,
        md5: Optional[str] = None,
        note: Optional[str] = None,
    ):
        args = locals()
        data = self._get_payload_data(args, [])
        result = self._create_resource(f"messageTypes", data)
        return result

    @output_decorator
    def record(
        self,
        timestamp: float,
        topic_id: UUID,
        offset: Optional[int] = None,
        length: Optional[int] = None,
        data_offset: Optional[int] = None,
        data_length: Optional[int] = None,
        errored: Optional[bool] = False,
        archived: Optional[bool] = False,
        error: Optional[dict] = None,
        note: Optional[str] = None,
        chunk_compression: Optional[str] = None,
        chunk_offset: Optional[int] = None,
        chunk_length: Optional[int] = None,
        s3_bucket: Optional[str] = None,
        s3_key: Optional[str] = None,
        format: Optional[LogFormat] = None,
        message_data: Optional[dict] = None,
        message_type_id: Optional[UUID] = None,
        ingestion_id: Optional[UUID] = None,
        payload_bytes: Optional[str] = None,
        payload_dict: Optional[dict] = None,
    ):
        args = locals()
        data = self._get_payload_data(args, ["topic_id"])
        result = self._create_resource(f"topics/{topic_id}/records", data)
        return result

    @output_decorator
    def record_presigned_url(
        self, timestamp: float, topic_id: UUID, method: str, params: dict
    ):
        args = locals()
        data = self._get_payload_data(args, ["timestamp", "topic_id"])
        result = self._create_resource(
            f"topics/{topic_id}/records/{timestamp}/presignedUrls", data
        )
        return result

    @output_decorator
    def topic(
        self,
        name: str,
        log_id: UUID,
        message_type_id: UUID = None,
        ingestion_id: UUID = None,
    ):
        args = locals()
        data = self._get_payload_data(args, [])
        result = self._create_resource(f"topics", data)
        return result

    @output_decorator
    def topic_presigned_url(self, topic_id: UUID, method: str, params: dict):
        args = locals()
        data = self._get_payload_data(args, ["topic_id"])
        result = self._create_resource(f"topics/{topic_id}/presignedUrls", data)
        return result

    @output_decorator
    def user(self, username: str, is_admin: Optional[bool] = False):
        args = locals()
        data = self._get_payload_data(args, [])
        result = self._create_resource(f"users", data)
        return result
