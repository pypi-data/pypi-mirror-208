[token]: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
[hdsr-mid]: [https://github.com/hdr-mid]
[pypi]: https://pypi.org/project/hdsr_pygithub
[mit]: https://github.com/hdsr-mid/hdsr_pygithub/blob/main/LICENSE.txt

### Context
* Created: November 2021
* Author: Renier Kramer, renier.kramer@hdsr.nl
* Python version: >3.5

### Description
A python project that enables interaction with the GitHub API v3 to e.g. read/download dirs/files from the 
github organisation [hdsr-mid]. Often downloading is not required as files can be loaded in 
memory, see 'Usage 1' below. To interact with private repos you need to authenticate via a personal github 
access token (see 'Token' below).

### Token
A token (a long hash) has to be created once (and updated when it expires). You can have maximum 1 token. This token is
related to your github user account, so you don't need a token per repo/organisation/etc. 
You can [create a token yourself][token]. In short:
1. Login github.com with your account (user + password)
2. Ensure you have at least read-permission for the hdsr-mid repo(s) you want to interact with. To verify, browse to 
   the specific repo. If you can open it, then you have at least read-permission. If not, please contact 
   renier.kramer@hdsr.nl to get access.
3. Create a token:
   1. On github.com, go to your profile settings (click your icon right upper corner and 'settings' in the dropdown).
   2. Click 'developer settings' (left lower corner).
   3. Click 'Personal access tokens' and then 'Tokens (classic)'.
   4. Click 'Generate new token' and then 'Generate new token (classic)'.
   5. For scopes select only 'repo' (Full control of private repositories). This selects automatically the related 
      sub-selections (e.g. 'repo:status' (Access commit status).
4. We recommend setting an expiry date of max 1 year (for safety reasons).
5. You can use this token in two ways:
   1. recommended: Create a .env file for example on your personal HDSR drive, e.g. 'G:/secrets.env', and add one 
      line: GITHUB_PERSONAL_ACCESS_TOKEN=<your_token>. Please do not share this file with others!
   2. Use it hardcode in you code, see 'Usage 1: simple'. In this case, be careful sharing your code.
   
#### Why use a token?
This project is build on another pypi project 'PyGithub'. That project provides three ways for authentication exists 
to log in with GitHub API:
1. Github(login_or_token=<user>, password=<pass>)
2. Github(login_or_token=<personal_access_token>)
3. Github(base_url="https://{hostname}/api/v3", login_or_token=<personal_access_token>)
   
However, option 1 is not possible for github organisation 'hdsr-mid' since 13 sep 2021 as it requires 2FA for 
everyone in the hdsr-mid organisation: login trough github api is now only possible with a token (options 1 and 2). 
In this project we use option 2.


#### Installation
```
pip install hdsr-pygithub 
# or 
conda install hdsr-pygithub --channel hdsr-mid'
``` 

### Usage example 1: simple (little arguments and hard-coded personal_access_token)
```
# Ensure you followed steps 1 till 4 of topic 'Token' above
import hdsr_pygithub
from pathlib import Path

github_downloader = hdsr_pygithub.GithubFileDownloader(
    repo_name="startenddate",                                               # ensure your github account has read-permission for this repo
    target_file=Path("data/output/results/mwm_peilschalen_short.csv"),      # this file must exist in the master branch
    personal_access_token=<your_personal_access_token>                      # see topic 'Token' 5.2 above
)

# download files to disk
download_directory = github_downloader.download_files(download_directory=<a_dir>)
downloaded_filepath = download_directory / "data/output/results/mwm_peilschalen_short.csv"
assert downloaded_filepath.exists()

# or read file in memory using e.g. pandas
import pandas as pd
url = github_downloader.get_download_url()
# in case filetype is a .csv (other other filetypes: https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html):
dataframe_file = pd.read_csv(filepath_or_buffer=url)
```

### Usage example 2: sophisticated (more arguments and personal_access_token in .env file)
```
# Ensure you followed steps 1 till 4 from topic 'Token' above
import hdsr_pygithub
from datetime import datetime
from pathlib import Path

github_downloader = hdsr_pygithub.GithubDirDownloader(
    repo_name="startenddate",                                               # ensure your github account has read-permission for this repo
    branch_name="main",                                                     # defaults to 'main' if not specified                                                                        
    target_dir=Path("data/output/results/"),                                # this dir must exist in the branch specified above
    allowed_period_no_updates=datetime.timedelta(weeks=10),                 # defaults to 1 year if not specified 
    repo_organisation='hdsr-mid',                                           # defaults to 'hdsr-mid'
    secrets_env_path=<your .env file path>                                  # defaults to Path("G:/") / "secrets.env"
)

# download complete github directory (recursive) to disk
download_directory = github_downloader.download_files(download_directory=<a_dir>)
assert download_directory.is_dir()

# or download complete github directory (recursive) to disk to your Temp directory (C:/Users/<user>/AppData/Local/Temp/..)
download_directory = github_downloader.download_files(use_tmp_dir=True)
assert download_directory.is_dir()
```

### License 
[MIT][mit]

### Releases
[PyPi][pypi]

### Contributions
All contributions, bug reports, bug fixes, documentation improvements, enhancements and ideas are welcome.
Issues are posted on: https://github.com/hdsr-mid/hdsr_pygithub/issues

### Test coverage (release v1.12)
```
---------- coverage: platform win32, python 3.11.0-final-0 -----------
Name                               Stmts   Miss  Cover
------------------------------------------------------
hdsr_pygithub\__init__.py              4      0   100%
hdsr_pygithub\constants.py             7      0   100%
hdsr_pygithub\downloader\base.py     252     40    84%
hdsr_pygithub\downloader\dir.py       88      0   100%
hdsr_pygithub\downloader\file.py      34      0   100%
hdsr_pygithub\exceptions.py           21      2    90%
setup.py                              10     10     0%
------------------------------------------------------
TOTAL                                416     52    88%
```

### Conda general tips
#### Build conda environment (on Windows) from any directory using environment.yml:
Note1: prefix is not set in the environment.yml as then conda does not handle it very well
Note2: env_directory can be anywhere, it does not have to be in your code project
```
> conda env create --prefix <env_directory><env_name> --file <path_to_project>/environment.yml
# example: conda env create --prefix C:/Users/xxx/.conda/envs/project_xx --file C:/Users/code_projects/xx/environment.yml
> conda info --envs  # verify that <env_name> (project_xx) is in this list 
```
#### Start the application from any directory:
```
> conda activate <env_name>
At any location:
> (<env_name>) python <path_to_project>/main.py
```
#### Test the application:
```
> conda activate <env_name>
> cd <path_to_project>
> pytest  # make sure pytest is installed (conda install pytest)
```
#### List all conda environments on your machine:
```
At any location:
> conda info --envs
```
#### Delete a conda environment:
```
Get directory where environment is located 
> conda info --envs
Remove the enviroment
> conda env remove --name <env_name>
Finally, remove the left-over directory by hand
```
#### Write dependencies to environment.yml:
The goal is to keep the .yml as short as possible (not include sub-dependencies), yet make the environment 
reproducible. Why? If you do 'conda install matplotlib' you also install sub-dependencies like pyqt, qt 
icu, and sip. You should not include these sub-dependencies in your .yml as:
- including sub-dependencies result in an unnecessary strict environment (difficult to solve when conflicting)
- sub-dependencies will be installed when dependencies are being installed
```
> conda activate <conda_env_name>

Recommended:
> conda env export --from-history --no-builds | findstr -v "prefix" > --file <path_to_project>/environment_new.yml   

Alternative:
> conda env export --no-builds | findstr -v "prefix" > --file <path_to_project>/environment_new.yml 

--from-history: 
    Only include packages that you have explicitly asked for, as opposed to including every package in the 
    environment. This flag works regardless how you created the environment (through CMD or Anaconda Navigator).
--no-builds:
    By default, the YAML includes platform-specific build constraints. If you transfer across platforms (e.g. 
    win32 to 64) omit the build info with '--no-builds'.
```
#### Pip and Conda:
If a package is not available on all conda channels, but available as pip package, one can install pip as a dependency.
Note that mixing packages from conda and pip is always a potential problem: conda calls pip, but pip does not know 
how to satisfy missing dependencies with packages from Anaconda repositories. 
```
> conda activate <env_name>
> conda install pip
> pip install <pip_package>
```
The environment.yml might look like:
```
channels:
  - defaults
dependencies:
  - <a conda package>=<version>
  - pip
  - pip:
    - <a pip package>==<version>
```
You can also write a requirements.txt file:
```
> pip list --format=freeze > <path_to_project>/requirements.txt
```
