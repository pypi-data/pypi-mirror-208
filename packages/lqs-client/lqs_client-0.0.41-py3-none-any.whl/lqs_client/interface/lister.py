from typing import Optional
from datetime import datetime
from uuid import UUID

from .common import RESTInterface, ProcessStatus, UserRole, LogFormat, output_decorator


class Lister(RESTInterface):
    def __init__(self, config):
        super().__init__(config)

    @output_decorator
    def api_key(
        self,
        offset: Optional[int] = 0,
        limit: Optional[int] = 10,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        user_id: Optional[UUID] = None,
        key: Optional[str] = None,
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        args = locals()
        resource_path = f"apiKeys" + self._get_url_param_string(args, [])
        result = self._get_resource(resource_path)
        return result

    @output_decorator
    def extraction(
        self,
        offset: Optional[int] = 0,
        limit: Optional[int] = 10,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        log_id: Optional[UUID] = None,
        group_id: Optional[UUID] = None,
        status: Optional[ProcessStatus] = None,
        processing: Optional[bool] = None,
        queued: Optional[bool] = None,
        cancelled: Optional[bool] = None,
        errored: Optional[bool] = None,
        archived: Optional[bool] = None,
        completed: Optional[bool] = None,
        name: Optional[str] = None,
        name_like: Optional[str] = None,
        format: Optional[LogFormat] = None,
        s3_bucket: Optional[str] = None,
        s3_key: Optional[str] = None,
        s3_key_prefix: Optional[str] = None,
        size_null: Optional[bool] = None,
        size_gte: Optional[int] = None,
        size_lte: Optional[int] = None,
        progress_null: Optional[bool] = None,
        progress_gte: Optional[float] = None,
        progress_lte: Optional[float] = None,
        error_like: Optional[str] = None,
        note_like: Optional[str] = None,
        context_filter: Optional[dict] = None,
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        args = locals()
        resource_path = f"extractions" + self._get_url_param_string(args, [])
        result = self._get_resource(resource_path)
        return result

    @output_decorator
    def extraction_topic(
        self,
        extraction_id: UUID,
        offset: Optional[int] = 0,
        limit: Optional[int] = 10,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        topic_id: Optional[UUID] = None,
        start_time_null: Optional[bool] = None,
        start_time_gte: Optional[float] = None,
        start_time_lte: Optional[float] = None,
        end_time_null: Optional[bool] = None,
        end_time_gte: Optional[float] = None,
        end_time_lte: Optional[float] = None,
        size_null: Optional[bool] = None,
        size_gte: Optional[int] = None,
        size_lte: Optional[int] = None,
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        args = locals()
        resource_path = f"extractions/{extraction_id}" + self._get_url_param_string(
            args, ["extraction_id"]
        )
        result = self._get_resource(resource_path)
        return result

    @output_decorator
    def group(
        self,
        offset: Optional[int] = 0,
        limit: Optional[int] = 10,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        name: Optional[str] = None,
        name_like: Optional[str] = None,
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        args = locals()
        resource_path = f"groups" + self._get_url_param_string(args, [])
        result = self._get_resource(resource_path)
        return result

    @output_decorator
    def group_association(
        self,
        offset: Optional[int] = 0,
        limit: Optional[int] = 10,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        user_id: Optional[UUID] = None,
        group_id: Optional[UUID] = None,
        role: Optional[UserRole] = None,
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        args = locals()
        resource_path = f"groupAssociations" + self._get_url_param_string(args, [])
        result = self._get_resource(resource_path)
        return result

    @output_decorator
    def ingestion(
        self,
        offset: Optional[int] = 0,
        limit: Optional[int] = 10,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        log_id: Optional[UUID] = None,
        group_id: Optional[UUID] = None,
        status: Optional[ProcessStatus] = None,
        processing: Optional[bool] = None,
        queued: Optional[bool] = None,
        cancelled: Optional[bool] = None,
        errored: Optional[bool] = None,
        archived: Optional[bool] = None,
        completed: Optional[bool] = None,
        format: Optional[LogFormat] = None,
        name: Optional[str] = None,
        name_like: Optional[str] = None,
        s3_bucket: Optional[str] = None,
        s3_key: Optional[str] = None,
        s3_key_prefix: Optional[str] = None,
        size_null: Optional[bool] = None,
        size_gte: Optional[int] = None,
        size_lte: Optional[int] = None,
        progress_null: Optional[bool] = None,
        progress_gte: Optional[float] = None,
        progress_lte: Optional[float] = None,
        meta_like: Optional[str] = None,
        error_like: Optional[str] = None,
        note_like: Optional[str] = None,
        context_filter: Optional[dict] = None,
        start_offset_null: Optional[bool] = None,
        start_offset_gte: Optional[int] = None,
        start_offset_lte: Optional[int] = None,
        end_offset_null: Optional[bool] = None,
        end_offset_gte: Optional[int] = None,
        end_offset_lte: Optional[int] = None,
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        args = locals()
        resource_path = f"ingestions" + self._get_url_param_string(args, [])
        result = self._get_resource(resource_path)
        return result

    @output_decorator
    def log(
        self,
        offset: Optional[int] = 0,
        limit: Optional[int] = 10,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        group_id: Optional[UUID] = None,
        locked: Optional[bool] = None,
        start_time_null: Optional[bool] = None,
        start_time_gte: Optional[float] = None,
        start_time_lte: Optional[float] = None,
        end_time_null: Optional[bool] = None,
        end_time_gte: Optional[float] = None,
        end_time_lte: Optional[float] = None,
        name: Optional[str] = None,
        name_like: Optional[str] = None,
        note_like: Optional[str] = None,
        context_filter: Optional[dict] = None,
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        args = locals()
        resource_path = f"logs" + self._get_url_param_string(args, [])
        result = self._get_resource(resource_path)
        return result

    @output_decorator
    def message_type(
        self,
        offset: Optional[int] = 0,
        limit: Optional[int] = 10,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        group_id: Optional[UUID] = None,
        name: Optional[str] = None,
        name_like: Optional[str] = None,
        md5: Optional[str] = None,
        definition_like: Optional[str] = None,
        note_like: Optional[str] = None,
        context_filter: Optional[dict] = None,
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        args = locals()
        resource_path = f"messageTypes" + self._get_url_param_string(args, [])
        result = self._get_resource(resource_path)
        return result

    @output_decorator
    def record(
        self,
        topic_id: UUID,
        offset: Optional[int] = 0,
        limit: Optional[int] = 10,
        order: Optional[str] = "timestamp",
        sort: Optional[str] = "ASC",
        log_id: Optional[UUID] = None,
        ingestion_id: Optional[UUID] = None,
        errored: Optional[bool] = None,
        archived: Optional[bool] = None,
        data_filter: Optional[dict] = None,
        context_filter: Optional[dict] = None,
        frequency: Optional[float] = None,
        timestamp_gt: Optional[float] = None,
        timestamp_lt: Optional[float] = None,
        timestamp_gte: Optional[float] = None,
        timestamp_lte: Optional[float] = None,
        length_gte: Optional[int] = None,
        length_lte: Optional[int] = None,
        data_length_gte: Optional[int] = None,
        data_length_lte: Optional[int] = None,
        offset_gte: Optional[int] = None,
        offset_lte: Optional[int] = None,
        data_offset_gte: Optional[int] = None,
        data_offset_lte: Optional[int] = None,
        nanosecond_gte: Optional[int] = None,
        nanosecond_lte: Optional[int] = None,
        error_like: Optional[str] = None,
        note_like: Optional[str] = None,
        include_image: Optional[bool] = False,
        include_bytes: Optional[bool] = False,
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        args = locals()
        resource_path = f"topics/{topic_id}/records" + self._get_url_param_string(
            args, []
        )
        result = self._get_resource(resource_path)
        return result

    @output_decorator
    def topic(
        self,
        offset: Optional[int] = 0,
        limit: Optional[int] = 10,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        log_id: Optional[UUID] = None,
        group_id: Optional[UUID] = None,
        message_type_id: Optional[UUID] = None,
        associated_topic_id: Optional[UUID] = None,
        ingestion_id: Optional[UUID] = None,
        locked: Optional[bool] = None,
        name: Optional[str] = None,
        name_like: Optional[str] = None,
        context_filter: Optional[dict] = None,
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        args = locals()
        resource_path = f"topics" + self._get_url_param_string(args, [])
        result = self._get_resource(resource_path)
        return result

    @output_decorator
    def user(
        self,
        offset: Optional[int] = 0,
        limit: Optional[int] = 10,
        order: Optional[str] = "created_at",
        sort: Optional[str] = "ASC",
        username: Optional[str] = None,
        username_like: Optional[str] = None,
        is_admin: Optional[bool] = None,
        created_by: Optional[UUID] = None,
        updated_by: Optional[UUID] = None,
        deleted_by: Optional[UUID] = None,
        updated_by_null: Optional[bool] = None,
        deleted_by_null: Optional[bool] = None,
        updated_at_null: Optional[bool] = None,
        deleted_at_null: Optional[bool] = None,
        created_at_lte: Optional[datetime] = None,
        updated_at_lte: Optional[datetime] = None,
        deleted_at_lte: Optional[datetime] = None,
        created_at_gte: Optional[datetime] = None,
        updated_at_gte: Optional[datetime] = None,
        deleted_at_gte: Optional[datetime] = None,
    ):
        args = locals()
        resource_path = f"users" + self._get_url_param_string(args, [])
        result = self._get_resource(resource_path)
        return result

    # Plural methods
    def api_keys(self, **kwargs):
        return self.api_key(**kwargs)

    def extractions(self, **kwargs):
        return self.extraction(**kwargs)

    def extraction_topics(self, **kwargs):
        return self.extraction_topic(**kwargs)

    def groups(self, **kwargs):
        return self.group(**kwargs)

    def group_associations(self, **kwargs):
        return self.group_association(**kwargs)

    def ingestions(self, **kwargs):
        return self.ingestion(**kwargs)

    def logs(self, **kwargs):
        return self.log(**kwargs)

    def message_types(self, **kwargs):
        return self.message_type(**kwargs)

    def records(self, **kwargs):
        return self.record(**kwargs)

    def topics(self, **kwargs):
        return self.topic(**kwargs)

    def users(self, **kwargs):
        return self.user(**kwargs)
