# Copyright FuseSoC contributors
# Licensed under the 2-Clause BSD License, see LICENSE for details.
# SPDX-License-Identifier: BSD-2-Clause

import logging
import subprocess

from ..provider.provider import Provider
from ..utils import Launcher

logger = logging.getLogger(__name__)


class Git(Provider):
    @staticmethod
    def _checkout_library_version(library):
        git_args = ["-C", library.location, "checkout", "-q", library.sync_version]

        if library.sync_version:
            logger.info(
                "Checkout out {} at version {}".format(
                    library.name, library.sync_version
                )
            )
            Launcher("git", git_args).run()

    @staticmethod
    def init_library(library):
        logger.info(f"Cloning library into {library.location}")
        git_args = ["clone", library.sync_uri, library.location]
        try:
            Launcher("git", git_args).run()
            Git._checkout_library_version(library)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(str(e))

    @staticmethod
    def update_library(library):
        git_args = ["-C", library.location, "pull"]
        try:
            Git._checkout_library_version(library)
            Launcher("git", git_args).run()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(str(e))

    def _checkout(self, local_dir):
        version = self.config.get("version", None)

        # TODO : Sanitize URL
        repo = self.config.get("repo")
        logger.info("Checking out " + repo + " to " + local_dir)
        try:
            args = [
                "clone",
                "-q",
                "--depth",
                "1",
                "--no-single-branch",
                repo,
                local_dir,
            ]
            Launcher("git", args).run()
        except RuntimeError as e:
            try:
                args = ["clone", "-q", "--no-single-branch", repo, local_dir]
                Launcher("git", args).run()
            except Exception:
                raise e
        if version:
            args = ["-C", local_dir, "checkout", "-q", version]
            Launcher("git", args).run()
