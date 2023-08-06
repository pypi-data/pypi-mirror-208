from pathlib import Path


DEFAULT_GITHUB_ORGANISATION = "hdsr-mid"

# BASE_DIR avoid 'Path.cwd()'
BASE_DIR = Path(__file__).parent
assert BASE_DIR.name == "hdsr_pygithub", f"BASE_DIR {BASE_DIR} is wrong, should be 'hdsr_pygithub'"

# Each HDSR user has a personal drive (G:/)
G_DRIVE = Path("G:/")
SECRETS_ENV_PATH = G_DRIVE / "secrets.env"
GITHUB_PERSONAL_ACCESS_TOKEN = "GITHUB_PERSONAL_ACCESS_TOKEN"
