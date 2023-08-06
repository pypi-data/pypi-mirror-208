from datetime import timedelta
from github import Github
from github.ContentFile import ContentFile
from github.Repository import Repository
from hdsr_pygithub import exceptions
from hdsr_pygithub.constants import BASE_DIR
from hdsr_pygithub.downloader.dir import GithubDirDownloader
from hdsr_pygithub.downloader.file import GithubFileDownloader
from hdsr_pygithub.tests.utils import _get_files_recursively
from hdsr_pygithub.tests.utils import _remove_dir_recursively
from pathlib import Path

import pytest


STARTENDDATE_REPO_NAME = "startenddate"
STARTENDDATE_ALLOWED_PERIOD_NO_UPDATES = timedelta(weeks=52 * 10)


def test_dir_does_not_exist():
    target_dir = Path("xxx")
    with pytest.raises(exceptions.GithubDirNotFoundError):
        GithubDirDownloader(repo_name=STARTENDDATE_REPO_NAME, target_dir=target_dir)


def test_dir_works():
    target_dir = Path("data/output/")
    downloader = GithubDirDownloader(
        repo_name=STARTENDDATE_REPO_NAME,
        target_dir=target_dir,
        allowed_period_no_updates=STARTENDDATE_ALLOWED_PERIOD_NO_UPDATES,
    )

    # test github instance
    assert isinstance(downloader.github_instance, Github)

    # test repo
    assert isinstance(downloader.repo_instance, Repository)
    assert downloader.repo_instance.name == STARTENDDATE_REPO_NAME

    # test target_file
    assert downloader.target_dir == target_dir

    # test target_file content
    assert all([isinstance(x, ContentFile) for x in downloader.downloadable_content])


def test_target_dir():
    # find all files starting at root_dir
    dir1 = Path("data/input/")
    downloader1 = GithubDirDownloader(
        repo_name=STARTENDDATE_REPO_NAME,
        target_dir=dir1,
        allowed_period_no_updates=STARTENDDATE_ALLOWED_PERIOD_NO_UPDATES,
    )
    assert len(downloader1.downloadable_content) == 1

    dir2 = Path("data/output/results/")
    downloader2 = GithubDirDownloader(
        repo_name=STARTENDDATE_REPO_NAME,
        target_dir=dir2,
        allowed_period_no_updates=STARTENDDATE_ALLOWED_PERIOD_NO_UPDATES,
    )
    assert len(downloader2.downloadable_content) == 14


def test_dir_too_old():
    target_dir = Path("data/output/")
    short_timedelta = timedelta(minutes=1)  # the file is too old for sure
    with pytest.raises(exceptions.GithubFileTooOldError):
        GithubDirDownloader(
            repo_name=STARTENDDATE_REPO_NAME, target_dir=target_dir, allowed_period_no_updates=short_timedelta,
        )


def test_filter_extension_good():
    target_dir = Path("")
    extensions = [".csv", ".cfg"]

    # only
    downloader = GithubDirDownloader(
        repo_name=STARTENDDATE_REPO_NAME,
        target_dir=target_dir,
        only_these_extensions=extensions,
        allowed_period_no_updates=STARTENDDATE_ALLOWED_PERIOD_NO_UPDATES,
    )
    file_extensions_found = [Path(x.path).suffix for x in downloader.downloadable_content]
    assert all([extension in extensions for extension in file_extensions_found])

    # exclude
    downloader = GithubDirDownloader(
        repo_name=STARTENDDATE_REPO_NAME,
        target_dir=target_dir,
        exclude_these_extensions=extensions,
        allowed_period_no_updates=STARTENDDATE_ALLOWED_PERIOD_NO_UPDATES,
    )
    file_extensions_found = [Path(x.path).suffix for x in downloader.downloadable_content]
    assert not any([extension in extensions for extension in file_extensions_found])


def test_filter_extension_wrong():
    target_dir = Path("")

    with pytest.raises(AssertionError):
        wrong_extensions = ["csv", ".*"]
        GithubDirDownloader(
            repo_name=STARTENDDATE_REPO_NAME, target_dir=target_dir, only_these_extensions=wrong_extensions,
        )

    with pytest.raises(AssertionError):
        wrong_extension = ".csv"
        GithubDirDownloader(
            repo_name=STARTENDDATE_REPO_NAME, target_dir=target_dir, only_these_extensions=wrong_extension,  # noqa
        )


def test_filter_files_good():
    target_dir = Path("data/output/results/")
    files = [
        Path("caw_oppervlaktewater_hymos_short.csv"),
        Path("caw_oppervlaktewater_long.csv"),
    ]

    # only
    downloader = GithubDirDownloader(repo_name=STARTENDDATE_REPO_NAME, target_dir=target_dir, only_these_files=files)
    assert len(downloader.downloadable_content) == 2
    assert sorted([Path(x.name) for x in downloader.downloadable_content]) == files

    # exclude
    downloader = GithubDirDownloader(repo_name=STARTENDDATE_REPO_NAME, target_dir=target_dir, exclude_these_files=files)
    assert len(downloader.downloadable_content) == 12
    assert sorted([x.name for x in downloader.downloadable_content]) == [
        "avallo_grondwater_short.csv",
        "caw_grondwater_long.csv",
        "caw_grondwater_short.csv",
        "caw_meteoverwachting_long.csv",
        "caw_meteoverwachting_short.csv",
        "caw_neerslag_long.csv",
        "caw_neerslag_short.csv",
        "caw_oppervlaktewater_short.csv",
        "caw_waterkwaliteit_long.csv",
        "caw_waterkwaliteit_short.csv",
        "mwm_peilschalen_short.csv",
        "winnet_grondwater_short.csv",
    ]


def test_filter_files_wrong():
    target_dir = Path("")

    with pytest.raises(AssertionError):
        wrong_extensions = ["csv", ".*"]
        GithubDirDownloader(
            repo_name=STARTENDDATE_REPO_NAME, target_dir=target_dir, only_these_extensions=wrong_extensions,
        )

    with pytest.raises(AssertionError):
        wrong_extension = ".csv"
        GithubDirDownloader(
            repo_name=STARTENDDATE_REPO_NAME, target_dir=target_dir, only_these_extensions=wrong_extension,
        )  # noqa


def test_dir_download_to_no_tmp_dir():
    target_dir = Path("data/output/results/")
    downloader = GithubDirDownloader(repo_name=STARTENDDATE_REPO_NAME, target_dir=target_dir)

    download_directory = downloader.download_files(use_tmp_dir=False, download_directory=BASE_DIR / "remove_this_dir2")
    assert download_directory.is_dir()

    expected_downloaded_file_names = [x.name for x in downloader.downloadable_content]
    reality_downloaded_file_paths = _get_files_recursively(dir_path=download_directory, files_found=[])
    reality_downloaded_file_names = [x.name for x in reality_downloaded_file_paths]
    assert sorted(expected_downloaded_file_names) == sorted(reality_downloaded_file_names)

    for downloaded_filepath in reality_downloaded_file_paths:
        assert downloaded_filepath.lstat().st_size > 10  # ensure > 10 kb
    _remove_dir_recursively(dir_path=download_directory)


def test_dir_download_to_tmp_dir():
    target_dir = Path("data/output/results/")
    downloader = GithubDirDownloader(repo_name=STARTENDDATE_REPO_NAME, target_dir=target_dir)

    tmp_dir = downloader.download_files(use_tmp_dir=True)
    assert tmp_dir.is_dir()

    expected_downloaded_file_names = [x.name for x in downloader.downloadable_content]
    reality_downloaded_file_paths = _get_files_recursively(dir_path=tmp_dir, files_found=[])
    reality_downloaded_file_names = [x.name for x in reality_downloaded_file_paths]
    assert sorted(expected_downloaded_file_names) == sorted(reality_downloaded_file_names)

    for downloaded_filepath in reality_downloaded_file_paths:
        assert downloaded_filepath.lstat().st_size > 10  # ensure > 10 kb
    _remove_dir_recursively(dir_path=tmp_dir)


def test_download_wrong():
    target_dir = Path("data/output/results/")

    # wrong key argument (should be target_dir)
    with pytest.raises(TypeError):
        GithubDirDownloader(repo_name=STARTENDDATE_REPO_NAME, target_file=Path("doesnotmatter"))  # noqa

    # wrong key argument (should be target_file)
    with pytest.raises(TypeError):
        GithubFileDownloader(repo_name=STARTENDDATE_REPO_NAME, target_dir=Path("doesnotmatter"))  # noqa

    downloader = GithubDirDownloader(repo_name=STARTENDDATE_REPO_NAME, target_dir=target_dir)
    with pytest.raises(AssertionError):
        downloader.download_files(use_tmp_dir=True, download_directory=Path("doesnotmatter"))
