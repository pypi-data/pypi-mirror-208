from uuid import UUID

from .common import RESTInterface, output_decorator


class Getter(RESTInterface):
    def __init__(self, config):
        super().__init__(config)

    @output_decorator
    def api_key(self, api_key_id: UUID):
        result = self._get_resource(f"apiKeys/{api_key_id}")
        return result

    @output_decorator
    def extraction(self, extraction_id: UUID):
        result = self._get_resource(f"extractions/{extraction_id}")
        return result

    @output_decorator
    def extraction_topic(self, extraction_id: UUID, extraction_topic_id: UUID):
        result = self._get_resource(
            f"extractions/{extraction_id}/topics/{extraction_topic_id}"
        )
        return result

    @output_decorator
    def group(self, group_id: UUID):
        result = self._get_resource(f"groups/{group_id}")
        return result

    @output_decorator
    def group_association(self, group_association_id: UUID):
        result = self._get_resource(f"groupAssociations/{group_association_id}")
        return result

    @output_decorator
    def ingestion(self, ingestion_id: UUID):
        result = self._get_resource(f"ingestions/{ingestion_id}")
        return result

    @output_decorator
    def log(self, log_id: UUID):
        result = self._get_resource(f"logs/{log_id}")
        return result

    @output_decorator
    def message_type(self, message_type_id: UUID):
        result = self._get_resource(f"messageTypes/{message_type_id}")
        return result

    @output_decorator
    def record(self, timestamp: float, topic_id: UUID):
        result = self._get_resource(f"topics/{topic_id}/records/{timestamp}")
        return result

    @output_decorator
    def topic(self, topic_id: UUID):
        result = self._get_resource(f"topics/{topic_id}")
        return result

    @output_decorator
    def user(self, user_id: UUID):
        result = self._get_resource(f"users/{user_id}")
        return result
