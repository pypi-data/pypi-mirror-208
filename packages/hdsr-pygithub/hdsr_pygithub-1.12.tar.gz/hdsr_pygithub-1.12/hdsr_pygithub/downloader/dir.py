from datetime import timezone
from github.ContentFile import ContentFile
from hdsr_pygithub import exceptions
from hdsr_pygithub.downloader.base import GithubDownloaderBase
from pathlib import Path
from typing import List

import datetime
import logging


logger = logging.getLogger(__name__)


class GithubDirDownloader(GithubDownloaderBase):
    """A wrapper around https://github.com/PyGithub/PyGithub. It uses a read-only github account
    token for interacting with hdsr github repos (see README.md)."""

    def __init__(
        self,
        target_dir: Path,
        only_these_files: List[Path] = None,
        exclude_these_files: List[Path] = None,
        only_these_extensions: List[str] = None,
        exclude_these_extensions: List[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.target_dir = target_dir
        self.only_these_files = only_these_files if only_these_files else []
        self.exclude_these_files = exclude_these_files if exclude_these_files else []
        self.only_these_extensions = only_these_extensions if only_these_extensions else []
        self.exclude_these_extensions = exclude_these_extensions if exclude_these_extensions else []
        self._target_dir_contents = None
        self.validate_constructor()

    def validate_constructor(self) -> None:
        assert isinstance(self.target_dir, Path), f"target_file {self.target_dir} must be a Path"

        if self.only_these_files or self.exclude_these_files:
            assert bool(self.only_these_files) != bool(
                self.exclude_these_files
            ), "use either 'only_files' or 'exclude_files'"
            for _list in (self.only_these_files, self.exclude_these_files):
                assert isinstance(_list, List)
                for _path in _list:
                    assert isinstance(_path, Path)

        if self.only_these_extensions or self.exclude_these_extensions:
            assert bool(self.only_these_extensions) != bool(
                self.exclude_these_extensions
            ), "use either 'only_extensions' or 'exclude_extensions'"
            for _list in (self.only_these_extensions, self.exclude_these_extensions):
                assert isinstance(_list, List)
                for extension in _list:
                    assert isinstance(extension, str)
                    assert extension.startswith("."), f"extension {extension} must start with '.'"

        self.__check_target_dir_exists()
        self.__check_target_dir_contents_recent_enough()

    @property
    def downloadable_content(self) -> List[ContentFile]:
        if self._target_dir_contents is not None:
            return self._target_dir_contents
        existing_dirs, existing_files = self._get_branch_absolute_paths(start_dir=self.target_dir)
        self._target_dir_contents = self.__filter_download_content(existing_files=existing_files)
        return self._target_dir_contents

    def __check_target_dir_exists(self):
        repo_root_dir = Path(".")
        existing_dirs, existing_files = self._get_branch_absolute_paths(start_dir=repo_root_dir)
        if self.target_dir in existing_dirs or self.target_dir == repo_root_dir:
            return
        raise exceptions.GithubDirNotFoundError(
            msg=f"dir {self.target_dir} does not exist in repo={self.repo_name}, branch={self.branch_name}"
        )

    def __check_target_dir_contents_recent_enough(self):
        """Ensure that all files in dir are updated within self.allowed_period_no_updates."""
        for file_content in self.downloadable_content:
            last_modified_date = self._get_file_last_modified_date(file_content=file_content)
            period_file_not_updated = datetime.datetime.now(timezone.utc) - last_modified_date.astimezone(timezone.utc)
            if period_file_not_updated < self.allowed_period_no_updates:
                logger.info(
                    f"github file ({file_content.name}) is recent enough: not updated for "
                    f"{period_file_not_updated.days} days while max allowed is "
                    f"{self.allowed_period_no_updates.days} days"
                )
                continue
            raise exceptions.GithubFileTooOldError(
                msg=f"Github file (name={file_content.name}) is too old. "
                f"\n File is {period_file_not_updated.days} days not updated, while allowed is "
                f"{self.allowed_period_no_updates.days} days: {file_content.html_url}"
            )

    def __filter_files(self, files: List[ContentFile]) -> List[ContentFile]:
        filtered_contents = []
        if self.only_these_files:
            only_these_files = [x.as_posix() for x in self.only_these_files]
            for content_file in files:
                if content_file.path in only_these_files or content_file.name in only_these_files:
                    filtered_contents.append(content_file)
        elif self.exclude_these_files:
            exclude_these_files = [x.as_posix() for x in self.exclude_these_files]
            for content_file in files:
                if content_file.path not in exclude_these_files and content_file.name not in exclude_these_files:
                    filtered_contents.append(content_file)
        else:
            filtered_contents = files
        return filtered_contents

    def __filter_extensions(self, files: List[ContentFile]) -> List[ContentFile]:
        filtered_contents = []
        if self.only_these_extensions:
            for content_file in files:
                if Path(content_file.name).suffix in self.only_these_extensions:
                    filtered_contents.append(content_file)
        elif self.exclude_these_extensions:
            for content_file in files:
                if Path(content_file.name).suffix not in self.exclude_these_extensions:
                    filtered_contents.append(content_file)
        else:
            filtered_contents = files
        return filtered_contents

    def __filter_download_content(self, existing_files: List[ContentFile]) -> List[ContentFile]:
        filtered_contents = self.__filter_files(files=existing_files)
        filtered_contents = self.__filter_extensions(files=filtered_contents)
        filtered_contents = list(set(filtered_contents))
        return filtered_contents
