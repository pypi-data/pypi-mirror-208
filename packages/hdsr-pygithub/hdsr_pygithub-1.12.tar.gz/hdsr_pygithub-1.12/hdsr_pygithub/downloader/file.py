from datetime import timezone
from github.ContentFile import ContentFile
from hdsr_pygithub import exceptions
from hdsr_pygithub.downloader.base import GithubDownloaderBase
from pathlib import Path

import datetime
import logging


logger = logging.getLogger(__name__)


class GithubFileDownloader(GithubDownloaderBase):
    """A wrapper around https://github.com/PyGithub/PyGithub. It uses a read-only github account
    token for interacting with hdsr github repos (see README.md)."""

    def __init__(self, target_file: Path, **kwargs) -> None:
        super().__init__(**kwargs)
        self.target_file = target_file
        self._content_file = None
        self.validate_constructor()

    def validate_constructor(self) -> None:
        assert isinstance(self.target_file, Path), f"target_file {self.target_file} must be a Path"
        self.__check_target_file_is_recent_enough()

    def get_download_url(self) -> str:
        return self.downloadable_content.download_url

    @property
    def downloadable_content(self) -> ContentFile:
        if self._content_file is not None:
            return self._content_file
        repo_root_dir = Path("")
        dir_paths, content_files = self._get_branch_absolute_paths(start_dir=repo_root_dir)
        self._content_file = self._find_content_file(repo_content_files=content_files, content_file=self.target_file)
        return self._content_file

    def __check_target_file_is_recent_enough(self) -> None:
        """It is considered good practice to always check if the github file is not too old: just check last
        commit date."""
        last_modified_date = self._get_file_last_modified_date(file_content=self.downloadable_content)
        period_file_not_updated = datetime.datetime.now(timezone.utc) - last_modified_date.astimezone(timezone.utc)
        if period_file_not_updated > self.allowed_period_no_updates:
            msg = (
                f"Github file (name={self.downloadable_content}) is too old. "
                f"\n File is {period_file_not_updated.days} days not updated, while allowed is "
                f"{self.allowed_period_no_updates.days} days: {self.downloadable_content}"
            )
            raise exceptions.GithubFileTooOldError(msg=msg)
        logger.info(
            f"github file ({self.downloadable_content}) is recent enough: not updated for "
            f"{period_file_not_updated.days} days while max allowed is "
            f"{self.allowed_period_no_updates.days} days"
        )
