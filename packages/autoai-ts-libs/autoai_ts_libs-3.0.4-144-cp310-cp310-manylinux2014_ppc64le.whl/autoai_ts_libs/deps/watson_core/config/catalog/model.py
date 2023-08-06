# *****************************************************************#
# (C) Copyright IBM Corporation 2021.                             #
#                                                                 #
# The source code for this program is not published or otherwise  #
# divested of its trade secrets, irrespective of what has been    #
# deposited with the U.S. Copyright Office.                       #
# *****************************************************************#

from autoai_ts_libs.deps.watson_core.toolkit import alog
from re import match
from ...toolkit.errors import error_handler
from . import base
from .. import config


log = alog.use_channel("CFGGBSMDL")
error = error_handler.get(log)


class ModelCatalog(base.BaseCatalog):
    """Catalog of models available for download."""

    def get_models(self, username=None, password=None):
        """Get a dict of all known models supported in this library version. Queries model store,
        requires credentials, and may take a bit to run depending on connection speed. Also,
        retrieves aliased models.

        Note:
            Alias rule/logic: `<block_type>_<block_shortname>_<language>_<description>`
            And aliases always map to full-length model name paths.

        Args:
            username:  str
                Applicable username to download the artifact. If None, looks for credentials from
                environment variable: ARTIFACTORY_USERNAME
            password:  str
                Applicable password to download the artifact. If None, looks for credentials from
                environment variable: ARTIFACTORY_API_KEY

        Returns:
            ModelCatalog
                New instance of ModelCatalog with all download-able models.
        """
        all_models = self._get_all_artifacts("blocks", username, password)
        # models in artifactory are always stored as full model names, and many times there are
        #     broken & invalid models up there, so we need to create aliases from the full names
        #     and filter out those invalid models before returning to users a model catalog
        all_models = self.alias_filter_models(all_models)
        return ModelCatalog(all_models, self.library_version, self.artifact_path)

    def get_alias_models(self, username=None, password=None):
        """Get a dict of all aliased models supported in this library version. Queries Artifactory,
        requires credentials, and may take a bit to run depending on connection speed.

        Note:
            Alias rule/logic: `<block_type>_<block_shortname>_<language>_<description>`
            And aliases always map to full-length model name paths.

        Args:
            username:  str
                Applicable username to download the artifact. If None, looks for credentials from
                environment variable: ARTIFACTORY_USERNAME
            password:  str
                Applicable password to download the artifact. If None, looks for credentials from
                environment variable: ARTIFACTORY_API_KEY

        Returns:
            ModelCatalog
                New instance of ModelCatalog with all latest download-able models.
        """
        return self.get_models(username, password).filter_non_aliased()

    def get_latest_models(self, username=None, password=None):
        """Get a dict of all latest models supported in this library version. Queries Artifactory,
        requires credentials, and may take a bit to run depending on connection speed. Does NOT
        return alias, returns full length model name paths.

        Args:
            username:  str
                Applicable username to download the artifact. If None, looks for credentials from
                environment variable: ARTIFACTORY_USERNAME
            password:  str
                Applicable password to download the artifact. If None, looks for credentials from
                environment variable: ARTIFACTORY_API_KEY

        Returns:
            ModelCatalog
                New instance of ModelCatalog with all latest download-able models.
        """
        return self.get_models(username, password).filter_non_latest()

    def filter_non_aliased(self):
        """Filter model catalog to only return aliased models.

        Returns:
            ModelCatalog
                New instance of ModelCatalog with models in accordance with the filter.
        """
        # model name being separated by three underscores means it's a short name
        models = {
            model_name: model_path
            for model_name, model_path in self.items()
            if len(model_name.split("_")) == 4
        }
        return ModelCatalog(models, self.library_version, self.artifact_path)

    def filter_non_latest(self):
        """Filter model catalog to only return latest, full-name models.

        Returns:
            ModelCatalog
                New instance of ModelCatalog with models in accordance with the filter.
        """
        return ModelCatalog(
            self._filter_non_latest(self.filter_non_aliased()),
            self.library_version,
            self.artifact_path,
        )

    def filter_by_block_type(self, *block_types):
        """Filter models by block type(s).

        Args:
            block_types:  str
                The (hyphen-separated) block_type(s) of the model(s) you wish to get.

        Example:
            model_catalog = watson_core.get_models()
            model_catalog.filter_by_block_type('entity-mentions')

        Returns:
            ModelCatalog
                New instance of ModelCatalog with models in accordance with the filter.
        """
        return ModelCatalog(
            self._filter_begin(*block_types), self.library_version, self.artifact_path
        )

    def filter_by_block_shortname(self, *block_shortnames):
        """Filter models by block shortname(s).

        Args:
            block_shortnames:  str
                Name(s) (possibly shortened, hyphen-separated) for the block(s) that trained the
                model(s) you wish to get.

        Example:
            model_catalog = watson_core.get_models()
            model_catalog.filter_by_block_shortname('alchemy-disambig')

        Returns:
            ModelCatalog
                New instance of ModelCatalog with models in accordance with the filter.
        """
        return ModelCatalog(
            self._filter_inner(*block_shortnames),
            self.library_version,
            self.artifact_path,
        )

    def filter_by_model_language(self, *model_languages):
        """Filter models by model language(s).

        Args:
            model_languages:  str
                Language code(s) for the model(s) (should be omitted for multi-lingual models) you
                want to get.

        Example:
            model_catalog = watson_core.get_models()
            model_catalog.filter_by_model_language('zh-cn')

        Returns:
            ModelCatalog
                New instance of ModelCatalog with models in accordance with the filter.
        """
        return ModelCatalog(
            self._filter_inner(*model_languages),
            self.library_version,
            self.artifact_path,
        )

    def filter_by_library_version(self, *library_versions):
        """Filter models by version(s) of the configured library.

        Args:
            library_version:  str
                The library version(s) (SemVer) that trained/uploaded the model(s) you wish to get.

        Example:
            model_catalog = watson_core.get_models()
            model_catalog.filter_by_library_version('0.0.5')

        Returns:
            ModelCatalog
                New instance of ModelCatalog with models in accordance with the filter.
        """
        return ModelCatalog(
            self._filter_inner(
                *library_versions, formatter=lambda ver: "v" + ver.replace(".", "-")
            ),
            self.library_version,
            self.artifact_path,
        )

    def filter_by_model_description(self, *model_descriptions):
        """Filter models by model description(s).

        Args:
            model_description:  str
                Short, human-readable description(s) of the model(s) you want to get.

        Example:
            model_catalog = watson_core.get_models()
            model_catalog.filter_by_model_description('stock')

        Returns:
            ModelCatalog
                New instance of ModelCatalog with models in accordance with the filter.
        """
        return ModelCatalog(
            self._filter_end(*model_descriptions),
            self.library_version,
            self.artifact_path,
        )

    @staticmethod
    def _split_model_name(model):
        """Return a dict of model name split into each of its component parts. Internal use only.

        Args:
            model:  str
                Model name to be split into its component parts.

        Returns:
            dict or None
                Dict of each of the model name's component parts, as follows:
                {
                    'block_type': <block-type>,
                    'block_shortname': <block-shortname>,
                    'library_version': <library-version>,
                    'language': <language>,
                    'description': <description>,
                    'timestamp': <timestamp>,
                {
                Function gives best effort and returns all it can. User can decide if model name is
                invalid or not based on return.
        """
        error.type_check("<COR89833884E>", str, model=model)

        # NOTE: all the `if` checks below are present to PREVENT this function from throwing any
        #     errors.. If it CANNOT pull out `language` for example, this function should simply set
        #     it to be equal to `None`.
        split_model = model.split("_")

        # step 1: block type (required)
        block_type = None
        if split_model:
            block_type = split_model[0]

        # step 2: block shortname (required)
        block_shortname = None
        if len(split_model) > 1:
            block_shortname = split_model[1]

        # step 3: library version (required)
        library_version = None
        if len(split_model) > 2 and match(r"^v[0-9]+\-[0-9]+\-[0-9]+$", split_model[2]):
            library_version = ".".join(split_model[2].lstrip("v").split("-"))

        # step 4: language (optional)
        language = None
        if "lang_" in model:
            language_split = model.split("lang_")[-1].split("_")
            if language_split:
                language = language_split[0]

        # step 5: timestamp (required)
        timestamp = None
        if split_model:
            timestamp_split = split_model[-1].split("-")
            timestamp = base._get_timestamp(timestamp_split)

        # step 6: description (optional); last because it's harder to extract
        description = None
        if language:
            description_split = model.split("lang_" + language + "_")
            if description_split:
                description_split = description_split[-1].split("_")
                if description_split:
                    description = description_split[0]

        # Note: operate on the raw strings that are parsed into the timestamp, otherwise
        # names like 2020-04-10 will be converted to numerics and reparsed to 2020-4-10
        elif timestamp_split and timestamp:
            # If we've got a timestamp and no language, our model name will look something like
            # lang-detect_izumo_v0-0-18_stock_2020-04-10-100000. We want to take everything up to
            # the timestamp, and strip off underscores, then take the last entry when splitting at
            # underscores to get the description.
            time_substr = "-".join(timestamp_split[:3])
            description_split = model.split(time_substr)[0].strip("_").split("_")
            if description_split:
                description = description_split[-1]

        return {
            "block_type": block_type,
            "block_shortname": block_shortname,
            "library_version": library_version,
            "language": language,
            "description": description,
            "timestamp": timestamp,
        }

    @staticmethod
    def _is_model_name_valid(name_dict):
        # NOTE: bool is NEEEDED here due to Python behavior!
        return (
            bool(name_dict["block_type"])
            and bool(name_dict["block_shortname"])
            and bool(name_dict["library_version"])
            and bool(name_dict["timestamp"])
        )

    def alias_filter_models(self, models):
        """Get all the names (aliased included) of models one can download. Always defaults to
        latest available. Also, filter non-valid names.

        Note:
            Alias rule/logic: `<block_type>_<block_shortname>_<language>_<description>`
            And aliases always map to full-length model name paths.

        Args:
            models:  dict
                Key is the full model name and the value is the URL to its .zip location in
                Artifactory.

        Returns:
            dict
                Same dict as input arg models with:
                    1) incorrect/invalid names removed
                    2) aliased names added

        Note:
            This function is required to do two things:
            1. Filter out invalid models or models that should not be able to be downloaded by this
            library version.
            2. Create the alias names to map to the latest version of the model for that block_type and
            block_shortname. It will be clear which long-version name of the model is being
            downloaded from the value in the dict, where the alias is the key.
        """
        error.type_check("<COR85584002E>", dict, models=models)

        output_models = models.copy()
        for model in models:
            name_dict = ModelCatalog._split_model_name(model)

            model_ver = name_dict["library_version"]

            valid_model = ModelCatalog._is_model_name_valid(name_dict)

            if not valid_model:
                # checking for alias models
                zip_model = models[model].rstrip(".zip").split("/")[-1]
                zip_name_dict = ModelCatalog._split_model_name(zip_model)

                valid_zip_model = ModelCatalog._is_model_name_valid(zip_name_dict)

                # if it is NOT a "valid" name AND it points to an "invalid" model, assume it is NOT
                #     an alias name and SHOULD be removed
                if not valid_zip_model:
                    log.debug(
                        "Invalid zip model found and will not be returned: %s", model
                    )
                    output_models.pop(model)

                # skip any further operations on "invalid" model names
                continue

            # NOTE: we can assume at this point the model name is "valid"
            log.debug("Model %s is considered valid", model)

            # filter out models that are too new for this library version; enforce version-ing
            model_version_is_newer = config.compare_versions(
                model_ver, self.library_version
            )

            if model_version_is_newer == 1:
                # model is too new for library version of library!
                log.debug("Model %s requires library version >= %s", model, model_ver)
                output_models.pop(model)
                continue

            # join all of the fields to get alias name if the needed "optional" fields exist
            if not (
                name_dict["block_type"]
                and name_dict["block_shortname"]
                and name_dict["language"]
                and name_dict["description"]
            ):
                continue

            alias_name_list = [
                name_dict["block_type"],
                name_dict["block_shortname"],
                name_dict["language"],
                name_dict["description"],
            ]
            alias_name = "_".join(alias_name_list)
            log.debug("Model %s has alias %s", model, alias_name)

            # check against previous alias if exists
            if alias_name in output_models:
                other_name_dict = ModelCatalog._split_model_name(
                    output_models[alias_name].split("/")[-1].rstrip(".zip")
                )

                this_is_newer = base.BaseCatalog.compare_module_versions(
                    name_dict, other_name_dict
                )
                # should never have two models that are equal versions
                assert (
                    this_is_newer != 0
                ), "Two models are exactly the same version! This: {0}".format(model)

                if this_is_newer == 1:
                    output_models[alias_name] = models[model]
            else:
                output_models[alias_name] = models[model]

        return output_models
