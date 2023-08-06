# *****************************************************************#
# (C) Copyright IBM Corporation 2021.                             #
#                                                                 #
# The source code for this program is not published or otherwise  #
# divested of its trade secrets, irrespective of what has been    #
# deposited with the U.S. Copyright Office.                       #
# *****************************************************************#
"""This contains the `base` class from which **all** Workflows inherit. This
class is not for direct use and most methods are, in fact, abstract and
inherited from ModuleBase.
"""

import os

import semver

import autoai_ts_libs.deps.watson_core as watson_core

import autoai_ts_libs.deps.watson_core.data_model as dm
from autoai_ts_libs.deps.watson_core import model_manager
from autoai_ts_libs.deps.watson_core import module as mod
from autoai_ts_libs.deps.watson_core.toolkit import alog
from autoai_ts_libs.deps.watson_core.toolkit.errors import error_handler

log = alog.use_channel("WFBASE")
error = error_handler.get(log)


def workflow(id, name, version):
    """Apply this decorator to any class that should be treated as a workflow (i.e., extends
    `WorkflowBase`) and registered with watson_core so that the library "knows" the class is a
    workflow and is capable of loading instances of the workflow.

    Args:
        id:  str
            A UUID to use when registering this workflow with watson_core
        name:  str
            A human-readable name for the workflow
        version:  str
            A SemVer for the workflow

    Returns:
        A decorated version of the class to which it was applied, after registering the class
        as a valid workflow with watson_core
    """
    error.type_check("<COR35888256E>", str, id=id, name=name, version=version)

    semver.VersionInfo.parse(version)  # Make sure this is a valid SemVer

    def workflow_decorator(cls):
        # Verify this is a valid workflow (i.e., inherits from WorkflowBase)
        if not issubclass(cls, WorkflowBase):
            error(
                "<COR94314749E>",
                TypeError("`{}` does not extend `WorkflowBase`".format(cls.__name__)),
            )

        # Add attributes to the workflow class
        cls.WORKFLOW_ID = id
        cls.MODULE_ID = id  # Module ID == Workflow ID
        cls.WORKFLOW_NAME = name
        cls.MODULE_NAME = name  # Module Name == Workflow Name
        cls.WORKFLOW_VERSION = version
        cls.WORKFLOW_CLASS = cls.__module__ + "." + cls.__qualname__
        cls.PRODUCER_ID = dm.ProducerId(cls.WORKFLOW_NAME, cls.WORKFLOW_VERSION)

        # Verify UUID and add this workflow to the module and workflow registries
        current_class = model_manager.MODULE_REGISTRY.get(cls.MODULE_ID)
        if current_class is not None:
            error(
                "<COR03935755E>",
                RuntimeError(
                    "WORKFLOW_ID `{}` conflicts for classes `{}` and `{}`".format(
                        cls.MODULE_ID,
                        cls.__name__,
                        model_manager.MODULE_REGISTRY[cls.MODULE_ID].__name__,
                    )
                ),
            )
        model_manager.MODULE_REGISTRY[cls.MODULE_ID] = cls
        model_manager.WORKFLOW_REGISTRY[cls.WORKFLOW_ID] = cls

        return cls

    return workflow_decorator


class WorkflowSaver(mod.ModuleSaver):
    """A workflower saver that inherits from the module saver. Workflows should have a workflow_id
    and can directly save other modules (e.g., blocks).
    """

    def __init__(self, module, **kwargs):
        """Construct a new workflow saver.

        Args:
            module:  watson_core.module.Module
                The instance of the module to be saved.
        """
        super().__init__(**kwargs)
        if hasattr(module, "WORKFLOW_ID"):
            self.config.update(
                {
                    "name": module.WORKFLOW_NAME,
                    "version": module.WORKFLOW_VERSION,
                    "workflow_class": module.WORKFLOW_CLASS,
                    "workflow_id": module.WORKFLOW_ID,
                }
            )
        else:
            msg = "module `{}` is not a workflow.".format(module.__class__.__name__)
            log.warning("<COR80155031W>", msg)

    def save_module(self, module, relative_path):
        """Save a WatsonCore module within a workflow artifact and add a reference to the config.

        Args:
            module:  watson_core.ModuleBase
                The WatsonCore module to save as part of this workflow
            relative_path:  str
                The relative path inside of `model_path` where the block will be saved
        """
        if not issubclass(module.__class__, mod.ModuleBase):
            error(
                "<COR30664151E>",
                TypeError(
                    "`{}` does not extend `ModuleBase`".format(
                        module.__class__.__name__
                    )
                ),
            )

        rel_path, abs_path = self.add_dir(relative_path)
        # Save this module at the specified location
        module.save(abs_path)
        self.config.setdefault("module_paths", {}).update({relative_path: rel_path})
        return rel_path, abs_path

    def save_module_list(self, modules, config_key):
        """Save a list of WatsonCore modules within a workflow artifact and add a reference to the
        config.

        Args:
            modules:  dict{str -> watson_core.ModuleBase}
                A dict with module relative path as key and a WatsonCore module as value to save as
                part of this workflow
            config_key:  str
                The config key inside of `model_path` where the modules' relative path with be
                referenced

        Returns:
            list_of_rel_path: list(str)
                List of relative paths where the modules are saved
            list_of_abs_path: list(str)
                List of absolute paths where the modules are saved
        """
        # validate type of input parameters
        error.type_check("<COR44644420E>", dict, modules=modules)
        error.type_check("<COR54316176E>", str, config_key=config_key)

        list_of_rel_path = []
        list_of_abs_path = []

        # iterate through the dict and serialize the modules in its corresponding paths
        for relative_path, module in modules.items():
            if not issubclass(module.__class__, mod.ModuleBase):
                error(
                    "<COR67834055E>",
                    TypeError(
                        "`{}` does not extend `ModuleBase`".format(
                            module.__class__.__name__
                        )
                    ),
                )
            error.type_check("<COR48984754E>", str, relative_path=relative_path)

            rel_path, abs_path = self.add_dir(relative_path)

            # Save this module at the specified location
            module.save(abs_path)

            # append relative and absolute path to a list that will be returned
            list_of_rel_path.append(rel_path)
            list_of_abs_path.append(abs_path)

        # update the config with config key and list of relative path
        self.config.setdefault("module_paths", {}).update(
            {config_key: list_of_rel_path}
        )
        return list_of_rel_path, list_of_abs_path

    def save_params(self, **kwargs):
        """Save parameters in a workflow config

        Args:
            **kwargs: dict
                key-value pair of parameters to save in config.yml
        """
        self.config.update(kwargs)


class WorkflowLoader(mod.ModuleLoader):
    """A workflow loader that inherits from the module loader. Workflow loader is used to
    load internal blocks/resources and use them to instantiate a new instance of the
    module. Workflows should have a workflow_id.
    """

    def __init__(self, module, model_path):
        """Construct a new workflow loader.

        Args:
            module:  watson_core.ModuleBase
                The WatsonCore module to load as part of this workflow
            model_path:  str
                The path to the directory where the workflow is to be loaded from.
        """
        super().__init__(model_path)
        if not hasattr(module, "WORKFLOW_ID"):
            msg = "module `{}` is not a workflow.".format(module.__class__.__name__)
            log.warning("<COR88287900W>", msg)

    def load_module(self, module_paths_key, load_singleton=False):
        """Load a WatsonCore module from a workflow config.module_paths specification.

        Args:
            module_paths_key:  str
                key in `config.module_paths` looked at to load a block/resource
        """
        # Load module from a given relative path
        # Can be updated to load from a block/resource key
        if "module_paths" not in self.config:
            error(
                "<COR08580509E>", KeyError("Missing `module_paths` in workflow config!")
            )

        if module_paths_key not in self.config.module_paths:
            error(
                "<COR22069088E>",
                KeyError(
                    "Missing required {} key in config.module_paths!".format(
                        module_paths_key
                    )
                ),
            )

        module_path = os.path.join(
            self.model_path, self.config.module_paths[module_paths_key]
        )
        return watson_core.load(module_path, load_singleton=load_singleton)

    def load_module_list(self, module_paths_key):
        """Load a list of WatsonCore module from a workflow config.module_paths specification.

        Args:
            module_paths_key:  str
                key in `config.module_paths` looked at to load a list of block/resource

        Returns:
            list
                list of loaded modules
        """
        # Load module from a given relative path
        # Can be updated to load from a block/resource key
        if "module_paths" not in self.config:
            error(
                "<COR52619266E>", KeyError("Missing `module_paths` in workflow config!")
            )

        if module_paths_key not in self.config.module_paths:
            error(
                "<COR75976687E>",
                KeyError(
                    "Missing required {} key in config.module_paths!".format(
                        module_paths_key
                    )
                ),
            )

        module_list = self.config.module_paths[module_paths_key]
        error.type_check("<COR21790391E>", list, module_list=module_list)

        # Iterate through the list and load module one by one
        loaded_modules = []
        for module in module_list:
            module_path = os.path.join(self.model_path, module)
            loaded_modules.append(watson_core.load(module_path))

        return loaded_modules


class WorkflowBase(mod.ModuleBase):
    """Abstract base class for creating Workflows.  Inherits from ModuleBase."""

    @classmethod
    def load(cls, model_path, *args, **kwargs):
        """Load a new instance of workflow from a given model_path

        Args:
            model_path: str
                Path to workflow
        Returns:
            watson_core.workflows.base.WorkflowBase
                A new instance of any given implementation of WorkflowBase
        """
        return cls._load(WorkflowLoader(cls, model_path), *args, **kwargs)
