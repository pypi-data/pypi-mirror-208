# *****************************************************************#
# (C) Copyright IBM Corporation 2021.                             #
#                                                                 #
# The source code for this program is not published or otherwise  #
# divested of its trade secrets, irrespective of what has been    #
# deposited with the U.S. Copyright Office.                       #
# *****************************************************************#
"""This contains the `base` class from which ALL blocks inherit. This class is not for direct use
and most methods are, in fact, abstract.
"""

import threading

import semver

from autoai_ts_libs.deps.watson_core.toolkit import alog
from autoai_ts_libs.deps.watson_core.toolkit.errors import error_handler
import autoai_ts_libs.deps.watson_core.data_model as dm
from autoai_ts_libs.deps.watson_core import module as mod
from autoai_ts_libs.deps.watson_core import model_manager


log = alog.use_channel("BLBASE")
error = error_handler.get(log)


def block(id, name, version):
    """Apply this decorator to any class that should be treated as a block (i.e., extends
    `BlockBase`) and registered with watson_core so that the library "knows" the class is a
    block and is capable of loading instances of the block.

    Args:
        id:  str
            A UUID to use when registering this block with watson_core
        name:  str
            A human-readable name for the block
        version:  str
            A SemVer for the block

    Returns:
        A decorated version of the class to which it was applied, after registering the class
        as a valid block with watson_core
    """
    error.type_check("<COR56143234E>", str, id=id, name=name, version=version)

    semver.VersionInfo.parse(version)  # Make sure this is a valid SemVer

    def block_decorator(cls):
        # Verify this is a valid block (i.e., inherits from BlockBase)
        if not issubclass(cls, BlockBase):
            error(
                "<COR68265482E>",
                TypeError("`{}` does not extend `BlockBase`".format(cls.__name__)),
            )

        # Add attributes to the block class
        cls.BLOCK_ID = id
        cls.MODULE_ID = id  # Module ID == Block ID
        cls.BLOCK_NAME = name
        cls.MODULE_NAME = name  # Module Name == Block Name
        cls.BLOCK_VERSION = version
        cls.BLOCK_CLASS = cls.__module__ + "." + cls.__qualname__
        cls.PRODUCER_ID = dm.ProducerId(cls.BLOCK_NAME, cls.BLOCK_VERSION)

        # Verify UUID and add this block to the module and block registries
        current_class = model_manager.MODULE_REGISTRY.get(cls.MODULE_ID)
        if current_class is not None:
            error(
                "<COR30607646E>",
                RuntimeError(
                    "BLOCK_ID `{}` conflicts for classes `{}` and `{}`".format(
                        cls.MODULE_ID,
                        cls.__name__,
                        model_manager.MODULE_REGISTRY[cls.MODULE_ID].__name__,
                    )
                ),
            )
        model_manager.MODULE_REGISTRY[cls.MODULE_ID] = cls
        model_manager.BLOCK_REGISTRY[cls.BLOCK_ID] = cls

        return cls

    return block_decorator


class BlockSaver(mod.ModuleSaver):
    """A block saver that inherits from the module saver. Blocks should have a block_id
    and cannot directly save other modules (in contrast with workflows, which can).
    """

    def __init__(self, module, **kwargs):
        """Construct a new workflow saver.

        Args:
            module:  watson_core.module.Module
                The instance of the module to be saved.
        """
        super().__init__(**kwargs)
        if hasattr(module, "BLOCK_ID"):
            self.config.update(
                {
                    "name": module.BLOCK_NAME,
                    "version": module.BLOCK_VERSION,
                    "block_class": module.BLOCK_CLASS,
                    "block_id": module.BLOCK_ID,
                }
            )
        else:
            msg = "module `{}` is not a block.".format(module.__class__.__name__)
            log.warning("<COR80333031W>", msg)


class BlockBase(mod.ModuleBase):
    """Abstract base class for creating Blocks.  Inherits from ModuleBase."""

    # This mutex is shared among TensorFlow / Keras models to use around model loading.
    # In TensorFlow 1.x, model loading was *not* thread safe and this was required.
    # We need to verify whether or not model loading operations are thread safe in TensorFlow 2.x
    tensorflow_graph_mutex = threading.Lock()
