import logging
from typing import Tuple

import click
from exasol_script_languages_container_tool.lib.api.push import push

from exasol_script_languages_container_ci.lib.common import print_docker_images


class CIPush:
    def push(self,
             flavor_path: Tuple[str, ...],
             target_docker_repository: str,
             target_docker_tag_prefix: str,
             docker_user: str,
             docker_password: str):
        """
        Push the docker image to Dockerhub
        """

        logging.info(f"Running command 'push' with parameters: {locals()}")
        push(flavor_path=flavor_path,
             push_all=True,
             force_push=True,
             workers=7,
             target_docker_repository_name=target_docker_repository,
             target_docker_tag_prefix=target_docker_tag_prefix,
             target_docker_username=docker_user,
             target_docker_password=docker_password)
        print_docker_images(logging.info)
