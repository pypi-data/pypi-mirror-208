# *****************************************************************#
# (C) Copyright IBM Corporation 2021.                             #
#                                                                 #
# The source code for this program is not published or otherwise  #
# divested of its trade secrets, irrespective of what has been    #
# deposited with the U.S. Copyright Office.                       #
# *****************************************************************#
"""BaseCatalog has helper methods for Model/Resource catalog serves as base class for both.
"""

import os
import json

from autoai_ts_libs.deps.watson_core.toolkit import alog, WebClient
from autoai_ts_libs.deps.watson_core.toolkit.errors import error_handler
from autoai_ts_libs.deps.watson_core.config import config



log = alog.use_channel("CFGGBASE")
error = error_handler.get(log)


class BaseCatalog(dict):
    """Catalog of models/resources available for download."""

    def __init__(self, artifacts, library_version, artifact_path):
        """Initialize a catalog.

        Args:
            artifacts/models/workflows/resources:  dict
                Keys are model names, values are path in artifactory.
            library_version:  str
                Version of library using this catalog (SemVer).
            artifact_path:  str
                Specific format of base url, per:
                https://www.jfrog.com/confluence/display/RTF/Artifactory+REST+API
        """
        error.type_check("<COR24780634E>", dict, artifacts=artifacts)

        self.library_version = library_version
        self.artifact_path = artifact_path
        super().__init__(artifacts)

    def get_models(self, *args, **kwargs):
        raise NotImplementedError("Not available in this catalog.")

    def get_workflows(self, *args, **kwargs):
        raise NotImplementedError("Not available in this catalog.")

    def get_resources(self, *args, **kwargs):
        raise NotImplementedError("Not available in this catalog.")

    def _filter_non_latest(self, aliased_artifacts):
        """Filter model/resource catalog to only return latest, full-name resources.

        Returns:
            dict
                Dictionary which can be used to initialize a new catalog with filtered artifacts
        """
        # can get latest by:
        #     1) extracting artifact names from what the aliases point to
        #     2) setting those artifact names as the new keys
        artifacts = {}

        for artifact in aliased_artifacts:
            # step 1: get artifact name of zip to which it points
            zip_artifact = aliased_artifacts[artifact].rstrip(".zip").split("/")[-1]

            # step 2: set as key to same value
            artifacts[zip_artifact] = aliased_artifacts[artifact]

        return artifacts

    @staticmethod
    def _item_in_iterable_filter(to_filter, appearance_list):
        """Keep items in to_filter if any elements from appearance_list are "in" that item.

        Args:
            to_filter:  list
                List to be filtered and returned. Iterate over it and if a given item appears in one
                of the elements of `appearance_list`, then remove it.
            appearance_list:  list
                List that contains values that should be used to filter the items in to_filter.
                E.g. _item_in_iterable_filter(['bcd'], ['ab', 'bc']) == ['ab']
        """
        return [
            item for item in to_filter if any(val in item for val in appearance_list)
        ]

    @staticmethod
    def _key_in_iterable_filter(to_filter, appearance_list):
        """Keep entries in to_filter if key from that entry is "in" appearance_list.

        Args:
            to_filter:  dict
                Dict to be filtered and returned. Iterate over its keys and if a given key equals
                one of the elements of `appearance_list`, then remove it.
            appearance_list:  list
                List that contains values that should be used to filter the items in to_filter.
                E.g. _key_in_iterable_filter({'ab': 0, 'bc': 1}, ['ab']) == {'bc': 1}
        """
        return {key: val for key, val in to_filter.items() if key in appearance_list}

    @classmethod
    def compare_module_versions(cls, this, other):
        """Return 1, 0, or -1 depending on if `this` is a newer, equal, or older model than `other`.

        Args:
            this:  dict
                Looks for key:
                    - "library_version" which contains a SemVer string of the library: major,
                    minor, and patch versions.
                    - "timestamp" which contains a length 4 tuple of ints which correspond to: year,
                    month, day, and time.
            other:  dict
                Looks for key:
                    - "library_version" which contains a SemVer string of the library: major,
                    minor, and patch versions.
                    - "timestamp" which contains a length 4 tuple of ints which correspond to: year,
                    month, day, and time.

        Returns:
            int
                1 if `this` is a newer model than `other`, -1 if older, and 0 if equal
        """
        # method defaults to not replacing - no harm done; pass onto model train time
        this_is_newer_version = config.compare_versions(
            this["library_version"], other["library_version"]
        )

        # if 0, the versions are equal; means we should continue in checking
        if this_is_newer_version != 0:
            return this_is_newer_version

        # NOTE: only moves onto train time if library versions are equal

        # if same library versions, check train time of model
        this_year, this_month, this_day, this_time = this["timestamp"]
        other_year, other_month, other_day, other_time = other["timestamp"]

        # year
        if this_year > other_year:
            return 1
        if this_year < other_year:
            return -1
        # else => they are equal years

        # month
        if this_month > other_month:
            return 1
        if this_month < other_month:
            return -1
        # else => they are equal months

        # day
        if this_day > other_day:
            return 1
        if this_day < other_day:
            return -1
        # else => they are equal months

        # time
        if this_time > other_time:
            return 1
        if this_time < other_time:
            return -1
        # else => they are equal times

        # they are equal
        return 0

    def _filter_begin(self, *values, formatter=lambda val: val):
        """Filter catalog dictionary keys if it starts with a value in values. e.g.
        for models, `block_type` is checked with `value_` ('_' is added if it doesn't exist)

        Args:
            *values: string(s)
                Value(s) to filter on
            formatter: func
                Function to wrap around on each string value in values. Needs to be provided as a
                keyword argument since values are an unbounded list of arguments

        Returns:
            dict
                Dictionary which can be used to initialize a new catalog
        """
        error.type_check_all("<COR26481622E>", str, values=values)
        error.value_check("<COR83538502E>", values, "`values` must be nonempty")
        return self._filter(
            [self._with_pad(formatter(value), False, True) for value in values]
        )

    def _filter_inner(self, *values, formatter=lambda val: val):
        """Filter catalog dictionary keys if it contains a value in values. e.g.
        for models, `block_shortname` is checked with `_value_` ('_' is added if it doesn't exist)

        Args:
            *values: string(s)
                Value(s) to filter on
            formatter: func
                Function to wrap around on each string value in values. Needs to be provided as a
                keyword argument since values are an unbounded list of arguments

        Returns:
            dict
                Dictionary which can be used to initialize a new catalog
        """
        error.type_check_all("<COR74553679E>", str, values=values)
        error.value_check("<COR94970856E>", values, "`values` must be nonempty")
        return self._filter(
            [self._with_pad(formatter(value), True, True) for value in values]
        )

    def _filter_end(self, *values, formatter=lambda val: val):
        """Filter catalog dictionary keys if it ends with a value in values. e.g.
        for models, `timestamp` is checked with `value_` ('_' is added if it doesn't exist)

        Args:
            *values: string(s)
                Value(s) to filter on
            formatter: func
                Function to wrap around on each string value in values. Needs to be provided as a
                keyword argument since values are an unbounded list of arguments

        Returns:
            dict
                Dictionary which can be used to initialize a new catalog
        """
        error.type_check_all("<COR28138344E>", str, values=values)
        error.value_check("<COR42144240E>", values, "`values` must be nonempty")
        return self._filter(
            [self._with_pad(formatter(value), True, False) for value in values]
        )

    @staticmethod
    def _with_pad(value, begin=False, end=False):
        """Add _ at the beginning or end for a given value, used to filter keys"""
        value = "_" + value if begin and not value.startswith("_") else value
        value = value + "_" if end and not value.endswith("_") else value
        return value

    def _filter(self, values):
        """Find all available matching values and return a dictionary of filtered key, value pairs
        which can be used to initialize a new catalog type
        """
        filtered_values = self._item_in_iterable_filter(self, values)
        return self._key_in_iterable_filter(self, filtered_values)

    def _get_all_artifacts(self, artifact_subpath, username=None, password=None):
        """Base method to get list of all artifacts stored in artifactory. Root URL obtained from
        config.yml.

        Args:
            artifact_subpath:  str
                subpath appended to root artifactory URL to fetch list of artifacts/models/resources
            username:  str
                Username (ARTIFACTORY_USERNAME) used for authentication
            password:  str
                Password (ARTIFACTORY_API_KEY) used for authentication

        Returns:
            dict
                Dictionary with artifact keys (basename) and associated full URLs
        """
        username, password = config.get_credentials_or_default(username, password)

        # model storage location logic -- assumed to be in '{artifact_subpath}/'
        # ex:
        #   https://na-blue.artifactory.swg-devops.com/artifactory/api/storage/wcp-nlu-team-one-nlp-models-generic-local/0.0.2?list&deep=1
        artifact_subpath = artifact_subpath.strip("/")
        list_artifacts_url = (
            self.artifact_path + "/" + artifact_subpath + "/?list&deep=1"
        )
        log.debug("Fetching artifacts from Artifactory URL: %s", list_artifacts_url)

        response, _ = WebClient.request(list_artifacts_url, username, password)
        with response as rp:
            json_response = json.loads(
                rp.read().decode(response.info().get_param("charset") or "utf-8")
            )

        # get all files and remove path and extensions;
        #    file['uri'] starts with a '/' which is why this works
        # NOTE: .replace(...) because of the base path
        #     --> this is more sustainable than the other way around
        all_artifacts = {
            os.path.basename(file["uri"]).split(".")[0]: self.artifact_path.replace(
                "/artifactory/api/storage/", "/artifactory/"
            )
            + artifact_subpath
            + "/"
            + file["uri"].strip("/")
            for file in json_response["files"]
        }
        log.debug("Fetched the following [potential] artifacts: %s", all_artifacts)

        return all_artifacts


def _get_timestamp(timestamp_split):
    # [4, 2, 2, 6] are the lengths of the encoding of the train time for, respectively:
    #     year, month, day, hours/minutes/seconds
    timestamp = None
    if len(timestamp_split) == 4 and [len(_time) for _time in timestamp_split] == [
        4,
        2,
        2,
        6,
    ]:
        timestamp = tuple(int(_time) for _time in timestamp_split)
    return timestamp
