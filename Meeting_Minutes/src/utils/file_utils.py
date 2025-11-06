"""Generic File IO utils
"""

import functools
import json
import logging
import logging.config
import os
import pickle
import shutil
from pathlib import Path
from time import time
from typing import Any

import hjson
from loguru import logger

from src.utils.config_utils import TEMP_DIR, config


def load_hjson(file_path) -> dict:
    """
    Load data from an Hjson file.

    Args:
    file_path: The path to the Hjson file.

    Returns:
    dict: The data loaded from the Hjson file.
    """
    try:
        with open(file_path, "r") as fp:
            data = hjson.load(fp)
        return dict(data)
    except FileNotFoundError:
        logger.error(f"No such file or directory: '{file_path}'")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    return {}


def get_logger(name: str, logfile: str = "log.log", debug_mode: bool = config["debug"]):
    """
    logger = get_logger('Doc-Reader')  # Example usage
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging_level = logging.DEBUG if debug_mode else logging.INFO
    logging.basicConfig(
        level=logging_level, format=log_format, filename=logfile, filemode="w"
    )

    console = logging.StreamHandler()
    console.setLevel(logging_level)
    console.setFormatter(logging.Formatter(log_format))
    logging.getLogger(name).addHandler(console)
    return logging.getLogger(name)


def time_logger(func):
    """
    A decorator that logs the time a function takes to execute.
    """

    @functools.wraps(func)
    def timer_wrapper(*args, **kwargs):
        tic = time()
        result = func(*args, **kwargs)
        logger.info(f"Time taken by {func.__name__}: {time() - tic:.2f} s")
        return result

    return timer_wrapper


def load_json(file_path) -> dict:
    """
    utility function that loads data from an JSON file.

    Args:
    file_path: The path to the JSON file.

    Returns:
    dict: The data loaded from the JSON file.
    """
    try:
        with open(file_path, "r") as fp:
            data = json.load(fp)
        return dict(data)
    except FileNotFoundError:
        logger.error(f"No such file or directory: '{file_path}'")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    return {}


def dump_to_json(data: Any, file_path) -> None:
    """
    utility function to dump data into a JSON file.

    Args:
        data (Any): The data to be written to the file.
        file_path: The path to the file to write to.
    """
    try:
        with open(file_path, "w") as fp:
            json.dump(data, fp, indent=4)
        logging.info(f"Data successfully dumped to JSON file: {file_path}")
    except Exception as exp:
        logging.error(f"Failed to dump data to JSON file {file_path}: {exp}")
        raise exp


def load_pickle(file_path):
    """
    utility function that loads a Python object from a Pickle file.

    Args:
        file_path : str
            The path of the Pickle file to load.

    Returns:
        object : any type
            The Python object that was loaded from the Pickle file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
    """
    try:
        with open(file_path, "rb") as file:
            return pickle.load(file)
    except Exception as exp:
        logging.error(f"Failed to load data from pickle file {file_path}: {exp}")
        raise exp


def dump_to_pickle(data: Any, file_path: str) -> None:
    """Dump data to a pickle file.

    Args:
        data : Any
            The Python object to be dumped into a Pickle file.
        file_path
            The path where the Pickle file will be saved.
    """
    try:
        with open(file_path, "wb") as fp:
            pickle.dump(data, fp)
        logging.info(f"Data successfully dumped to pickle file: {file_path}")
    except Exception as exp:
        logging.error(f"Failed to dump data to pickle file {file_path}: {exp}")
        raise exp


def write_tempfile(temp_file, temp_dir: Path = TEMP_DIR):
    """utility function writes a bytes object to a temp file in temp_dir.

    Args:
        temp_file (_type_): Uploaded file
        temp_dir (Path, optional): Dir to store the temp file. Defaults to TEMP_DIR.

    Returns:
        temp_file_path (Path): Path to stored temp file
    """
    contents = temp_file.file.read()
    # Save the file temporarily
    temp_file_path = temp_dir / temp_file.filename
    with open(temp_file_path, "wb") as f:
        f.write(contents)
    return temp_file_path


def delete_tempfile(temp_file_path):
    """utility function that deletes the temp file.

    Args:
        temp_file_path (_type_): Path to temp file.
    """
    if os.path.isfile(temp_file_path):
        try:
            os.remove(temp_file_path)
        except PermissionError as pe:
            logger.error(f"Another Process is accessing the file: {pe}")
    else:
        logger.error(f"{temp_file_path} does not exist.")


def read_csv_as_text(file_path, encoding="utf-16") -> str:
    """
    utility function that reads a csv file and returns its content as str.

    Args:
        file_path (str): The path to the file to be read. This should be a full path, including the file name and extension.

    Returns:
        content (str): The content of the csv file as a string.
    """
    with open(file_path, "r", encoding=encoding) as file:
        content = file.read()
    return content


def read_file_as_bytes(file_path):
    """
    utility function that reads a file and returns its content as bytes.

    Args:
        file_path (str): The path to the file to be read. This should be a full path, including the file name and extension.

    Returns:
        file_bytes: The content of the file as bytes.
    """

    # Open the file in binary mode
    with open(file_path, "rb") as file:
        file_bytes = file.read()

    return file_bytes


def load_txt(file_path):
    """
    Loads content from a specified file.

    Args:
        file_path (str): The path to the file containing the content.

    Returns:
        str: The content of the file.

    Raises:
        Exception: If the file cannot be read.
    """
    try:
        with open(file_path, "r") as file:
            content = file.read()
        return content
    except Exception as e:
        logger.error(f"Failed to load content from {file_path}: {e}")
        raise


def make_directory(directory_path):
    """
    Creates a directory at the specified path

    Args:
        directory_path (str): The path where the directory should be created.

    Returns:
        bool: True if the directory was created successfully or already exists, False otherwise.
    """
    try:
        # Attempt to create the directory, allowing it to exist without raising an error
        os.makedirs(directory_path, exist_ok=True)
        logger.info(
            f"Directory created successfully or already exists: {directory_path}"
        )
        return directory_path

    except Exception as exp:
        logger.error(
            f"An error occurred while creating the directory {directory_path}: {exp}"
        )
        raise exp


def ensure_directory_exists(directory) -> None:
    """Ensure the directory exists, create if it doesn't."""
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logging.info(f"Directory created: {directory}")
        else:
            logging.info(f"Directory already exists: {directory}")
    except Exception as exp:
        logging.error(f"Error creating directory {directory}: {exp}")
        raise exp


def delete_directory(directory_path: str) -> bool:
    """
    Delete a directory and all of its contents.

    Parameters:
    directory_path (str): The path of the directory to be deleted.

    Returns:
    bool: True if the directory was deleted successfully, False otherwise.

    Raises:
    ValueError: If the specified path is not a directory.
    """
    if not os.path.isdir(directory_path):
        logging.error(f"Specified path is not a directory: {directory_path}")
        raise ValueError(f"Specified path is not a directory: {directory_path}")

    try:
        # Recursively delete a directory tree
        shutil.rmtree(directory_path)
        logging.info(f"Directory deleted successfully: {directory_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to delete directory {directory_path}: {e}")
        return False
