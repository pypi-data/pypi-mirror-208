# *****************************************************************#
# (C) Copyright IBM Corporation 2021.                             #
#                                                                 #
# The source code for this program is not published or otherwise  #
# divested of its trade secrets, irrespective of what has been    #
# deposited with the U.S. Copyright Office.                       #
# *****************************************************************#
"""This contains the `base` class from which ALL resource types inherit. This class is not for
direct use and most methods are, in fact, abstract.
"""

import semver

import autoai_ts_libs.deps.watson_core.data_model as dm
from autoai_ts_libs.deps.watson_core import model_manager
from autoai_ts_libs.deps.watson_core import module as mod
from autoai_ts_libs.deps.watson_core.toolkit import alog
from autoai_ts_libs.deps.watson_core.toolkit.errors import error_handler

log = alog.use_channel("RSRCBASE")
error = error_handler.get(log)


def resource(id, name, version):
    """Apply this decorator to any class that should be treated as a resource type (i.e., extends
    `ResourceBase`) and registered with watson_core so that the library "knows" the class is a
    resource type and is capable of loading instances of the resource.

    Args:
        id:  str
            A UUID to use when registering this resource type with watson_core
        name:  str
            A human-readable name for the resource type
        version:  str
            A SemVer for the resource type

    Returns:
        A decorated version of the class to which it was applied, after registering the class
        as a valid resource type with watson_core
    """
    error.type_check("<COR76610591E>", str, id=id, name=name, version=version)

    semver.VersionInfo.parse(version)  # Make sure this is a valid SemVer

    def resource_decorator(cls):
        # Verify this is a valid resource type (i.e., inherits from ResourceBase)
        if not issubclass(cls, ResourceBase):
            error(
                "<COR37744263E>",
                TypeError("`{}` does not extend `ResourceBase`".format(cls.__name__)),
            )

        # Add attributes to the resource type class
        cls.RESOURCE_ID = id
        cls.MODULE_ID = id  # Module ID == Resource Type ID
        cls.RESOURCE_NAME = name
        cls.MODULE_NAME = name  # Module Name == Resource Name
        cls.RESOURCE_VERSION = version
        cls.RESOURCE_CLASS = cls.__module__ + "." + cls.__qualname__
        cls.PRODUCER_ID = dm.ProducerId(cls.RESOURCE_NAME, cls.RESOURCE_VERSION)

        # Verify UUID and add this resource type to the module and resource registries
        current_class = model_manager.MODULE_REGISTRY.get(cls.MODULE_ID)
        if current_class is not None:
            error(
                "<COR99556540E>",
                RuntimeError(
                    "RESOURCE_ID `{}` conflicts for classes `{}` and `{}`".format(
                        cls.MODULE_ID,
                        cls.__name__,
                        model_manager.MODULE_REGISTRY[cls.MODULE_ID].__name__,
                    )
                ),
            )
        model_manager.MODULE_REGISTRY[cls.MODULE_ID] = cls
        model_manager.RESOURCE_REGISTRY[cls.RESOURCE_ID] = cls
        return cls

    return resource_decorator


class ResourceSaver(mod.ModuleSaver):
    """A resource saver that inherits from the module saver. Resource types should have a
    resource_id.
    """

    def __init__(self, module, **kwargs):
        """Construct a new resource saver.

        Args:
            module:  watson_core.module.Module
                The instance of the module to be saved.
        """
        super().__init__(**kwargs)
        if hasattr(module, "RESOURCE_ID"):
            self.config.update(
                {
                    "name": module.RESOURCE_NAME,
                    "version": module.RESOURCE_VERSION,
                    "resource_class": module.RESOURCE_CLASS,
                    "resource_id": module.RESOURCE_ID,
                }
            )
        else:
            msg = "module `{}` is not a resource.".format(module.__class__.__name__)
            log.warning("<COR87448339W>", msg)


class ResourceBase(mod.ModuleBase):
    """Abstract base class for creating Resource Types.  Inherits from ModuleBase."""

    pass
