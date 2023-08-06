"""A service for downloading artifacts."""

import os
from datetime import timedelta
from typing import Dict, List, NamedTuple, Optional

import inject
import structlog
from tenacity import Retrying, stop_after_attempt, wait_fixed

from db_contrib_tool.clients.download_client import DownloadClient, DownloadError
from db_contrib_tool.clients.file_service import FileService
from db_contrib_tool.setup_repro_env.release_models import ReleaseUrls
from db_contrib_tool.setup_repro_env.request_models import DownloadRequest
from db_contrib_tool.utils import is_windows

LOGGER = structlog.get_logger(__name__)
MAX_RETRIES = 2
RETRY_WAIT_TIME = timedelta(seconds=1).total_seconds()


class DownloadOptions(NamedTuple):
    """
    Options describing how downloads should occur.

    * download_binaries: Should the binaries be downloaded.
    * download_symbols: Should the debug symbols be downloaded.
    * download_artifacts: Should the build artifacts be downloaded.
    * download_python_venv: Should the python virtualenv be downloaded.
    * install_dir: Directory to install downloaded artifacts.
    * link_dir: Directory to link downloaded files to.
    """

    download_binaries: bool
    download_symbols: bool
    download_artifacts: bool
    download_python_venv: bool

    install_dir: str
    link_dir: str


class DownloadUrl(NamedTuple):
    """
    Wrapper for download URL and its fallback.

    * primary: Primary URL.
    * fallback: Fallback URL.
    """

    primary: str
    fallback: Optional[str] = None


class ArtifactDownloadService:
    """A service for downloading artifacts."""

    @inject.autoparams()
    def __init__(self, download_client: DownloadClient, file_service: FileService) -> None:
        """
        Initialize the service.

        :param download_client: Client to perform download actions.
        :param file_service: Client to perform filesystem actions.
        """
        self.download_client = download_client
        self.file_service = file_service
        self.is_windows = is_windows()
        self.retry_time_secs = RETRY_WAIT_TIME

    def download_and_extract(
        self,
        download_request: DownloadRequest,
        download_options: DownloadOptions,
    ) -> Optional[str]:
        """
        Download and extract artifacts from the given URLs.

        :param download_request: Details about from where artifacts to download.
        :param download_options: Details about how to download artifacts.
        :return: Directory extracted artifacts where linked to.
        """
        url_list = self.find_urls_to_download(
            download_request.evg_urls_info.urls, download_request.fallback_urls, download_options
        )
        install_dir = os.path.join(
            download_options.install_dir, download_request.evg_urls_info.evg_version_id
        )
        linked_dir = self.setup_mongodb(
            url_list,
            download_options.download_binaries,
            install_dir,
            download_options.link_dir,
            download_request.bin_suffix,
        )
        return linked_dir

    @staticmethod
    def find_urls_to_download(
        urls: Dict[str, str],
        fallback_urls: Optional[ReleaseUrls],
        download_options: DownloadOptions,
    ) -> List[DownloadUrl]:
        """
        Collect the urls to download based on the given options.

        :param urls: Known URLs.
        :param fallback_urls: Fallback URLs.
        :param download_options: Options describing which URLs to target.
        :return: List of URLs that should be downloaded.
        """
        download_list = []
        if download_options.download_binaries:
            binaries_url = urls.get("Binaries")
            if binaries_url is not None:
                download_list.append(
                    DownloadUrl(
                        primary=binaries_url,
                        fallback=fallback_urls.binary if fallback_urls is not None else None,
                    )
                )
            else:
                raise DownloadError("Binaries download requested but not URL available")

        if download_options.download_artifacts:
            artifacts_url = urls.get("Artifacts")
            if artifacts_url is not None:
                download_list.append(DownloadUrl(primary=artifacts_url))
            else:
                raise DownloadError("Evergreen artifacts download requested but not URL available")

        if download_options.download_symbols:
            symbols_url = (
                urls.get(" mongo-debugsymbols.tgz")
                or urls.get("mongo-debugsymbols.tgz")
                or urls.get(" mongo-debugsymbols.zip")
                or urls.get("mongo-debugsymbols.zip")
            )
            if symbols_url is not None:
                download_list.append(
                    DownloadUrl(
                        primary=symbols_url,
                        fallback=fallback_urls.debug_symbols if fallback_urls is not None else None,
                    )
                )
            else:
                raise DownloadError("Symbols download requested but not URL available")

        if download_options.download_python_venv:
            python_venv_url = urls.get("Python venv (see included README.txt)") or urls.get(
                "Python venv (see included venv_readme.txt)"
            )
            if python_venv_url is not None:
                download_list.append(DownloadUrl(primary=python_venv_url))
            else:
                raise DownloadError("Python venv download requested but not URL available")

        return download_list

    def setup_mongodb(
        self,
        urls: List[DownloadUrl],
        create_symlinks: bool,
        install_dir: str,
        link_dir: str,
        bin_suffix: str,
    ) -> Optional[str]:
        """
        Download artifacts from the given URLs, extract them, and create symlinks.

        :param urls: List of artifact URLs to download.
        :param create_symlinks: Should symlinks be created to downloaded artifacts.
        :param install_dir: Directory to extract artifacts to.
        :param link_dir: Directory to create symlinks in.
        :param bin_suffix: Suffix to append to symlink name.
        :return: Directory symlinks were created in.
        """
        for url in urls:
            self.download_with_retries(url, install_dir)

        if create_symlinks:
            if self.is_windows:
                LOGGER.info(
                    "Linking to install_dir on Windows; executable have to live in different "
                    "working directories to avoid DLLs for different versions clobbering each other"
                )
                link_dir = self.download_client.symlink_version(bin_suffix, install_dir, None)
            else:
                link_dir = self.download_client.symlink_version(bin_suffix, install_dir, link_dir)
            return link_dir
        return None

    def download_with_retries(self, url: DownloadUrl, install_dir: str) -> None:
        """
        Download and extract with retries.

        :param url: Primary URL to download with fallback URL.
        :param install_dir: Location to extract the contents of the downloaded URL.
        """
        retrying = Retrying(
            stop=stop_after_attempt(MAX_RETRIES),
            wait=wait_fixed(self.retry_time_secs),
            reraise=True,
        )

        try:
            retrying(self.try_download, url.primary, install_dir)
        except Exception as err:
            if url.fallback is None:
                LOGGER.error("Failed to setup from primary source...", error=err)
                raise err
            LOGGER.warning("Failed to setup from primary source, using fallback...", error=err)
            retrying(self.try_download, url.fallback, install_dir)

    def try_download(self, target_url: str, install_dir: str) -> None:
        """
        Attempt to download the given URL.

        :param target_url: URL to download.
        :param install_dir: Location to extract the contents of the downloaded URL.
        """
        tarball = self.download_client.download_from_url(target_url)
        self.download_client.extract_archive(tarball, install_dir)
        self.file_service.delete_file(tarball)
