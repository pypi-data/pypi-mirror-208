from datetime import timedelta
from github import Github
from github.ContentFile import ContentFile
from github.Repository import Repository
from hdsr_pygithub import exceptions
from hdsr_pygithub.constants import BASE_DIR
from hdsr_pygithub.downloader.file import GithubFileDownloader
from hdsr_pygithub.tests.utils import _remove_dir_recursively
from pathlib import Path

import pytest


def test_file_does_not_exist():
    repo_name = "startenddate"
    target_file = Path("xxx")
    with pytest.raises(exceptions.GithubFileNotFoundError):
        GithubFileDownloader(repo_name=repo_name, target_file=target_file)


def test_file_too_old():
    repo_name = "startenddate"
    target_file = Path("data/output/results/mwm_peilschalen_short.csv")
    short_timedelta = timedelta(minutes=1)  # the file is too old for sure
    with pytest.raises(exceptions.GithubFileTooOldError):
        GithubFileDownloader(
            repo_name=repo_name, target_file=target_file, allowed_period_no_updates=short_timedelta,
        )


def test_file_works():
    repo_name = "startenddate"
    target_file = Path("data/output/results/mwm_peilschalen_short.csv")
    downloader = GithubFileDownloader(repo_name=repo_name, target_file=target_file)

    # test github instance
    assert isinstance(downloader.github_instance, Github)

    # test repo
    assert isinstance(downloader.repo_instance, Repository)
    assert downloader.repo_instance.name == repo_name

    # test target_file
    assert downloader.target_file == target_file

    # test target_file content
    assert isinstance(downloader.downloadable_content, ContentFile)
    assert downloader.downloadable_content.name == target_file.name
    assert downloader.downloadable_content.content


def test_download_url():
    repo_name = "startenddate"
    target_file = Path("data/output/results/mwm_peilschalen_short.csv")
    downloader = GithubFileDownloader(repo_name=repo_name, target_file=target_file)

    # test download_url exists
    url = downloader.get_download_url()
    assert url and isinstance(url, str)


def test_file_download_to_no_tmp_dir():
    repo_name = "startenddate"
    target_file = Path("data/output/results/mwm_peilschalen_short.csv")
    downloader = GithubFileDownloader(repo_name=repo_name, target_file=target_file)

    download_directory = downloader.download_files(use_tmp_dir=False, download_directory=BASE_DIR / "remove_this_dir1")
    assert download_directory.is_dir()
    downloaded_file_path = download_directory / target_file
    assert downloaded_file_path.exists()
    assert downloaded_file_path.lstat().st_size > 10  # ensure > 10 kb
    _remove_dir_recursively(dir_path=download_directory)


def test_file_download_to_tmp_dir():
    repo_name = "startenddate"
    target_file = Path("data/output/results/mwm_peilschalen_short.csv")
    downloader = GithubFileDownloader(repo_name=repo_name, target_file=target_file)

    tmp_dir = downloader.download_files(use_tmp_dir=True)
    assert tmp_dir.is_dir()

    downloaded_file_path = tmp_dir / target_file
    assert downloaded_file_path.exists()
    assert downloaded_file_path.lstat().st_size > 10  # ensure > 10 kb
    # no need to delete but we don't want to wait for Windows to clean it
    _remove_dir_recursively(dir_path=tmp_dir)


def test_wis_config_large():
    github_downloader = GithubFileDownloader(
        target_file=Path("FEWS/Config/ModuleConfigFiles/Verdamping/GFGProfilePLGB.xml"),
        allowed_period_no_updates=timedelta(weeks=52 * 2),
        repo_name="FEWS-WIS_HKV",
        branch_name="productie",
        repo_organisation="hdsr-mid",
    )
    download_directory = github_downloader.download_files(use_tmp_dir=True)
    _remove_dir_recursively(dir_path=download_directory)
