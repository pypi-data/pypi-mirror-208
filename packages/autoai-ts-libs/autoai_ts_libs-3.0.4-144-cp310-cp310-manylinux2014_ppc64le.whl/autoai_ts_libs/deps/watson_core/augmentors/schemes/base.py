# *****************************************************************#
# (C) Copyright IBM Corporation 2021.                             #
#                                                                 #
# The source code for this program is not published or otherwise  #
# divested of its trade secrets, irrespective of what has been    #
# deposited with the U.S. Copyright Office.                       #
# *****************************************************************#
"""Core base class for Augmentor combination schemes.
"""
import random

from autoai_ts_libs.deps.watson_core.augmentors import AugmentorBase
from autoai_ts_libs.deps.watson_core.toolkit import alog
from autoai_ts_libs.deps.watson_core.toolkit.errors import error_handler

log = alog.use_channel("AUG_SCHEME_BASE")
error = error_handler.get(log)


class SchemeBase:
    def __init__(self, preserve_order, augmentors, random_seed):
        """Initialize the core components of a merging scheme to be leveraged when combining
        augmentors.

        Args:
            preserve_order: bool
                Indicates whether or not the contained augmentors should always be considered in
                the order that they were provided when they are being applied.
            augmentors: list(AugmentorBase) | tuple(AugmentorBase)
                List or tuple of Augmentor objects to be applied.
            random_seed: int
                Random seed for controlling shuffling behavior.
        """
        error.type_check("<COR54555981E>", bool, preserve_order=preserve_order)
        error.type_check("<COR54155111E>", list, tuple, augmentors=augmentors)
        error.type_check("<COR73170110E>", int, random_seed=random_seed)
        error.value_check(
            "<COR67355718E>",
            len(augmentors) > 0,
            "Must provide at least one augmentor to build a scheme.",
        )
        error.type_check_all("<COR37249765E>", AugmentorBase, augmentors=augmentors)
        # Determine whether or not augmentors should be applied in the order provided or
        # applied in random order.
        self._preserve_order = preserve_order
        self._current_order = list(range(len(augmentors)))
        self._augmentors = augmentors
        self._init_state = random.getstate()

    def execute(self, obj):
        """Execute the merged scheme, i.e., augment the object by leveraging the encapsulated
        augmentors.

        Args:
            obj: str | watson_core.data_model.DataBase
                Object to be augmented.
        Returns:
            str | watson_core.data_model.DataBase
                Augmented object of same type as input obj.
        """
        if not self._preserve_order:
            random.shuffle(self._current_order)
        return self._execute(obj)

    def reset(self):
        """Reset the random state of all encapsulated augmentors and the scheme itself."""
        # Reset the random state for all augmentors
        for aug in self._augmentors:
            aug.reset()
        # Reset the random state for the scheme using the default random package
        random.setstate(self._init_state)
