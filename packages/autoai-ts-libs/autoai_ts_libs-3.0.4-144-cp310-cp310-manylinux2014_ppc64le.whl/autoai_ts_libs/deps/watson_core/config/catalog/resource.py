# *****************************************************************#
# (C) Copyright IBM Corporation 2021.                             #
#                                                                 #
# The source code for this program is not published or otherwise  #
# divested of its trade secrets, irrespective of what has been    #
# deposited with the U.S. Copyright Office.                       #
# *****************************************************************#
"""Resource Catalog used to obtain available resources, and filter them based on qualifiers.
"""

from autoai_ts_libs.deps.watson_core.toolkit import alog, isvalidversion
from ...toolkit.errors import error_handler

from . import base
from .. import config


log = alog.use_channel("CFGGBSRSC")
error = error_handler.get(log)


class ResourceCatalog(base.BaseCatalog):
    def get_resources(self, username=None, password=None):
        """Get a dict of all known resources supported in this library version. Queries Artifactory,
        requires credentials, and may take a bit to run depending on connection speed. Also,
        retrieves aliased resources.

        Note:
            Full resource name:
            `<resource_type>_v<lib_ver>_<block_type>_<block_shortname>_lang_<lang_code>_
            <description>_<timestamp>`
                Language is optional (omit `lang_<lang_code>`)
            Alias rule/logic:
            `<resource_type>_<block_type>_<block_shortname>_<language>_<description>`
            A resource may span multiple block_type/shortname/language so they default to 'multi'
            Aliases always map to full-length resource name paths.

        Args:
            username:  str
                Applicable username to download the artifact. If None, looks for credentials from
                environment variable: ARTIFACTORY_USERNAME
            password:  str
                Applicable password to download the artifact. If None, looks for credentials from
                environment variable: ARTIFACTORY_API_KEY

        Returns:
            ResourceCatalog
                New instance of ResourceCatalog with all download-able resources.
        """
        all_resources = self._get_all_artifacts("resources", username, password)
        # resource/models in artifactory are always stored as full resource names, and many times
        # there are broken & invalid artifacts up there, so we need to create aliases from the full
        # names and filter out those invalid artifacts before returning to users a catalog
        return ResourceCatalog(
            self.alias_filter_resources(all_resources),
            self.library_version,
            self.artifact_path,
        )

    def get_alias_resources(self, username=None, password=None):
        """Get a dict of all aliased resources supported in this library version. Queries
        Artifactory, requires credentials, and may take a bit to run depending on connection speed.

        Note:
            Alias rule/logic:
            `<resource_type>_<block_type>_<block_shortname>_<language>_<description>`
            A resource may span multiple block_type/shortname/language so they default to 'multi'
            Aliases always map to full-length resource name paths.

        Args:
            username:  str
                Applicable username to download the artifact. If None, looks for credentials from
                environment variable: ARTIFACTORY_USERNAME
            password:  str
                Applicable password to download the artifact. If None, looks for credentials from
                environment variable: ARTIFACTORY_API_KEY

        Returns:
            ResourceCatalog
                New instance of ResourceCatalog with all download-able resources.
        """
        return self.get_resources(username, password).filter_non_aliased()

    def get_latest_resources(self, username=None, password=None):
        """Get a dict of all latest resources supported in this library version. Queries
        Artifactory, requires credentials, and may take a bit to run depending on connection
        speed. Does NOT return alias, returns full length resource name paths.

        Args:
            username:  str
                Applicable username to download the artifact. If None, looks for credentials from
                environment variable: ARTIFACTORY_USERNAME
            password:  str
                Applicable password to download the artifact. If None, looks for credentials from
                environment variable: ARTIFACTORY_API_KEY

        Returns:
            ResourceCatalog
                New instance of ResourceCatalog with all download-able resources.
        """
        return self.get_resources(username, password).filter_non_latest()

    def filter_non_aliased(self):
        """Filter resource catalog to only return aliased resources.

        Returns:
            ResourceCatalog
                New instance of ResourceCatalog with resources in accordance with the filter.
        """
        # resource name being separated by three underscores means it's a short name
        return ResourceCatalog(
            {name: path for name, path in self.items() if self.is_aliased(name)},
            self.library_version,
            self.artifact_path,
        )

    def filter_non_latest(self):
        """Filter resource catalog to only return latest, full-name resources.

        Returns:
            ResourceCatalog
                New instance of ResourceCatalog with resources in accordance with the filter.
        """
        return ResourceCatalog(
            self._filter_non_latest(self.filter_non_aliased()),
            self.library_version,
            self.artifact_path,
        )

    def filter_by_resource_type(self, *resource_types):
        """Filter resource catalog by resource_type (as implemented in watson_nlp)

        Args:
            resource_types: str
                The (hyphen-separated) resource_type(s) of the resource you wish to get

        Example:
            resource_catalog = watson_core.get_resources()
            resource_catalog.filter_by_resource_type('file')

        Returns:
            ResourceCatalog
                New instance of ResourceCatalog with resources in accordance with the filter.
        """
        return ResourceCatalog(
            self._filter_begin(*resource_types),
            self.library_version,
            self.artifact_path,
        )

    def filter_by_resource_shortname(self, *resource_shortnames):
        """Filter resources by resource shortname(s).

        Args:
            resource_shortnames:  str
                Name(s) (possibly shortened, hyphen-separated) for the block(s) that are relevant to
                the a resource

        Example:
            resource_catalog = watson_core.get_resources()
            resource_catalog.filter_by_resource_shortname('path')

        Returns:
            ResourceCatalog
                New instance of ResourceCatalog with resources in accordance with the filter.

        """
        return ResourceCatalog(
            self._filter_inner(*resource_shortnames),
            self.library_version,
            self.artifact_path,
        )

    def filter_by_block_type(self, *block_types):
        """Filter resources by block type(s).

        Args:
            block_types:  str
                The (hyphen-separated) block_type(s) of the block(s) that are relevant to the
                resource

        Example:
            resource_catalog = watson_core.get_resources()
            resource_catalog.filter_by_block_type('entity-mentions')

        Returns:
            ResourceCatalog
                New instance of ResourceCatalog with resources in accordance with the filter.
        """
        return ResourceCatalog(
            self._filter_inner(*block_types), self.library_version, self.artifact_path
        )

    def filter_by_block_shortname(self, *block_shortnames):
        """Filter resources by block shortname(s).

        Args:
            block_shortnames:  str
                Name(s) (possibly shortened, hyphen-separated) for the block(s) that are relevant to
                the a resource

        Example:
            resource_catalog = watson_core.get_resources()
            resource_catalog.filter_by_block_shortname('alchemy-disambig')

        Returns:
            ResourceCatalog
                New instance of ResourceCatalog with resources in accordance with the filter.

        """
        return ResourceCatalog(
            self._filter_inner(*block_shortnames),
            self.library_version,
            self.artifact_path,
        )

    def filter_by_language(self, *languages):
        """Filter resources by resource language(s).

        Args:
            languages:  str
                Language code(s) for the resource(s) (should be omitted for multi-lingual
                resources) you want to get.

        Example:
            resource_catalog = watson_core.get_resources()
            resource_catalog.filter_by_language('zh-cn')

        Returns:
            ResourceCatalog
                New instance of ResourceCatalog with resources in accordance with the filter.
        """
        return ResourceCatalog(
            self._filter_inner(*languages), self.library_version, self.artifact_path
        )

    def filter_by_library_version(self, *library_versions):
        """Filter resources by version(s) of the configured library. Requires non-aliased keys

        Args:
            library_version:  str
                The library version(s) (SemVer) that trained/uploaded the resource(s) you wish to
                get.

        Example:
            resource_catalog = watson_core.get_resources()
            resource_catalog.filter_by_library_version('0.0.5')

        Returns:
            ResourceCatalog
                New instance of ResourceCatalog with resources in accordance with the filter.
        """
        return ResourceCatalog(
            self._filter_inner(
                *library_versions, formatter=lambda ver: "v" + ver.replace(".", "-")
            ),
            self.library_version,
            self.artifact_path,
        )

    def filter_by_resource_description(self, *descriptions):
        """Filter resources by resource description(s).

        Args:
            descriptions:  str
                Short, human-readable description(s) of the resource(s) you want to get.

        Example:
            resource_catalog = watson_core.get_resources()
            resource_catalog.filter_by_resource_description('stock')

        Returns:
            ResourceCatalog
                New instance of ResourceCatalog with resources in accordance with the filter.
        """
        return ResourceCatalog(
            self._filter_end(*descriptions), self.library_version, self.artifact_path
        )

    @staticmethod
    def _split_resource_key(resource_key):
        """Return a dict of resource name split into each of its component parts. Internal use only.

        Args:
            resource_key: str
                Resource name obtained from dict to be split into components

        Returns:
            dict or None
            {
                'resource_type': resource_type,
                'library_version': library_version,
                'block_type': block_type,
                'block_shortname': block_shortname,
                'language': language,
                'description': description,
                'timestamp': timestamp
            }
            Function gives best effort and returns all it can. User can decide if resource name is
                invalid or not based on return.

        """
        error.type_check("<COR53460717E>", str, resource_key=resource_key)
        split_resource = resource_key.split("_")

        # 1) resource-type
        resource_type = split_resource.pop(0) if split_resource else None

        # 2) resource-shortname
        resource_shortname = split_resource.pop(0) if split_resource else None

        # 3) library-version (not present in alias)
        library_version = (
            ".".join(split_resource.pop(0).lstrip("v").split("-"))
            if split_resource and not ResourceCatalog.is_aliased(resource_key)
            else None
        )

        # 4) timestamp (last in list)
        timestamp = None
        if split_resource:
            timestamp_split = split_resource.pop().split("-")
            timestamp = base._get_timestamp(timestamp_split)

        # 5) description (second last)
        description = split_resource.pop() if split_resource else None

        # 6) language (lang_<lang_code>)
        language = None
        if len(split_resource) >= 2 and split_resource[-2] == "lang":
            language = split_resource.pop()
            split_resource.pop()  # Pop 'lang' from split list

        # 7) block-type
        block_type = split_resource.pop(0) if split_resource else None

        # 8) block_shortname
        block_shortname = split_resource.pop(0) if split_resource else None

        return {
            "resource_type": resource_type,
            "resource_shortname": resource_shortname,
            "library_version": library_version,
            "block_type": block_type,
            "block_shortname": block_shortname,
            "language": language,
            "description": description,
            "timestamp": timestamp,
        }

    @staticmethod
    def _check_valid_resource(resource_dict):
        """Check whether all required attributes are present from a resource_dict (as obtained
        from _split_resource_key
        """
        return (
            resource_dict["resource_type"]
            and resource_dict["resource_shortname"]
            and isvalidversion(resource_dict["library_version"])
            and resource_dict["timestamp"]
            and resource_dict["description"]
        )

    def alias_filter_resources(self, resources):
        """Get all the names (aliased included) of resources one can download. Always defaults to
        latest available. Also, filter non-valid names.

        Note:
            Full resource name:
            `<resource_type>_<resource_shortname>_v<lib_ver>_<block_type>_<block_shortname>_lang_
            <lang_code>_
            <description>_<timestamp>`
                Language is optional (omit `lang_<lang_code>`)
            Alias rule/logic:
            `<resource_type>_<resource_shortname>_<block_type>_<block_shortname>_<language>_
            <description>`
            A resource may span multiple block_type/shortname/language so they default to 'multi'
            Aliases always map to full-length resource name paths.

        Args:
            resources:  dict
                Key is the full resource name and the value is the URL to its .zip location in
                Artifactory.

        Returns:
            dict
                Same dict as input arg resources with:
                    1) incorrect/invalid names removed
                    2) aliased names added

        Note:
            This function is required to do two things:
            1. Filter out invalid resources or ones that should not be able to downloaded by this
            library version.
            2. Create the alias names to map to, essentially, latest for that
            resource_Type, block_type and block_shortname. It will be clear which long-version
            name of the resource is being downloaded from the value in the dict, where the alias is
            the key.
        """
        error.type_check("<COR50327132E>", dict, resources=resources)

        filtered_resources = resources.copy()
        for resource, _resource_url in resources.items():
            log.debug("For resource: {}".format(resource))
            resource_dict = self._split_resource_key(resource)
            if not self._check_valid_resource(resource_dict):
                log.debug("First level invalid resource: {}".format(resource))
                # checking for alias resources
                if not isinstance(resources[resource], str):
                    log.debug(
                        "Catalog value invalid and will not be returned: %s", resource
                    )
                    filtered_resources.pop(resource)
                    continue
                zip_resource = resources[resource].rstrip(".zip").split("/")[-1]
                resource_dict = self._split_resource_key(zip_resource)

                # if it is NOT a "valid" name AND it points to an "invalid" resource, assume it is
                #  NOT an alias name and SHOULD be removed
                if not self._check_valid_resource(resource_dict):
                    log.debug(
                        "Invalid zip resource found and will not be returned: %s",
                        resource,
                    )
                    filtered_resources.pop(resource)

                # skip any further operations on "invalid" resource names
                continue

            # NOTE: we can assume at this point the resource name is "valid"
            log.debug("Resource %s is considered valid", resource)

            resource_version = resource_dict["library_version"]
            # filter out resources that are too new for this library version; enforce version-ing
            resource_version_is_newer = config.compare_versions(
                resource_version, self.library_version
            )

            if resource_version_is_newer == 1:
                # resource is too new for library version of library!
                log.debug(
                    "Resource %s requires library version >= %s",
                    resource,
                    resource_version,
                )
                filtered_resources.pop(resource)
                continue

            alias_name_list = [
                resource_dict["resource_type"],
                resource_dict["resource_shortname"],
                resource_dict["block_type"] or "multi",
                resource_dict["block_shortname"] or "multi",
                resource_dict["language"] or "multi",
                resource_dict["description"],
            ]
            alias_name = "_".join(alias_name_list)
            log.debug("Resource %s has alias %s", resource, alias_name)

            # check against previous alias if exists
            if alias_name in filtered_resources:
                other_name_obj = self._split_resource_key(
                    filtered_resources[alias_name].split("/")[-1].rstrip(".zip")
                )

                if (
                    other_name_obj.get("library_version") is None
                    or resource_dict.get("library_version") is None
                ):
                    continue

                this_is_newer = base.BaseCatalog.compare_module_versions(
                    resource_dict, other_name_obj
                )
                # should never have two resources that are equal versions
                assert (
                    this_is_newer != 0
                ), "Two resources are exactly the same version! This: {0}".format(
                    resource
                )

                if this_is_newer == 1:
                    filtered_resources[alias_name] = resources[resource]
            else:
                filtered_resources[alias_name] = resources[resource]

        return filtered_resources

    @staticmethod
    def is_aliased(key):
        """Check whether a resource key is already aliased

        Notes:
            Alias rule/logic:
            `<resource_type>_<resource_shortname>_<block_type>_<block_shortname>_<language>_
            <description>`
            A resource may span multiple block_type/shortname/language so they default to 'multi'

        Returns:
            boolean
                True if resource key name is already aliased, False otherwise
        """
        return len(key.split("_")) == 6
