"""Setup request models."""
from __future__ import annotations

from enum import Enum
from typing import Dict, NamedTuple, Optional

from db_contrib_tool.setup_repro_env.release_models import ReleaseUrls

BRANCH_FALLBACK = "master"


class EvgURLInfo(NamedTuple):
    """Wrapper around compile URLs with metadata."""

    urls: Dict[str, str]
    evg_version_id: str
    project_identifier: str


class RequestType(Enum):
    """
    How the mongo binaries are being requested.

    * git_commit: Get binaries from a specific commit.
    * git_branch: Get binaries from a specific git branch.
    * evg_version: Get binaries from a specific evergreen version.
    * evg_task: Get binaries from a specific evergreen task.
    * mongo_release_version: Get binaries for a release version of mongo (e.g. 4.4, 5.0, etc).
    * mongo_patch_version: Get binaries for a patch version of mongo (e.g. 4.2.18, 6.0.0-rc4, 6.1.0-alpha, etc).
    """

    GIT_COMMIT = "git_commit"
    GIT_BRANCH = "git_branch"
    EVG_VERSION = "evg_version"
    EVG_TASK = "evg_task"
    MONGO_RELEASE_VERSION = "mongo_release_version"
    MONGO_PATCH_VERSION = "mongo_patch_version"

    def __str__(self) -> str:
        """Display item as a string."""
        return self.value


class RequestTarget(NamedTuple):
    """
    Version of mongo binaries that was requested.

    * request_type: Type of the identifier.
    * identifier: Identifier used to find request.
    """

    request_type: RequestType
    identifier: str

    @classmethod
    def previous_release(cls, identifier: str) -> RequestTarget:
        """
        Build a target for either the previous LTS or Continuous release.

        :param identifier: Identifier of release to download.
        :return: Request target to download given release.
        """
        if identifier == BRANCH_FALLBACK:
            return cls(request_type=RequestType.GIT_BRANCH, identifier=identifier)
        return cls(request_type=RequestType.MONGO_RELEASE_VERSION, identifier=identifier)

    def __str__(self) -> str:
        """Display item as a string."""
        return f"{self.request_type}({self.identifier})"


class DownloadRequest(NamedTuple):
    """Class representing the request to download a repro environment."""

    bin_suffix: str
    discovery_request: RequestTarget
    evg_urls_info: EvgURLInfo
    fallback_urls: Optional[ReleaseUrls]

    def __hash__(self) -> int:
        """Return object hash value."""
        return hash(
            (
                self.evg_urls_info.evg_version_id,
                self.evg_urls_info.project_identifier,
                self.bin_suffix,
            )
        )

    def __eq__(self, other: object) -> bool:
        """Download objects are identical if evg version id, project id and name suffix are identical."""
        if isinstance(other, self.__class__):
            return (
                other.evg_urls_info.evg_version_id == self.evg_urls_info.evg_version_id
                and other.evg_urls_info.project_identifier == self.evg_urls_info.project_identifier
                and other.bin_suffix == self.bin_suffix
            )
        return False
