import os
from dotenv import load_dotenv
from .log_helper import logger

__envDir__ = os.path.abspath(os.path.join(os.path.abspath(os.path.join(__file__, os.pardir)), os.pardir))
env = os.environ.get("MTM_ENV", "dev")
__env_file__ = os.path.join(__envDir__, f".env.{env}")

logger('DEBUG', f'Envrionnement = {env}')
logger('DEBUG', f'Path environnement file : {__env_file__}')

load_dotenv(dotenv_path=__env_file__)

# variable_global
ENVIRONEMENT = env
PROXY_AUCHAN = "http://proxy.auchan.com:80"

# file_transfer_environment
FT_PARAM_FILEPATH = os.environ.get("FT_PARAM_FILEPATH")
FT_GRAVITEE_URL = os.environ.get("FT_GRAVITEE_URL")
FT_GRAVITEE_KEY = os.environ.get("FT_GRAVITEE_KEY")

# bq_environment
GCP_ACCOUNT_SERVICE_FILE = os.environ.get("GCP_ACCOUNT_SERVICE_FILE")
BQ_PROJECT_ID = os.environ.get("BQ_PROJECT_ID")

# job_directory
CHAINE_APAR_DIR = os.environ.get("CHAINE_APAR_DIR")
