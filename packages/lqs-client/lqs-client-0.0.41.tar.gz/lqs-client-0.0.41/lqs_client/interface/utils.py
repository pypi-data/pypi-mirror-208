import io
import os
import logging
from uuid import UUID
from enum import Enum
from concurrent.futures import ThreadPoolExecutor

import av
import numpy as np
from PIL import Image as ImagePIL
from sensor_msgs.msg import Image, CompressedImage

logging.basicConfig(
    level=os.getenv("LQS_LOG_LEVEL") or logging.INFO,
    format="%(asctime)s  (%(levelname)s - %(name)s): %(message)s",
)
logger = logging.getLogger(__name__)


class S3Resource(str, Enum):
    extraction = "extraction"
    ingestion = "ingestion"
    log = "log"
    record = "record"
    topic = "topic"


class Utils:
    def __init__(self, getter, s3, gen, config):
        self._getter = getter
        self._s3 = s3
        self._gen = gen
        self._config = config
        self._cached_ingestions = {}
        self._cached_message_types = {}

        if self._config.get("aws_access_key_id"):
            self._use_s3_directly = True
        else:
            self._use_s3_directly = False

        if self._config.get("verbose"):
            logger.setLevel(logging.DEBUG)

    def upload_part(
        self,
        resource: S3Resource,
        resource_id: UUID,
        file_path: str,
        upload_id: str,
        part_number: int,
        key: str = None,
        part_size: int = 5 * 1024 * 1024,
    ):
        file = open(file_path, "rb")
        file.seek((part_number - 1) * part_size)
        part_data = file.read(part_size)

        logger.debug(f"Uploading part {part_number} ({len(part_data)} bytes)")

        if key is None:
            key = file_path.split("/")[-1]

        r_headers, r_params, r_body = self._s3.upload_part(
            resource=resource,
            resource_id=resource_id,
            key=key,
            part_number=part_number,
            upload_id=upload_id,
            body=part_data,
        )
        e_tag = r_headers["ETag"]
        return {"PartNumber": part_number, "ETag": e_tag}

    def upload(
        self,
        resource: S3Resource,
        resource_id: UUID,
        file_path: str,
        key: str = None,
        part_size: int = 5 * 1024 * 1024,
        max_workers: int = 8,
        exist_ok: bool = False,
    ):
        if key is None:
            key = file_path.split("/")[-1]

        if not exist_ok:
            r_headers, r_params, r_body = self._s3.head_object(
                resource=resource, resource_id=resource_id, key=key
            )
            logger.debug(f"HEAD {resource} ({resource_id}): {key} - {r_body}")
            if r_body["exists"]:
                raise FileExistsError(f"File already exists in S3: {key}")

        logger.debug("Uploading %s to %s", file_path, key)
        logger.debug("Creating multipart upload for %s %s", resource, resource_id)
        (
            _create_mpu_headers,
            _create_mpu_params,
            create_mpu_body,
        ) = self._s3.create_multipart_upload(
            resource=resource, resource_id=resource_id, key=key
        )
        try:
            upload_id = create_mpu_body["InitiateMultipartUploadResult"]["UploadId"]
            logger.debug("Upload ID: %s", upload_id)
        except KeyError as e:
            logger.error("Error creating multipart upload: %s", create_mpu_body)
            raise e

        file = open(file_path, "rb")
        file_size = os.fstat(file.fileno()).st_size
        part_count = (file_size // part_size) + 1
        logger.debug("File size: %s", file_size)
        logger.debug("Part size: %s", part_size)

        parts = []
        futures = []
        logger.debug("Uploading parts with %s workers", max_workers)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for i in range(part_count):
                part_number = i + 1
                future = executor.submit(
                    self.upload_part,
                    resource=resource,
                    resource_id=resource_id,
                    file_path=file_path,
                    upload_id=upload_id,
                    part_number=part_number,
                    key=key,
                    part_size=part_size,
                )
                futures.append(future)

        for future in futures:
            parts.append(future.result())
            logger.debug("Uploaded part %s of %s", len(parts), part_count)

        logger.debug("Completing multipart upload")
        (
            _complete_mpu_headers,
            _complete_mpu_params,
            complete_mpu_body,
        ) = self._s3.complete_multipart_upload(
            resource=resource,
            resource_id=resource_id,
            key=key,
            upload_id=upload_id,
            parts=parts,
        )
        logger.debug("Completed multipart upload %s", complete_mpu_body)

    # Message Processing

    def get_message_data_from_record(self, record):
        ingestion_id = record["ingestion_id"]
        s3_bucket = record["s3_bucket"]
        s3_key = record["s3_key"]
        if s3_bucket is None or s3_key is None:
            # the record doesn't have the s3 bucket and key, so we need to get them from the ingestion
            if ingestion_id is None:
                raise ValueError(
                    "No S3 bucket or key and no ingestion is available on record."
                )
            elif ingestion_id in self._cached_ingestions:
                ingestion = self._cached_ingestions[ingestion_id]
            elif ingestion_id is not None:
                ingestion = self._getter.ingestion(ingestion_id)["data"]
                self._cached_ingestions[ingestion_id] = ingestion

            s3_bucket = ingestion["s3_bucket"]
            s3_key = ingestion["s3_key"]
            if s3_bucket is None or s3_key is None:
                raise ValueError("No S3 bucket or key available on record's ingestion.")

        message_data = self._s3.get_message_data_from_record(
            record=record, s3_bucket=s3_bucket, s3_key=s3_key, ingestion_id=ingestion_id
        )

        return message_data

    def get_message_class(self, message_type_id):
        if message_type_id in self._cached_message_types:
            message_type = self._cached_message_types[message_type_id]
        else:
            message_type = self._getter.message_type(message_type_id)["data"]
            self._cached_message_types[message_type_id] = message_type

        message_type_name = message_type["name"]
        if "_generated" not in message_type or True:
            self._gen.process_message_definition(
                message_type["definition"], *message_type_name.split("/")
            )
            self._gen.generate_messages()
            self._cached_message_types[message_type_id]["_generated"] = True

        message_class = self._gen.get_message_class(message_type_name)
        return message_class

    def get_ros_message_from_message_data(self, message_data, message_type_id):
        message_class = self.get_message_class(message_type_id)
        message = message_class()
        message.deserialize(message_data)
        return message

    def get_ros_message_from_record(self, record):
        message_data = self.get_message_data_from_record(record=record)

        return self.get_ros_message_from_message_data(
            message_data=message_data, message_type_id=record["message_type_id"]
        )

    def get_image_from_ros_message(self, message, image_mode=None):
        # We assume that if the message class name is "Image" or "CompressedImage",
        # then the message type matches the ROS message type.
        message_class_name = message.__class__.__name__
        if message_class_name == "Image":
            img_modes = {
                "16UC1": "I;16",
                "mono8": "L",
                "mono16": "I;16",
                "32FC1": "F",
                "8UC1": "L",
                "8UC3": "RGB",
                "rgb8": "RGB",
                "bgr8": "RGB",
                "rgba8": "RGBA",
                "bgra8": "RGBA",
                "bayer_rggb": "L",
                "bayer_rggb8": "L",
                "bayer_gbrg": "L",
                "bayer_gbrg8": "L",
                "bayer_grbg": "L",
                "bayer_grbg8": "L",
                "bayer_bggr": "L",
                "bayer_bggr8": "L",
                "yuv422": "YCbCr",
                "yuv411": "YCbCr",
            }
            if image_mode is None:
                if not message.encoding:
                    logger.warn(f"No encoding: {message.encoding}")
                    return None
                image_mode = img_modes[message.encoding]
            img = ImagePIL.frombuffer(
                image_mode,
                (message.width, message.height),
                message.data,
                "raw",
                image_mode,
                0,
                1,
            )
            if message.encoding == "bgr8":
                b, g, r = img.split()
                img = ImagePIL.merge("RGB", (r, g, b))

            if message.encoding in ["mono16", "16UC1", "32FC1"]:
                pixels = np.asarray(img)
                pixel_range = np.max(pixels) - np.min(pixels)
                if pixel_range == 0:
                    pixels *= 0
                else:
                    pixels = ((pixels - np.min(pixels)) / pixel_range) * 255.0
                img = ImagePIL.fromarray(pixels)
                img = img.convert("L")
        elif message_class_name == "CompressedImage":
            if message.format == "h264":
                codec = av.CodecContext.create("h264", "r")
                packets = av.packet.Packet(message.data)
                img = codec.decode(packets)[0].to_image()
            else:
                img = ImagePIL.open(io.BytesIO(message.data))
        else:
            raise NotImplementedError(
                f"Message type {type(message)} not supported for image conversion."
            )

        return img

    def process_image(
        self,
        img,
        format="PNG",
        output_path=None,
        resize_width=None,
        resize_height=None,
        resize_scale=None,
    ):
        if (
            resize_width is not None
            or resize_height is not None
            or resize_scale is not None
        ):
            width = img.width
            height = img.height
            if resize_width is not None:
                width = resize_width
            if resize_height is not None:
                height = resize_height
            if resize_scale is not None:
                width = int(width * resize_scale)
                height = int(height * resize_scale)
            img = img.resize((width, height))

        if output_path is not None:
            img.save(output_path, format)
            return None
        else:
            buffered_img = io.BytesIO()
            img.save(buffered_img, format)
            buffered_img.seek(0)
            return buffered_img

    def get_image_from_record(self, record):
        message = self.get_ros_message_from_record(record=record)
        return self.get_image_from_ros_message(message)

    def get_processed_image_from_record(self, record):
        img = self.get_image_from_record(record)
        return self.process_image(img)
