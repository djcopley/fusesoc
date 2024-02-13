# Copyright FuseSoC contributors
# Licensed under the 2-Clause BSD License, see LICENSE for details.
# SPDX-License-Identifier: BSD-2-Clause

import logging
import os.path
import tarfile
import urllib.request as urllib
from urllib.error import URLError

from ..provider.provider import Provider

logger = logging.getLogger(__name__)


URL = "https://github.com/{user}/{repo}/archive/{version}.tar.gz"


class Github(Provider):
    def _checkout(self, local_dir):
        user = self.config.get("user")
        repo = self.config.get("repo")

        version = self.config.get("version", "master")

        # TODO : Sanitize URL
        url = URL.format(user=user, repo=repo, version=version)
        logger.info(f"Downloading {user}/{repo} from github")
        try:
            (filename, headers) = urllib.urlretrieve(url)
        except URLError as e:
            raise RuntimeError(f"Failed to download '{url}'. '{e.reason}'")
        t = tarfile.open(filename)
        (cache_root, core) = os.path.split(local_dir)

        # Ugly hack to get the first part of the directory name of the extracted files
        tmp = t.getnames()[0]
        t.extractall(cache_root)
        os.rename(os.path.join(cache_root, tmp), os.path.join(cache_root, core))
