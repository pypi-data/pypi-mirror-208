import logging
from typing import Tuple

from exasol_script_languages_container_tool.lib.api import export
from exasol_script_languages_container_tool.lib.tasks.export.export_containers import ExportContainerResult

from exasol_script_languages_container_ci.lib.common import print_docker_images


class CIExport:
    def export(self,
               flavor_path: Tuple[str, ...],
               export_path: str) -> ExportContainerResult:
        """
        Export the flavor as tar.gz file
        """

        logging.info(f"Running command 'push' with parameters: {locals()}")
        export_result = export(flavor_path=flavor_path,
                               export_path=export_path,
                               workers=7)
        print_docker_images(logging.info)
        return export_result
