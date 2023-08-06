import json
from contextlib import contextmanager
from pathlib import Path
from typing import Callable
from inspect import cleandoc

import docker


def _get_docker_images():
    docker_client = docker.from_env()
    exa_images = []
    try:
        exa_images = [str(img) for img in docker_client.images.list() if "exasol" in str(img)]
    finally:
        docker_client.close()
    return exa_images


def print_docker_images(writer: Callable[[str], None]):
    """
    Prints all docker images whith "exa" in it's name to stdout.
    :return: None
    """

    writer(cleandoc("""
        {seperator}
        Printing docker images
        {seperator}
        {images}""").format(
        seperator=20 * "=", images="\n".join(_get_docker_images())
    ))


def print_file(filename: Path, writer: Callable[[str], None]):
    """
    Opens file readonly, reads it content and prints to writer.
    """
    with open(filename, "r") as f:
        writer(f.read())


@contextmanager
def get_config(config_file: str):
    """
    Opens config file and returns parsed JSON object.
    """
    with open(config_file, "r") as f:
        yield json.load(f)
