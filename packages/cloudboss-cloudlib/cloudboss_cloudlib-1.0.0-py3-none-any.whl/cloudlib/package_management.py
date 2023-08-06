import logging
import os
import shutil

logger = logging.getLogger(__name__)


def remove_pycache(destination_folder):
    logger.debug("Deleting __pycache__ folders from %s", destination_folder)
    for root, _, __ in os.walk(destination_folder):
        if root.endswith("__pycache__"):
            shutil.rmtree(root, ignore_errors=True)
