# *****************************************************************#
# (C) Copyright IBM Corporation 2021.                             #
#                                                                 #
# The source code for this program is not published or otherwise  #
# divested of its trade secrets, irrespective of what has been    #
# deposited with the U.S. Copyright Office.                       #
# *****************************************************************#
import random

from autoai_ts_libs.deps.watson_core.data_model.base import DataBase
from autoai_ts_libs.deps.watson_core.toolkit import alog
from autoai_ts_libs.deps.watson_core.toolkit.errors import error_handler

log = alog.use_channel("AUGMENT_BASE")
error = error_handler.get(log)


class AugmentorBase:
    def __init__(self, random_seed, produces_none=False):
        """The base class from which all Augmentors inherit. An augmentor is a bit different from a
        module in that it is subject to the following constraints / design considerations.

        - An augmentor must have the same input type as output type. Currently, this should only be
        data model objects / strings only.
        - An augmentor only takes one argument at run time, which is the object being augmented.
        Everything else should be contained within the class. This is necessary so that augmentors
        can be merged.

        Augmentors can only be combined if they have the same input/output object type.
        """
        error.type_check("<COR73155110E>", int, random_seed=random_seed)
        error.type_check(
            "<COR73301070E>", bool, allow_none=True, produces_none=produces_none
        )
        if random_seed is not None:
            random.seed(random_seed)
            self._is_random = True
            self._init_state = random.getstate()
        self.produces_none = produces_none

    def augment(self, inp_obj):
        """Take an object in, give an object back. Calls ._augment in the subclass.

        Args:
            inp_obj: str | watson_core.data_model.DataBase
                Object to be augmented.
        Returns:
            str | watson_core.data_model.DataBase
                Augmented object of same type as input inp_obj.
        """
        if not isinstance(inp_obj, self.augmentor_type):
            raise TypeError(
                "Input type [{}] is misaligned with augmentor type [{}]".format(
                    type(inp_obj), self.augmentor_type
                )
            )
        out_obj = self._augment(inp_obj)
        # Only some augmentors are allowed to return None.
        if out_obj is None and self.produces_none:
            return out_obj
        if not isinstance(out_obj, self.augmentor_type):
            error(
                "<COR72611702E>",
                TypeError(
                    "Output type [{}] is misaligned with augmentor type [{}]".format(
                        type(out_obj), self.augmentor_type
                    )
                ),
            )
        return out_obj

    def reset(self):
        """Reset random number generation for the current augmentor. Note that this currently
        assumes the augmentor is using the builtin random generator leveraged by Python; if
        you end up using something else, you may want to override this or restructure this
        base class to allow resetting of random states based on seed type.
        """
        if self._is_random:
            random.setstate(self._init_state)
