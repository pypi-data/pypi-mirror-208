import os
import time
import datetime
import threading
import logging
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(
    level=os.getenv("LQS_LOG_LEVEL") or logging.INFO,
    format="%(asctime)s  (%(levelname)s - %(name)s): %(message)s",
)
logger = logging.getLogger(__name__)

from tqdm import tqdm

sshkeyboard_installed = False
try:
    from sshkeyboard import listen_keyboard, stop_listening

    sshkeyboard_installed = True
except ImportError:

    def listen_keyboard(*args, **kwargs):
        pass

    def stop_listening(*args, **kwargs):
        pass


colorama_installed = False
try:
    from colorama import Fore, Style, init

    init(autoreset=True)
    colorama_installed = True
except ImportError:

    class Dummy:
        def __getattr__(self, name):
            return ""

    Fore = Dummy()
    Style = Dummy()


class Terminal:
    def __init__(self, getter, lister, config):
        self._get = getter
        self._list = lister
        self._config = config

        verbose = self._config.get("verbose", False)
        if verbose:
            logger.setLevel(logging.DEBUG)

    def _format_spdlog_data(self, record, single_line=False, output_file=None):
        data = record["message_data"]
        timestamp = datetime.datetime.fromtimestamp(data["time"] / 1e9).strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )[:-3]
        level = {
            1: "trace",
            2: "debug",
            3: "info",
            4: "warn",
            5: "error",
            6: "critical",
            7: "off",
        }.get(data["level"], "unknown")
        level_colors = {
            "trace": Fore.WHITE,
            "debug": Fore.CYAN,
            "info": Fore.GREEN,
            "warn": Fore.YELLOW,
            "error": Fore.RED,
            "critical": Fore.RED + Style.BRIGHT,
            "unknown": Fore.MAGENTA,
        }
        thread_id = data["thread_id"]
        logger_name = data["logger_name"] if data["logger_name"] else "root"
        payload = data["payload"]
        if payload and single_line:
            payload = payload.replace("\n", "")

        if output_file:
            output_file.write(
                f"{timestamp} [{level}] [{thread_id}] [{logger_name}] {payload}\n"
            )
        else:
            print(
                f"{timestamp} [{level_colors[level]}{level}{Style.RESET_ALL}] [{thread_id}] [{logger_name}] {payload}"
            )

    def play(
        self,
        log_id=None,
        log_name=None,
        topic_id=None,
        topic_name=None,
        data_filter=None,
        max_dt=0.1,
        min_dt=0.01,
        sleep=True,
        single_line=True,
        paused=False,
        offset=0,
        start_timestamp=None,
        end_timestamp=None,
        start_datetime=None,
        end_datetime=None,
        keyboard_input=True,
        output_filepath=None,
        limit=100,
    ):
        if not sshkeyboard_installed:
            print("Install sshkeyboard for keyboard input")
        if not colorama_installed:
            print("Install colorama for colored output")

        if log_name:
            log_id = self._list.logs(name=log_name)["data"][0]["id"]
        elif log_id:
            log_name = self._get.log(log_id=log_id)["data"]["name"]
        else:
            raise Exception("Must provide log_id or log_name")

        if topic_name:
            topic_id = self._list.topics(log_id=log_id, name=topic_name)["data"][0][
                "id"
            ]
        elif topic_id:
            topic_name = self._get.topic(topic_id=topic_id)["data"]["name"]
        else:
            raise Exception("Must provide topic_id or topic_name")

        if data_filter is not None:
            if data_filter == "default":
                data_filter = {"var": "payload", "op": "ilike", "val": "%%"}

        if start_datetime:
            start_timestamp = datetime.datetime.fromisoformat(
                start_datetime
            ).timestamp()
        if end_datetime:
            end_timestamp = datetime.datetime.fromisoformat(end_datetime).timestamp()

        output_file = None
        if output_filepath:
            # create and append to file
            output_file = open(output_filepath, "a+")

        logger.info(f"Log: {log_name} ({log_id})")
        logger.info(f"Topic: {topic_name} ({topic_id})")
        if start_timestamp:
            logger.info(f"Start timestamp: {start_timestamp}")
        if end_timestamp:
            logger.info(f"End timestamp: {end_timestamp}")
        if data_filter:
            logger.info(f"Data filter: {data_filter}")
        if output_filepath:
            logger.info(f"Output file: {output_filepath}")

        self.offset = offset
        self.limit = limit

        # Controls

        self.paused = paused
        self.next = False
        self.prev = False
        self.exit_loop = False

        if output_file is None and keyboard_input:

            async def handle_pause(key):
                if key == "space":
                    self.paused = not self.paused
                if key == "q":
                    self.exit_loop = True
                if key == "s" or key == "up" or key == "left":
                    self.prev = True
                if key == "d" or key == "down" or key == "right":
                    self.next = True

            threading.Thread(
                target=listen_keyboard,
                kwargs=dict(on_press=handle_pause, delay_second_char=0.1),
            ).start()

            logger.info(
                "Press space to pause/resume, q to quit, up/left to go back, down/right to go forward"
            )

        # Record Accumulator
        self.buffer_index = 0
        self.record_buffer = []
        resp = self._list.records(
            log_id=log_id,
            topic_id=topic_id,
            offset=0,
            limit=0,
            data_filter=data_filter,
            timestamp_gte=start_timestamp,
            timestamp_lte=end_timestamp,
        )
        total_count = resp["count"]

        def load_record_buffer(buffer_size=3):
            while True and not self.exit_loop:
                buffer_len = len(self.record_buffer)
                if (
                    buffer_len >= buffer_size * self.limit
                    and self.buffer_index > buffer_len - self.limit
                ):
                    self.record_buffer = self.record_buffer[self.limit :]
                    self.buffer_index -= self.limit
                    buffer_len = len(self.record_buffer)
                if buffer_len < buffer_size * self.limit:
                    resp = self._list.records(
                        log_id=log_id,
                        topic_id=topic_id,
                        offset=self.offset,
                        limit=self.limit,
                        data_filter=data_filter,
                        timestamp_gte=start_timestamp,
                        timestamp_lte=end_timestamp,
                    )
                    records = resp["data"]
                    percent_complete = round(self.offset / total_count * 100, 2)
                    if len(records) == 0:
                        records = [{"end": True}]
                    self.record_buffer += records
                    if records[-1].get("end"):
                        break
                    self.offset += self.limit
                    logger.debug(
                        f"Loaded {self.offset} of {total_count} records ({percent_complete}%)"
                    )
            return

        thread = threading.Thread(target=load_record_buffer)
        thread.start()

        # Main Loop
        previous_timestamp = None
        logger.info("Loading initial data...")
        load_loops = 0
        wrote_count = 0
        try:
            while True and not self.exit_loop:
                if len(self.record_buffer) == 0:
                    time.sleep(1)
                    load_loops += 1
                    if load_loops == 30:
                        logger.error(
                            "Still loading data this long indicates an error.  Retry."
                        )
                    continue

                if not self.paused or self.next:
                    self.next = False
                    self.buffer_index += 1
                    if self.buffer_index >= len(self.record_buffer):
                        self.buffer_index = len(self.record_buffer) - 1
                    if self.buffer_index < 0 or self.buffer_index >= len(
                        self.record_buffer
                    ):
                        continue
                    record = self.record_buffer[self.buffer_index]
                    if record.get("end"):
                        logger.info("End of data")
                        self.exit_loop = True
                        break

                    timestamp = record["timestamp"]
                    if timestamp == previous_timestamp:
                        continue
                    self._format_spdlog_data(
                        record, single_line=single_line, output_file=output_file
                    )
                    wrote_count += 1
                    # log percent complete every 1% of total count
                    if wrote_count % (total_count // 100) == 0:
                        percent_complete = round(wrote_count / total_count * 100, 2)
                        logger.debug(
                            f"Wrote {wrote_count} of {total_count} records ({percent_complete}%)"
                        )
                    # print(datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
                    if output_file is None and not self.paused and sleep:
                        if previous_timestamp:
                            dt = timestamp - previous_timestamp
                            if max_dt and dt > max_dt:
                                time.sleep(max_dt)
                            elif min_dt and dt < min_dt:
                                time.sleep(min_dt)
                            else:
                                time.sleep(dt)
                    previous_timestamp = timestamp

                if self.prev:
                    self.prev = False
                    self.buffer_index -= 1
                    if self.buffer_index < 0:
                        self.buffer_index = 0
                    record = self.record_buffer[self.buffer_index]
                    timestamp = record["message_data"]["time"] / 1e9
                    print(
                        datetime.datetime.fromtimestamp(timestamp).strftime(
                            "%Y-%m-%d %H:%M:%S.%f"
                        )[:-3]
                    )
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.exit_loop = True
            stop_listening()
            thread.join()
            raise e

        logger.info("Waiting for threads to finish...")
        self.exit_loop = True
        stop_listening()
        thread.join()
        logger.info("Done")

    def download(
        self,
        output_filepath,
        log_id=None,
        log_name=None,
        topic_id=None,
        topic_name=None,
        data_filter=None,
        start_timestamp=None,
        end_timestamp=None,
        start_datetime=None,
        end_datetime=None,
        single_line=False,
        limit=100,
        max_workers=10,
    ):
        if log_name:
            log = self._list.logs(name=log_name)["data"][0]
            log_id = log["id"]
        elif log_id:
            log = self._get.log(log_id=log_id)["data"]
            log_name = log["name"]
        else:
            raise Exception("Must provide log_id or log_name")

        log_start_time = log["start_time"]
        log_end_time = log["end_time"]

        if topic_name:
            topic_id = self._list.topics(log_id=log_id, name=topic_name)["data"][0][
                "id"
            ]
        elif topic_id:
            topic_name = self._get.topic(topic_id=topic_id)["data"]["name"]
        else:
            raise Exception("Must provide topic_id or topic_name")

        if data_filter is not None:
            if data_filter == "default":
                data_filter = {"var": "payload", "op": "ilike", "val": "%%"}

        if start_datetime:
            start_timestamp = datetime.datetime.fromisoformat(
                start_datetime
            ).timestamp()
        if end_datetime:
            end_timestamp = datetime.datetime.fromisoformat(end_datetime).timestamp()

        output_file = open(output_filepath, "a+")

        logger.info(f"Log: {log_name} ({log_id})")
        logger.info(f"Topic: {topic_name} ({topic_id})")
        if start_timestamp:
            logger.info(f"Start timestamp: {start_timestamp}")
        if end_timestamp:
            logger.info(f"End timestamp: {end_timestamp}")
        if data_filter:
            logger.info(f"Data filter: {data_filter}")
        if output_filepath:
            logger.info(f"Output file: {output_filepath}")

        self.limit = limit

        self.record_buffer = []
        resp = self._list.records(
            log_id=log_id,
            topic_id=topic_id,
            offset=0,
            limit=0,
            data_filter=data_filter,
            timestamp_gte=start_timestamp,
            timestamp_lte=end_timestamp,
        )
        total_count = resp["count"]

        # Create timestamp ranges such that we have approximately 1000 records per range
        timestamp_ranges = []
        if start_timestamp is None:
            start_timestamp = log_start_time
        if end_timestamp is None:
            end_timestamp = log_end_time
        total_seconds = end_timestamp - start_timestamp
        total_records = total_count
        records_per_second = total_records / total_seconds
        records_per_range = 1000
        seconds_per_range = records_per_range / records_per_second
        timestamp = start_timestamp
        while timestamp < end_timestamp:
            timestamp_ranges.append((timestamp, timestamp + seconds_per_range))
            timestamp += seconds_per_range

        def get_records(timestamp_range):
            start_timestamp, end_timestamp = timestamp_range
            count = None
            records = []
            offset = 0
            while count is None or len(records) < count:
                resp = self._list.records(
                    log_id=log_id,
                    topic_id=topic_id,
                    offset=offset,
                    limit=limit,
                    data_filter=data_filter,
                    timestamp_gte=start_timestamp,
                    timestamp_lte=end_timestamp,
                )
                count = resp["count"]
                records += resp["data"]
                offset += limit
            return records

        logger.info(
            f"Downloading {total_count} records with limit {limit} using {max_workers} workers..."
        )
        with tqdm(total=total_count) as pbar:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for timestamp_range in timestamp_ranges:
                    future = executor.submit(get_records, timestamp_range)
                    futures.append(future)
                for future in futures:
                    records = future.result()
                    for record in records:
                        self._format_spdlog_data(
                            record, single_line=single_line, output_file=output_file
                        )
                    pbar.update(len(records))
        logger.info("Done")
