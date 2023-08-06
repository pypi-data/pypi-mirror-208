import logging
from typing import Tuple

import click
from exasol_script_languages_container_tool.lib.api.run_db_tests import run_db_test

from exasol_script_languages_container_ci.lib.common import print_docker_images

from exasol_script_languages_container_tool.lib.tasks.test.test_container import AllTestsResult


class CIExecuteTest:

    def execute_tests(self,
                      flavor_path: Tuple[str, ...],
                      docker_user: str,
                      docker_password: str,
                      test_container_folder: str) -> Tuple[AllTestsResult, AllTestsResult]:
        """
        Run db tests
        """
        logging.info(f"Running command 'run_db_test' for flavor-path {flavor_path}")
        run_db_test_flavor_result = \
            run_db_test(flavor_path=flavor_path,
                        workers=7,
                        source_docker_username=docker_user,
                        source_docker_password=docker_password,
                        test_container_folder=test_container_folder)
        logging.info(f"Running command 'run_db_test' for linker_namespace_sanity for flavor-path {flavor_path}")
        run_db_test_linkernamespace = \
            run_db_test(flavor_path=flavor_path, workers=7,
                        test_folder=("test/linker_namespace_sanity",),
                        release_goal=("base_test_build_run",),
                        source_docker_username=docker_user,
                        source_docker_password=docker_password,
                        test_container_folder=test_container_folder)
        print_docker_images(logging.info)
        return run_db_test_flavor_result, run_db_test_linkernamespace
