import logging
from pathlib import Path
from typing import Tuple

from exasol_script_languages_container_tool.lib.api import security_scan
from exasol_script_languages_container_tool.lib.tasks.security_scan.security_scan import AllScanResult

import exasol_script_languages_container_ci.lib.common


class CISecurityScan:

    def run_security_scan(self, flavor_path: Tuple[str, ...]) -> AllScanResult:
        """
        Run security scan and print result
        """

        logging.info(f"Running command 'security_scan' with parameters {locals()}")
        security_scan_result = security_scan(flavor_path=flavor_path, workers=7)
        exasol_script_languages_container_ci.lib.common.print_docker_images(logging.info)
        logging.info("============= SECURITY REPORT ===========")
        # Important: Call print_file over the global module name, otherwise the patch in the unit-test does not work!
        exasol_script_languages_container_ci.lib.common.print_file(
            Path() / ".build_output" / "security_scan" / "security_report", logging.info)
        return security_scan_result
