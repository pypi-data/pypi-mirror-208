# Scheme Base (used for all schemes)
from .base import SchemeBase

# General merged augmentor schemes to be leveraged by extensions of watson core
from .always_selection_scheme import AlwaysSelectionScheme
from .random_multi_selection_scheme import RandomMultiSelectionScheme
from .random_single_selection_scheme import RandomSingleSelectionScheme
