# *****************************************************************#
# (C) Copyright IBM Corporation 2022.                             #
#                                                                 #
# The source code for this program is not published or otherwise  #
# divested of its trade secrets, irrespective of what has been    #
# deposited with the U.S. Copyright Office.                       #
# *****************************************************************#
"""The base class for data model object backends"""

# Standard
from typing import Any, Type
import abc


# DataModelBackendBase #########################################################


class DataModelBackendBase(abc.ABC):
    """A base interface class for accessing data from within a given backend
    data layout
    """

    @abc.abstractmethod
    def get_attribute(self, data_model_class: Type["DataBase"], name: str) -> Any:
        """A data model backend must implement this in order to provide the
        frontend view the functionality needed to lazily extract data.

        Args:
            data_model_class:  Type[DataBase]
                The frontend data model class that is accessing this attribute
            name:  str
                The name of the attribute to access

        Returns:
            value:  Any
                The extracted attribute value
        """

    def cache_attribute(self, name: str, value: Any) -> bool:
        """Determine whether or not to cache the given attribute's result on the
        wrapping data model object.

        The base implementation always returns True. Derived classes may opt to
        always return False to fully disable caching, or cache conditionally
        based on the name/value of the individual field.

        Args:
            name:  str
                The name of the attribute to check
            value:  Any
                The extracted value

        Returns:
            should_cache:  bool
                True if the value should be cached, False otherwise
        """
        return True
