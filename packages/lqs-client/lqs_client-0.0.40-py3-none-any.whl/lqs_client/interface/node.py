import os
import time
import logging
import threading

import requests
import rospy

logging.basicConfig(
    level=os.getenv("LQS_LOG_LEVEL") or logging.INFO,
    format="%(asctime)s  (%(levelname)s - %(name)s): %(message)s",
)
logger = logging.getLogger(__name__)

# http://wiki.ros.org/ROS/Tutorials/WritingPublisherSubscriber%28python%29


class Node:
    def __init__(self, getter, lister, utils, config):
        self._get = getter
        self._list = lister
        self._utils = utils
        self._config = config

        self._log = None
        self._start_time = None
        self._end_time = None

        self._publishers = {}
        self._subscriptions = {}
        self._remaps = {}

        if self._config.get("aws_access_key_id"):
            self._use_s3_directly = True
        else:
            self._use_s3_directly = False
        self._kill_threads = False

        if self._config.get("verbose"):
            logger.setLevel(logging.DEBUG)

    def subscribe(self, log_id, topic_names, rel_start_time, rel_end_time, remaps={}):
        rospy.init_node("lqs_client", anonymous=True)

        self._log = self._get.log(log_id=log_id)["data"]

        self._start_time = self._log["start_time"] + rel_start_time
        self._end_time = self._log["start_time"] + rel_end_time

        topics_all = self._list.topics(log_id=log_id, limit=100)["data"]
        self._remaps = remaps
        self._subscriptions = {}
        for topic in topics_all:
            if topic["name"] in topic_names:
                message_class = self._utils.get_message_class(topic["message_type_id"])
                self._publishers[topic["name"]] = rospy.Publisher(
                    remaps.get(topic["name"], topic["name"]),
                    message_class,
                    queue_size=10,
                )
                thread = threading.Thread(
                    target=self.load_records, args=(topic["name"],)
                )
                thread.start()
                self._subscriptions[topic["name"]] = {
                    "topic": topic,
                    "thread": thread,
                    "loading_data": True,  # assume there is data to start
                    "records": [],
                }

    def fetch_record_bytes(self, topic_name, record):
        record["fetching_bytes"] = True
        record["bytes"] = None
        start_time = time.time()
        if self._use_s3_directly:
            mode = "direct"
            record["bytes"] = self._utils.get_message_data_from_record(record)
        else:
            mode = "presgined"
            record["bytes"] = requests.get(record["bytes_url"]).content
        end_time = time.time()
        logger.debug(
            f"({mode}) fetched bytes for {topic_name} ({record['timestamp']}) in {end_time - start_time}"
        )

    def load_records(self, topic_name):
        limit = 100 if self._use_s3_directly else 10
        offset = 0
        while True:
            if topic_name not in self._subscriptions:
                continue
            sub = self._subscriptions[topic_name]
            records = sub["records"]
            topic = sub["topic"]
            records_response = self._list.records(
                log_id=self._log["id"],
                topic_id=topic["id"],
                timestamp_gte=self._start_time,
                timestamp_lt=self._end_time,
                limit=limit,
                offset=offset,
                include_bytes=False if self._use_s3_directly else True,
            )
            records = records_response["data"]
            logger.debug(f"Loaded {len(records)} records for {topic_name}")
            if len(records) == 0:
                break
            offset += limit
            sub["records"] += records
            if self._kill_threads:
                break
        self._subscriptions[topic_name]["loading_data"] = False
        logger.debug(f"Done loading records for {topic_name}.")

    def publish(self, topic_name):
        sub = self._subscriptions[topic_name]
        topic = sub["topic"]
        records = sub["records"]
        if len(records) == 0:
            logger.debug(f"No records for {topic_name}")
            return

        record = records.pop(0)
        if "fetching_bytes" not in record:
            self.fetch_record_bytes(topic_name, record)

        while record["bytes"] is None:
            time.sleep(0.01)

        if len(records) > 0:
            next_record = records[0]
            if "fetching_bytes" not in next_record:
                threading.Thread(
                    target=self.fetch_record_bytes, args=(topic_name, next_record)
                ).start()

        message = self._utils.get_ros_message_from_message_data(
            message_data=record["bytes"],
            message_type_id=topic["message_type_id"],
        )
        publisher = self._publishers[topic_name]
        publisher.publish(message)

    def publish_next_message(self):
        # look through our records and publish the next message based on timestamp
        next_message_time = None
        next_message_topic = None
        still_loading = False
        for topic_name in self._subscriptions:
            sub = self._subscriptions[topic_name]
            if sub["loading_data"]:
                still_loading = True
            if len(sub["records"]) == 0:
                if still_loading:
                    # no records, but we're still loading data, so we restart the loop
                    return True
                continue
            next_record = sub["records"][0]
            if (
                next_message_time is None
                or next_record["timestamp"] < next_message_time
            ):
                # this topic may have the next message to publish
                next_message_time = next_record["timestamp"]
                next_message_topic = topic_name

        if next_message_topic is not None:
            self.publish(next_message_topic)
            return True
        elif still_loading:
            return True
        else:
            return False

    def play(self, rate=None, use_s3_directly=None):
        if use_s3_directly is not None:
            self._use_s3_directly = use_s3_directly

        if self._use_s3_directly:
            logger.info("Using S3 directly to fetch data.")
        else:
            logger.info("Using presigned URLs to fetch data.")

        if rate is not None:
            logger.warn("rate is now deprecated.")

        while not rospy.is_shutdown():
            try:
                continue_publishing = self.publish_next_message()
                if not continue_publishing:
                    logger.info("No more messages to publish.")
                    break
            except KeyboardInterrupt:
                self._kill_threads = True
                break
