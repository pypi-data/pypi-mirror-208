# *****************************************************************#
# (C) Copyright IBM Corporation 2021.                             #
#                                                                 #
# The source code for this program is not published or otherwise  #
# divested of its trade secrets, irrespective of what has been    #
# deposited with the U.S. Copyright Office.                       #
# *****************************************************************#
from .base import RemoteClient
from .artifactory import ArtifactoryRemote
from .no_op import NoOpRemote
from .s3 import S3Remote
