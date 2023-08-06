from hdsr_pygithub import exceptions
from hdsr_pygithub import GithubFileDownloader
from hdsr_pygithub.downloader.base import GithubDownloaderBase
from pathlib import Path

import datetime
import pytest


def test_wrong_token():
    repo_name = "startenddate"
    target_file = Path("data/output/results/mwm_peilschalen_short.csv")
    with pytest.raises(exceptions.BadCredentialsError):
        GithubFileDownloader(repo_name=repo_name, target_file=target_file, personal_access_token="xxx")


def test_repo_does_not_exist():
    repo_name = "xxx"
    target_file = Path("xxx")
    with pytest.raises(exceptions.GithubRepoInstanceError):
        GithubFileDownloader(repo_name=repo_name, target_file=target_file)


def test_not_main_branch_works():
    repo_name = "FEWS-WIS_HKV"
    file = Path("FEWS/Config/IdMapFiles/IdOPVLWATER.xml")
    for branch_name in ("productie", "test"):
        downloader = GithubFileDownloader(repo_name=repo_name, target_file=file, branch_name=branch_name)
        expected = f"https://api.github.com/repos/hdsr-mid/{repo_name}/contents/{file.as_posix()}?ref={branch_name}"
        assert downloader.downloadable_content.url == expected


def test_avoid_instance_base_class():
    repo_name = "FEWS-WIS_HKV"
    with pytest.raises(TypeError):
        GithubDownloaderBase(repo_name=repo_name)


def test_user_url():
    downloader = GithubFileDownloader(
        repo_name="startenddate",
        repo_organisation="hdsr-mid",
        target_file=Path("data/output/results/mwm_peilschalen_short.csv"),
        branch_name="main",
        allowed_period_no_updates=datetime.timedelta(days=356 * 30),
    )
    assert isinstance(downloader.user_url, str) and downloader.user_url


def test_repo_only_read_permission():
    repo_name = "promise-core"
    file = Path(".gitignore")
    branch_name = "master"
    repo_organisation = "request"

    downloader = GithubFileDownloader(
        repo_name=repo_name,
        repo_organisation=repo_organisation,
        target_file=file,
        branch_name=branch_name,
        allowed_period_no_updates=datetime.timedelta(days=356 * 30),
    )
    expected = (
        f"https://api.github.com/repos/{repo_organisation}/{repo_name}/contents/{file.as_posix()}?ref={branch_name}"
    )
    assert downloader.downloadable_content.url == expected

    # now add organisation into repo_name
    repo_name = "request/promise-core"
    file = Path(".gitignore")
    branch_name = "master"
    repo_organisation = ""
    downloader = GithubFileDownloader(
        repo_name=repo_name,
        repo_organisation=repo_organisation,
        target_file=file,
        branch_name=branch_name,
        allowed_period_no_updates=datetime.timedelta(days=356 * 30),
    )
    # no repo_organisation in download url
    expected = f"https://api.github.com/repos/{repo_name}/contents/{file.as_posix()}?ref={branch_name}"
    assert downloader.downloadable_content.url == expected
