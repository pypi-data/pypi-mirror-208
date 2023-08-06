# *****************************************************************#
# (C) Copyright IBM Corporation 2021.                             #
#                                                                 #
# The source code for this program is not published or otherwise  #
# divested of its trade secrets, irrespective of what has been    #
# deposited with the U.S. Copyright Office.                       #
# *****************************************************************#
"""Interface for remotes"""
import abc
from typing import List


class RemoteClient(abc.ABC):
    """Interface for a Repository's remote client.
    Implement this for any backend you want to support, e.g. local disk, Artifactory, S3...
    """

    @abc.abstractmethod
    def list(self, directory) -> List[str]:
        """Return a list of files in directory"""

    @abc.abstractmethod
    def upload(self, source_file, destination_path) -> None:
        """Push a single file source file to a remote destination"""

    @abc.abstractmethod
    def download(self, source_path, destination_path) -> None:
        """Pull a single file from a remote destination to a local path"""
