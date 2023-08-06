from abc import ABC
from abc import abstractmethod
from dateutil.parser import parse
from dotenv import load_dotenv
from github import BadCredentialsException
from github import Github
from github import UnknownObjectException
from github.Branch import Branch
from github.ContentFile import ContentFile
from github.GithubException import GithubException
from github.PaginatedList import PaginatedList
from github.Repository import Repository
from hdsr_pygithub import constants
from hdsr_pygithub import exceptions
from pathlib import Path
from typing import List
from typing import Tuple
from typing import Union

import base64
import datetime
import logging
import os
import tempfile


logger = logging.getLogger(__name__)


class GithubDownloaderBase(ABC):
    def __init__(
        self,
        repo_name: str,
        repo_organisation: str = constants.DEFAULT_GITHUB_ORGANISATION,
        branch_name: str = None,
        personal_access_token: str = None,
        secrets_env_path: Path = constants.SECRETS_ENV_PATH,
        allowed_period_no_updates: datetime.timedelta = datetime.timedelta(weeks=52),
    ) -> None:
        self.repo_name = repo_name
        self.branch_name = branch_name if branch_name else "main"
        self.allowed_period_no_updates = allowed_period_no_updates
        self.repo_organisation = repo_organisation
        self.secrets_env_path = secrets_env_path
        self._personal_access_token = personal_access_token
        logger.info(f"loading personal_access_token from .env = {not bool(personal_access_token)}")
        #
        self.content_dict = {}
        self._github_instance = None
        self._repo_instance = None
        self._content_file = None
        self._branch_commits = None
        #
        self.validate_base_constructor()

    @property
    def personal_access_token(self) -> str:
        if self._personal_access_token is not None:
            return self._personal_access_token
        secrets_env_path = self.secrets_env_path
        try:
            assert isinstance(secrets_env_path, Path), f"secrets_env_path '{secrets_env_path}' must be a pathlib.Path"
            assert secrets_env_path.is_file(), f"could not find secrets_env_path '{secrets_env_path}'"
            logger.info(f"retrieving your github personal access token from secrets_env_path '{secrets_env_path}'")
            load_dotenv(dotenv_path=secrets_env_path.as_posix())
            token = os.environ.get(constants.GITHUB_PERSONAL_ACCESS_TOKEN, None)
            assert token, (
                f"file {secrets_env_path} exists, but it must contain a row: "
                f"{constants.GITHUB_PERSONAL_ACCESS_TOKEN}=blablabla"
            )
            self._personal_access_token = token
        except Exception as err:
            msg = (
                f"could not get {constants.GITHUB_PERSONAL_ACCESS_TOKEN} from '{secrets_env_path}'. err={err}. For "
                f"info on how to create/use a token, read topic 'Token' on https://pypi.org/project/hdsr-pygithub/"
            )
            raise AssertionError(msg)
        return self._personal_access_token

    def validate_base_constructor(self) -> None:
        assert self.personal_access_token
        assert isinstance(self.allowed_period_no_updates, datetime.timedelta), (
            f"allowed_period_no_updates must be a datetime.timedelta " f"{self.allowed_period_no_updates}"
        )
        assert isinstance(self.repo_name, str) and self.repo_name, f"repo_name must be str {self.repo_name}"
        if self.repo_organisation:
            assert isinstance(self.repo_organisation, str), f"repo_organisation must be a str {self.repo_organisation}"
        available_branches = [branch.name for branch in self.repo_instance.get_branches()]
        if self.branch_name not in available_branches:
            raise exceptions.GithubBranchNotFound(msg=f"branch '{self.branch_name}' not found in {available_branches}")

    def _validate_personal_access_token(self, github_instance: Github) -> Github:
        # check 1: get user name via token
        try:
            user_url = github_instance.get_user().html_url  # noqa dont use self.user_url here to avoid recursion error
        except BadCredentialsException:
            msg = f"invalid personal_access_token {self.personal_access_token} as we cannot get user_html_url"
            raise exceptions.BadCredentialsError(msg)
        except Exception as err:
            raise AssertionError(f"code error: validate_personal_access_token, err={err}")

        # check 2: has token the correct scopes
        expected_scopes = ["repo"]
        found_scopes = github_instance.oauth_scopes
        if expected_scopes != found_scopes:
            msg = (
                f"user {user_url} has token scopes '{found_scopes}' which is not expected_scopes "
                f"'{expected_scopes}'. Please select correct scopes at github.com > select your profile "
                f"(right top corner) > settings > developer settings > personal access token > Tokens (classic) > "
                f"select your token > select only 'repo' (Full control of private repositories). This selects "
                f"automatically the related sub-selections (e.g. 'repo:status' (Access commit status)."
            )
            raise exceptions.TokenScopesError(msg)
        logger.info(f"user {user_url} has valid personal access token with correct scopes")
        return github_instance

    @property
    def user_url(self) -> str:
        """Returns e.g.: 'https://github.com/robvandenhengelhdsr' or 'https://github.com/renierkramerhdsr'."""
        return self.github_instance.get_user().html_url

    @property
    def github_instance(self) -> Github:
        if self._github_instance is not None:
            return self._github_instance
        github_instance = Github(login_or_token=self.personal_access_token)
        self._github_instance = self._validate_personal_access_token(github_instance=github_instance)
        return self._github_instance

    @property
    def repo_instance(self) -> Repository:
        if self._repo_instance is not None:
            return self._repo_instance
        repo_full_name = f"{self.repo_organisation}/{self.repo_name}" if self.repo_organisation else self.repo_name
        try:
            repo_instance = self.github_instance.get_repo(full_name_or_id=repo_full_name, lazy=False)
        except exceptions.BadCredentialsError:
            raise
        except UnknownObjectException as err:
            msg = f"can not create repo instance {repo_full_name} with user {self.user_url}."
            if self.__public_repo_works_okay():
                msg += (
                    f" However, a (test) public repo (that should work) does work. Does repo '{repo_full_name}' exist "
                    f"and does user={self.user_url} have access? err={err.__class__.__name__}: {err}"
                )
            else:
                msg += (
                    f" A (test) public repo (that should work) also does not work. "
                    f"Please check your personal access token, err={err.__class__.__name__}: {err}"
                )
            raise exceptions.GithubRepoInstanceError(msg=f"{msg}, err={err}")
        except Exception as err:
            raise AssertionError(f"code error err={err.__class__.__name__}: {err}")

        private_or_public = "private" if repo_instance.private else "public"
        logger.info(f"found {private_or_public} repo {repo_instance.html_url}")
        self._repo_instance = repo_instance
        return self._repo_instance

    @property
    def branch_instance(self) -> Branch:
        return self.repo_instance.get_branch(branch=self.branch_name)

    @property
    def branch_commits(self) -> PaginatedList:
        if self._branch_commits is not None:
            return self._branch_commits
        self._branch_commits = self.repo_instance.get_commits(sha=self.branch_name)
        return self._branch_commits

    @property
    @abstractmethod
    def downloadable_content(self) -> Union[ContentFile, List[ContentFile]]:
        raise NotImplementedError

    def _get_file_last_modified_date(self, file_content: ContentFile) -> datetime:
        """As file.last_modified (is file modification) is not the same as github_content_file.last_modified (is
        repo modification), we need to find the file in commits (within a branch) and then get the .last_modified."""
        # TODO: fix this (modified data is last commit date repo instead of commit to specific file) for repo
        #  startendate:
        #  INFO github file (ContentFile(path="data/output/results/caw_oppervlaktewater_short.csv")) is recent enough:
        #  not updated for 2 days while max allowed is 364 days
        for commit in self.branch_commits:
            for file in commit.files:
                if file_content.sha == file.sha:
                    last_modified = file.last_modified
                    return parse(last_modified)
        if file_content.last_modified:
            return parse(file_content.last_modified)
        default_last_modified_date = datetime.datetime.now() - self.allowed_period_no_updates / 2
        logger.warning(
            f"file {file_content.path} not found in commits AND it it has no last modified date."
            f"Using default_last_modified_date {default_last_modified_date}"
        )
        return default_last_modified_date

    def __public_repo_works_okay(self) -> bool:
        """In case access to a github private repo does not work, we test if access to a public repo works.
        We use the repo 'https://github.com/PyGithub/PyGithub' (the one that we use here for: 'pip install PyGithub'
        and 'from github import Github'."""
        expected_url = "https://github.com/PyGithub/PyGithub"
        try:
            github = Github(login_or_token=self.personal_access_token)
            repo_instance = github.get_repo(full_name_or_id="PyGithub/PyGithub")
            assert repo_instance.html_url == expected_url
            logger.info(f"repo instance works for public repo {expected_url}")
            return True
        except Exception:  # noqa
            logger.error(f"repo instance does not works for public repo {expected_url}")
            return False

    def __get_contents_wrapper(self, start_dir: Path, branch: str):
        """repo_instance.get_contents() can take a while so we cache all results (per start_dir-branch combo)."""
        assert isinstance(start_dir, Path) and isinstance(branch, str)
        key = start_dir.as_posix(), branch
        contents_cache = self.content_dict.get(key, None)
        if contents_cache:
            logger.debug(f"return cached repo.get_contents for path={start_dir} and ref={branch}")
            return contents_cache
        self.content_dict[key] = self.repo_instance.get_contents(path=start_dir.as_posix(), ref=branch)
        return self.content_dict[key]

    def _get_branch_absolute_paths(self, start_dir: Path) -> Tuple[List[Path], List[ContentFile]]:
        """Return tuple (_dirs, _files) of all absolute paths from repo root, e.g.:
        (
            [
                WindowsPath('data'),
                WindowsPath('startenddate'),
                WindowsPath('data/input'),
                ...
            ],
            [
                ContentFile(path=".gitignore"),
                ContentFile(path="LICENSE"),
                ContentFile(path="README.md"),
                ....
            ]
        )
        """
        dir_paths = []
        content_files = []  # get root content files
        contents = self.__get_contents_wrapper(start_dir=start_dir, branch=self.branch_name)
        while contents:
            content = contents.pop(0)
            if content.type == "dir":
                # add subdir content files
                _path = Path(content.path)
                dir_paths.append(_path)
                dir_contents = self.__get_contents_wrapper(start_dir=_path, branch=self.branch_name)
                start_dir.as_posix()
                contents.extend(dir_contents)
                continue
            if content.type == "file":
                content_files.append(content)
        return dir_paths, content_files

    def _find_content_file(self, repo_content_files: List[ContentFile], content_file: Path) -> ContentFile:
        # first, try exact match  based on whole filepath
        content_files = [x for x in repo_content_files if content_file.as_posix() in x.path]
        if len(content_files) == 1:
            content_file = content_files[0]
            logger.info(f"found exact match online: {content_file.path}")
            logger.debug(f"found file: {content_file.url} = url")
            logger.debug(f"found file: {content_file.html_url} = html_url")
            logger.debug(f"found file: {content_file.git_url} = git_url")
            logger.debug(f"found file: {content_file.download_url} = download_url")
            return content_file

        # secondly, try exact match based on filename (not path).
        content_files = [x for x in repo_content_files if x.name == content_file.name]
        if len(content_files) == 1:
            content_file = content_files[0]
            logger.info(f"found exact match online: {content_file.path}")
            logger.debug(f"found file: {content_file.url} = url")
            logger.debug(f"found file: {content_file.html_url} = html_url")
            logger.debug(f"found file: {content_file.git_url} = git_url")
            logger.debug(f"found file: {content_file.download_url} = download_url")
            return content_file

        default_error_msg = f"could not find file path {content_file} in repo {self.repo_instance.name}"
        if len(content_files) > 1:
            urls = [x.url for x in content_files]
            default_error_msg += f', found >1 files with name {content_file.name} in repo: {urls}")'
        raise exceptions.GithubFileNotFoundError(msg=default_error_msg)

    @staticmethod
    def __get_write_mode(absolute_file_path: Path, file_data: Union[bytes, str]) -> str:
        if isinstance(file_data, bytes):
            # avoid appending with 'ab' (use "r+b") as it sometimes forces all writes to happen at the end of the file
            return "r+b" if absolute_file_path.exists() else "wb"
        elif isinstance(file_data, str):
            return "a" if absolute_file_path.exists() else "w"
        raise AssertionError(f"unexpected data type {type(file_data)} for {absolute_file_path}")

    @staticmethod
    def __get_download_dir(use_tmp_dir: bool = False, download_directory: Path = None) -> Path:
        assert bool(use_tmp_dir) != bool(download_directory), (
            "either use 'use_tmp_dir' or 'download_directory'. "
            "Option use_tmp_dir=True deletes all downloaded github files at exit"
        )
        if use_tmp_dir:
            tmp_dir = tempfile.TemporaryDirectory()
            download_directory = Path(tmp_dir.name)
        else:
            assert isinstance(download_directory, Path)
            if not download_directory.is_dir():
                download_directory.mkdir(parents=True, exist_ok=True)
        return download_directory

    def __iterable_iterable_downloads(self) -> List[ContentFile]:
        if isinstance(self.downloadable_content, list):
            return self.downloadable_content
        return [self.downloadable_content]

    def __get_file_data_b64(self, content_file: ContentFile) -> bytes:
        try:
            file_data_b64 = base64.b64decode(content_file.content)
            if file_data_b64:
                return file_data_b64
        except GithubException:
            pass

        _1mb = 1000000
        if content_file.size > _1mb:
            logger.info(f"found github file > 1mb, {content_file.path}")
        try:
            # try blob (works only for blob object type)
            blob_data = self.repo_instance.get_git_blob(sha=content_file.sha)
            file_data_b64 = base64.b64decode(blob_data.content)
            return file_data_b64
        except Exception as err:
            logger.warning(f"work-around 'get_git_blob()' failed for large file {content_file.path}, err={err}")
            return b""

    def download_files(self, use_tmp_dir: bool = False, download_directory: Path = None) -> Path:
        """Download github files (and dirs) to directory while keeping the github directory structure.
        Either use 'use_tmp_dir' or 'download_directory'. The first options downloads to (a folder in) your
        Temp directory (e.g. C:/Users/<user>/AppData/Local/Temp/..).
        Windows never automatically cleans theTemp directory by default. In Windows 10 you have to enable this
        feature in Settings, and with earlier versions you must delete the files yourself or use
        programs like Disk Cleanup or cCleaner.
        Returns the path to root directory"""
        download_dir = self.__get_download_dir(use_tmp_dir=use_tmp_dir, download_directory=download_directory)
        for content_file in self.__iterable_iterable_downloads():
            relative_file_path = Path(content_file.path)
            file_dir = download_dir / relative_file_path.parent
            if not file_dir.is_dir():
                file_dir.mkdir(parents=True, exist_ok=True)
            absolute_file_path = file_dir / relative_file_path.name
            file_data_b64 = self.__get_file_data_b64(content_file=content_file)
            if not file_data_b64:
                logger.warning(f"could not decode file to base64, so skipping download {content_file.path}")
                continue
            try:
                write_mode = self.__get_write_mode(absolute_file_path=absolute_file_path, file_data=file_data_b64)
                file_out = open(file=absolute_file_path.as_posix(), mode=write_mode)
                file_out.write(file_data_b64)  # noqa
                file_out.close()
            except IOError as err:
                logging.error(f"could not download file to disk {absolute_file_path}, err={err}")
        return download_dir
