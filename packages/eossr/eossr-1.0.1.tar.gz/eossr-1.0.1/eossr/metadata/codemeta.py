import json
from warnings import warn

import numpy as np
import pandas as pd
import pkg_resources

from ..utils import write_json
from . import valid_semver

__all__ = [
    'schema',
    'codemeta_crosswalk',
    'Codemeta',
]


def schema():
    return json.load(pkg_resources.resource_stream(__name__, 'schema/codemeta.json'))


def codemeta_crosswalk():
    return pd.read_csv(
        pkg_resources.resource_stream(__name__, 'schema/escape_codemeta_crosswalk.csv'), comment='#', delimiter=';'
    )


class CodemetaRequiredError(KeyError):
    counter = 0

    def __init__(self, message):
        CodemetaRequiredError.counter += 1


class CodemetaRecommendedWarning(Warning):
    counter = 0

    def __init__(self, message):
        CodemetaRecommendedWarning.counter += 1


class Codemeta:
    def __init__(self, metadata: dict):
        self.metadata = metadata
        self._crosswalk_table = None

    @classmethod
    def from_file(cls, codemeta_filename):
        """Load `codemeta_filename` into the validator"""
        with open(codemeta_filename) as infile:
            controller = cls(json.load(infile))
        return controller

    @property
    def schema(self):
        return schema()

    @property
    def crosswalk_table(self):
        if self._crosswalk_table is None:
            self._crosswalk_table = codemeta_crosswalk()
        return self._crosswalk_table

    def missing_keys(self, level='required'):
        """
        Return the list of keys that are required but not present in the metadata
        level: str
            'required' or 'recommended'
        """
        required_mask = self.crosswalk_table['OSSR Requirement Level'] == level
        keys = np.array(list(self.metadata.keys()))
        required_keys = self.crosswalk_table['Property'][required_mask].values
        missing_keys = required_keys[np.in1d(required_keys, keys, invert=True)]
        return missing_keys

    def validate(self):
        """Validate the metadata against the CodeMeta schema
        Raises errors for required keys and warnings for recommended keys
        """
        if self.missing_keys('required').size > 0:
            raise CodemetaRequiredError(
                f"Missing {self.missing_keys('required').size} required keys: " f"{self.missing_keys('required')}"
            )
        else:
            if self.missing_keys('recommended').size > 0:
                warn(
                    f"Missing {self.missing_keys('recommended').size} recommended keys: "
                    f"{self.missing_keys('recommended')}",
                    CodemetaRecommendedWarning,
                )
            if "version" in self.metadata and not valid_semver(self.metadata["version"]):
                warn(f"Version {self.metadata['version']} does not follow the recommended format from semver.org.")
            if "softwareVersion" in self.metadata and not valid_semver(self.metadata["softwareVersion"]):
                warn(
                    f"Version {self.metadata['softwareVersion']} does not follow the recommended format from "
                    f"semver.org."
                )
            return False
        print("CodeMeta is valid")
        return True

    def write(self, path='codemeta.json', overwrite=False):
        """Write the CodeMeta file to `path`"""
        write_json(self.metadata, path, overwrite=overwrite)
