import os
import logging

from appdynamics.util.constants import APPDYNAMICS_LOGGER_NAME

logger = logging.getLogger(APPDYNAMICS_LOGGER_NAME)

# Add path `/var/task` to proxy certificate path which points to the lambda root directory if needed,
# and verify that path exists. If no path exists, return None.
def create_valid_lambda_path(path):
    if not path:
        return None
    if os.path.isabs(path):
        if not path.startswith("/var/task/"):
            return None
    else:
        path = f"/var/task/{path}"

    return path if os.path.isfile(path) else None


# Verify file exists and then read contents of file.
def read_lambda_file(path):
    path = create_valid_lambda_path(path)
    if path:
        try:
            with open(path, 'r') as f:
                password = f.read()
            return password
        except OSError as e:
            logger.error(f"Encountered OSError while trying to read '{path}': {e}")
    return None
