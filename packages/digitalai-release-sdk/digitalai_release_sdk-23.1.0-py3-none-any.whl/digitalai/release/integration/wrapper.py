from __future__ import annotations

import ast
import importlib
import json
import logging.config
import os
import signal
import sys

from .input_context import InputContext
from .job_data_encryptor import AESJobDataEncryptor, NoOpJobDataEncryptor
from .output_context import OutputContext
from .masked_io import MaskedIO
from .base_task import BaseTask
from .logging_config import LOGGING_CONFIG

# Mask the standard output and error streams by replacing them with MaskedIO objects.
masked_std_out: MaskedIO = MaskedIO(sys.stdout)
masked_std_err: MaskedIO = MaskedIO(sys.stderr)
sys.stdout = masked_std_out
sys.stderr = masked_std_err

# input and output context file location
input_context_file: str = os.getenv('INPUT_LOCATION', '/input')
output_context_file: str = os.getenv('OUTPUT_LOCATION', '/output')
base64_session_key: str = os.getenv('SESSION_KEY', '')
release_server_url: str = os.getenv('RELEASE_URL', '')
input_context: InputContext = None

# Create the encryptor
if base64_session_key:
    encryptor = AESJobDataEncryptor(base64_session_key)
else:
    encryptor = NoOpJobDataEncryptor()

# Set up logging
logging.config.dictConfig(LOGGING_CONFIG)

# Get the logger
logger = logging.getLogger("Digitalai")

# Initialize the global task object
dai_task_object: BaseTask = None


def abort_handler(signum, frame):
    """
    This function handles the abort request by calling the abort method on the global task object, if it exists.
    If the task object does not exist, it logs a message and exits with a status code of 1.
    """
    logger.debug("Received SIGTERM to gracefully stop the process")
    global dai_task_object

    if dai_task_object:
        dai_task_object.abort()
    else:
        logger.debug("Abort requested")
        sys.exit(1)


# Register abort handler
signal.signal(signal.SIGTERM, abort_handler)


def get_task_details():
    """
    Get the task details by reading the input context file, decrypting the contents using the encryptor,
    and parsing the JSON data into an InputContext object. Then, set the secrets for the masked standard output
    and error streams, build the task properties from the InputContext object.
    """
    logger.debug("Preparing for task properties.")
    with open(input_context_file) as data_input:
        input_content = data_input.read()
        decrypted_json = encryptor.decrypt(input_content)
        global input_context
        input_context = InputContext.from_dict(json.loads(decrypted_json))
    secrets = input_context.task.secrets()
    if input_context.release.automated_task_as_user.password:
        secrets.append(input_context.release.automated_task_as_user.password)
    masked_std_out.secrets = secrets
    masked_std_err.secrets = secrets
    task_properties = input_context.task.build_locals()
    return task_properties, input_context.task.type


def update_output_context_file(output_context: OutputContext):
    """
    Update the output context file by converting the output context object to a dictionary, serializing the
    dictionary to a JSON string, encrypting the string using the encryptor, and writing the encrypted string
    to the output context file.
    """
    logger.debug("Creating output context file")
    try:
        with open(output_context_file, "w") as data_output:
            output_content = json.dumps(output_context.to_dict())
            encrypted_json = encryptor.encrypt(output_content)
            data_output.write(encrypted_json)
    except Exception:
        logger.error("Unexpected error occurred.", exc_info=True)


def execute_task(task_object: BaseTask):
    """
    Execute the given task object by setting it as the global task object and starting its execution.
    If an exception is raised during execution, log the error. Finally, update the output context file
    using the output context of the task object.
    """
    try:
        global dai_task_object
        dai_task_object = task_object
        logger.debug("Starting task execution")
        dai_task_object.execute_task()
    except Exception:
        logger.error("Unexpected error occurred.", exc_info=True)
    finally:
        update_output_context_file(dai_task_object.get_output_context())


if __name__ == "__main__":
    try:
        # Get task details, parse the script file to get the task class, import the module,
        # create an instance of the task class, and execute the task
        task_props, task_type = get_task_details()
        task_class_name = task_type.split(".")[1]
        class_file_name = ''
        for filename in os.listdir(os.getcwd()):
            if filename.endswith('.py'):
                with open(filename) as file:
                    node = ast.parse(file.read())
                    classes = [n.name for n in node.body if isinstance(n, ast.ClassDef)]
                    if task_class_name in classes:
                        class_file_name = filename
                        break;
        if not class_file_name:
            raise ValueError(f"Could not find the {task_class_name} class")
        module = importlib.import_module(class_file_name[:-3])
        task_class = getattr(module, task_class_name)
        task_obj = task_class()
        task_obj.input_properties = task_props
        task_obj.release_server_url = release_server_url.strip('/')
        task_obj.release_context = input_context.release
        task_obj.task_id = input_context.task.id
        execute_task(task_obj)
    except Exception as e:
        # Log the error and update the output context file with exit code 1 if an exception is raised
        logger.error("Unexpected error occurred.", exc_info=True)
        update_output_context_file(OutputContext(1, str(e), {}, []))
