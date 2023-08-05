from uuid import UUID

from .common import RESTInterface, output_decorator


class Deleter(RESTInterface):
    def __init__(self, config):
        super().__init__(config)

    @output_decorator
    def api_key(self, api_key_id: UUID):
        self._delete_resource(f"apiKeys/{api_key_id}")
        return

    @output_decorator
    def extraction(self, extraction_id: UUID):
        self._delete_resource(f"extractions/{extraction_id}")
        return

    @output_decorator
    def extraction_topic(self, extraction_id: UUID, extraction_topic_id: UUID):
        self._delete_resource(
            f"extractions/{extraction_id}/topics/{extraction_topic_id}"
        )
        return

    @output_decorator
    def group(self, group_id: UUID):
        self._delete_resource(f"groups/{group_id}")
        return

    @output_decorator
    def group_association(self, group_association_id: UUID):
        self._delete_resource(f"groupAssociations/{group_association_id}")
        return

    @output_decorator
    def ingestion(self, ingestion_id: UUID):
        self._delete_resource(f"ingestions/{ingestion_id}")
        return

    @output_decorator
    def log(self, log_id: UUID):
        self._delete_resource(f"logs/{log_id}")
        return

    @output_decorator
    def message_type(self, message_type_id: UUID):
        self._delete_resource(f"messageTypes/{message_type_id}")
        return

    @output_decorator
    def record(self, timestamp: float, topic_id: UUID):
        self._delete_resource(f"topics/{topic_id}/records/{timestamp}")
        return

    @output_decorator
    def topic(self, topic_id: UUID):
        self._delete_resource(f"topics/{topic_id}")
        return

    @output_decorator
    def user(self, user_id: UUID):
        self._delete_resource(f"users/{user_id}")
        return
