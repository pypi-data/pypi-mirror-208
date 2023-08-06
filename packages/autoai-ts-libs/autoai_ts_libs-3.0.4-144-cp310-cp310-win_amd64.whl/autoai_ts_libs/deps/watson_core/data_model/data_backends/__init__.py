# *****************************************************************#
# (C) Copyright IBM Corporation 2022.                              #
#                                                                  #
# The source code for this program is not published or otherwise   #
# divested of its trade secrets, irrespective of what has been     #
# deposited with the U.S. Copyright Office.                        #
# *****************************************************************#
"""Class higherarchy for implementing independent backends for Data Model
classes
"""

from .base import DataModelBackendBase
from .dict_backend import DictBackend
