import os
import sys
from pathlib import Path
import importlib
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ros_import_error = False

import rospkg
import rosmsg
import roslib.message
import genpy.generator


LOAD_ENV_MSG_DEFS = False


class DefinitionNotFoundError(Exception):
    pass


class MessageGenerator:
    """Methods for generating message definition classes."""

    def __init__(self, getter, lister, base_path="/tmp"):
        self.getter = getter
        self.lister = lister
        self.message_path = base_path + "/message_generation"

    def list_message_types(self):
        message_types = []
        count = None
        offset = 0

        limit = 100
        max_iters = 100
        current_iter = 0
        max_restarts = 10
        current_restart = 0
        while count is None or count > len(message_types):
            list_message_types_response = self.lister.message_type(
                limit=limit, offset=offset
            )
            new_count = list_message_types_response["count"]
            if count is None:
                count = new_count
            elif count != new_count:
                logger.warn("Message type count changed during load; restarting...")
                message_types = []
                count = None
                offset = 0
                current_iter = 0
                current_restart += 1
                if current_restart > max_restarts:
                    raise Exception("Exceeded max restarts when loading message_types.")
                continue
            message_types += list_message_types_response["data"]
            current_iter += 1
            if current_iter > max_iters:
                raise Exception(
                    f"Exceeded max iterations when loading {count} message_types."
                )
            offset += limit

        logger.debug(f"Loaded {len(message_types)} message types.")
        return message_types

    def setup_message_definitions(self, definition_keys=None):
        download_path = os.path.join(self.message_path, "message_descriptions")
        logger.debug(f"download_path: {download_path}")
        if not os.path.exists(download_path):
            os.makedirs(download_path)

        logger.debug("Listing message types...")
        message_types = self.list_message_types()
        processed_message_types = []
        for message_type in message_types:
            message_type_name = message_type["name"]
            message_type_md5 = message_type["md5"]
            if (definition_keys is not None) and (message_type_name in definition_keys):
                if definition_keys[message_type_name] != message_type_md5:
                    logger.debug(
                        f"Skipping {message_type_name} ({message_type_md5}) based on definition_keys."
                    )
                    continue
            if message_type_name in processed_message_types:
                logger.debug(
                    f"Skipping {message_type_name} ({message_type_md5}) as a type of this name has already been processed."
                )
                continue
            package, name = message_type_name.split("/")
            definition = message_type["definition"]
            self.process_message_definition(definition, package, name)
            processed_message_types.append(message_type_name)

        logger.debug("Generating message classes.")
        self.generate_messages()

    def process_message_definition(self, definition, package, name):
        div = "================================================================================\n"
        defs = definition.split(div)
        main_def = defs[0]
        self.write_message_definition(main_def, package, name)
        for aux_profile in defs[1:]:
            msg_line, aux_def = aux_profile.split("\n", 1)
            assert msg_line[:5] == "MSG: "
            msg_type = msg_line[5:]
            aux_package, aux_name = msg_type.split("/")
            self.write_message_definition(aux_def, aux_package, aux_name)

    def write_message_definition(self, definition, package, name):
        download_path = os.path.join(self.message_path, "message_descriptions")
        target = os.path.join(download_path, f"{package}/msg/")
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        with open(f"{target}/{name}.msg", "w") as f:
            f.write(definition)

    def generate_package_messages(self, package, package_files, search_path):
        class_dir = os.path.join(self.message_path, f"message_classes/{package}/msg")
        os.makedirs(class_dir, exist_ok=True)

        init_file_path = os.path.join(class_dir, "__init__.py")
        init_file = Path(init_file_path)
        if not init_file.is_file():
            init_file.touch()
        logger.debug(f"package_files: {package_files}")
        with open(init_file_path, "a+") as f:
            for package_file in package_files:
                logger.debug(f"Adding package_file: {package_file}")
                class_name = package_file.split("/")[-1].split(".")[0]
                f.write(f"from ._{class_name} import *\n")

        generator = genpy.generator.MsgGenerator()
        logger.debug(f"Generating {package} messages...")
        result = generator.generate_messages(
            package, package_files, class_dir, search_path
        )
        assert result == 0
        "Error generating messages."

    def get_message_class(self, message_type):
        # TODO: verify that it's ok to remove this
        # message_class = roslib.message.get_message_class(message_type)
        message_class = None
        if message_class is None:
            package, name = message_type.split("/")
            try:
                if f"{package}.msg._{name}" in sys.modules:
                    importlib.reload(sys.modules[f"{package}.msg"])
                    importlib.reload(sys.modules[f"{package}.msg._{name}"])
                message_module = importlib.import_module(f"{package}.msg._{name}")
            except ModuleNotFoundError:
                raise DefinitionNotFoundError(
                    f"Failed importing class for message_type {message_type}."
                )
            message_class = getattr(message_module, name)
        return message_class

    def generate_messages(self):
        logger.debug(f"Generate messages in {self.message_path}.")
        os.makedirs(os.path.join(self.message_path, "message_classes"), exist_ok=True)
        init_file_path = os.path.join(self.message_path, "message_classes/__init__.py")
        init_file = Path(init_file_path)
        if not init_file.is_file():
            init_file.touch()

        logger.debug("Setting up search path...")
        desc_dir = os.path.join(self.message_path, "message_descriptions")
        r = rospkg.RosPack()
        it = rosmsg.iterate_packages(r, ".msg")
        search_path = {}

        if LOAD_ENV_MSG_DEFS:
            logger.debug("Loading environment message definitions...")
            for package, directory in it:
                search_path[package] = [directory]

            layer_path = "/opt/python"
            if os.path.isdir(layer_path):
                for package in os.listdir(layer_path):
                    if package[-5:] == "_msgs":
                        search_path[package] = [f"{layer_path}/{package}/msg"]

        for package in os.listdir(desc_dir):
            search_path[package] = [f"{desc_dir}/{package}/msg"]

        logger.debug(f"Search path: {search_path}")

        logger.debug("Generating local messages...")
        local_path = os.path.join(os.path.dirname(__file__), "..")
        logger.debug(f"local_path: {local_path}")
        local_message_packages = [
            "std_msgs",
            "rosgraph_msgs",
            "actionlib_msgs",
            "diagnostic_msgs",
            "geometry_msgs",
            "nav_msgs",
            "sensor_msgs",
            "shape_msgs",
            "stereo_msgs",
            "trajectory_msgs",
            "visualization_msgs",
        ]
        for package in local_message_packages:
            msg_dir = f"{local_path}/definitions/{package}/msg"
            search_path[package] = [msg_dir]
            package_files = []
            for file in os.listdir(msg_dir):
                if file.endswith(".msg"):
                    package_file = f"{msg_dir}/{file}"
                    package_files.append(package_file)
            logger.debug(f"package: {package}")
            self.generate_package_messages(package, package_files, search_path)

        logger.debug("Generating packages messages...")
        for package in os.listdir(desc_dir):
            msg_dir = f"{desc_dir}/{package}/msg"
            search_path[package] = [msg_dir]
            package_files = []
            for file in os.listdir(msg_dir):
                if file.endswith(".msg"):
                    package_file = f"{msg_dir}/{file}"
                    package_files.append(package_file)
            logger.debug(f"package: {package}")
            self.generate_package_messages(package, package_files, search_path)

        class_dir = os.path.join(self.message_path, "message_classes")
        sys.path.insert(1, class_dir)
        logger.debug(f"PATH: {sys.path}")
