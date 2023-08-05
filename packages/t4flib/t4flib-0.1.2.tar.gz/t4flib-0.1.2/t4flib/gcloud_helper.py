import shutil

from google.cloud import bigquery
from google.oauth2 import service_account
from google.cloud import storage
from google.api_core import exceptions as gcloud_ex
import pandas as pd
from .log_helper import logger
from .config import GCP_ACCOUNT_SERVICE_FILE, ENVIRONEMENT, PROXY_AUCHAN, BQ_PROJECT_ID
import os


def run_bq_query(query) -> (int, pd.DataFrame):
    ENVIRONEMENT='dev'
    credentials = service_account.Credentials.from_service_account_file(GCP_ACCOUNT_SERVICE_FILE)
    if ENVIRONEMENT == 'dev':
        os.environ["HTTPS_PROXY"] = PROXY_AUCHAN
    try:
        logger('DEBUG', query)
        client = bigquery.Client(credentials=credentials)
        query_job = client.query(query, location='EU')
        # if len(query_job.errors) > 0:
        #     return 1, pd.DataFrame()

        response = [dict(row) for row in query_job.result()]
        response_dataframe = pd.DataFrame.from_records(response)
        logger('INFO', 'La requete a été executé avec succès !')
        return 0, response_dataframe

    except gcloud_ex.BadRequest as e:
        logger('ERROR', f"La requête est mal formée ou comporte des erreurs syntaxiques : {str(e)}")
        return 1, None

    except gcloud_ex.Forbidden as e:
        logger('ERROR',
               f"L'utilisateur n'a pas les autorisations nécessaires pour accéder aux ressources demandées : {str(e)}")
        return 1, None

    except gcloud_ex.NotFound as e:
        logger('ERROR', f"La ressource demandée n'a pas été trouvée : {str(e)}")
        return 1, None

    except gcloud_ex.ServiceUnavailable as e:
        logger('ERROR', f"Le service BigQuery n'est pas disponible ou inaccessible : {str(e)}")
        return 1, None

    except gcloud_ex.TooManyRequests as e:
        logger('ERROR', f"L'utilisateur a dépassé le quota de requêtes autorisé : {str(e)}")
        return 1, None

    except  gcloud_ex.PermissionDenied as e:
        logger('ERROR', f"Erreur lors de l'indetification : {str(e)}")
        return 1, None

    except gcloud_ex.GoogleAPIError as e:
        logger('ERROR', f"Une erreur s'est produite lors de l'exécution de la requête : {str(e)}")
        return 1, None

    except Exception as e:
        logger('ERROR', f'Une erreur non repertorié est survenue : {str(e)}')
        return 1, None
def upload_file_to_gcs(file_path, bucket_name, path_bucket):
    logger('INFO', f'Début de l\'upload du fichier {file_path} vers le bucket {bucket_name}')
    try:
        if ENVIRONEMENT == 'dev':
            os.environ["HTTPS_PROXY"] = PROXY_AUCHAN

        credentials = service_account.Credentials.from_service_account_file(GCP_ACCOUNT_SERVICE_FILE)
        client = storage.Client(credentials=credentials)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(path_bucket)
        blob.upload_from_filename(file_path)

        logger('INFO', f'Le fichier {file_path} a été envoyé à gs://{os.path.join(bucket_name,path_bucket)} avec succès' )
        return 0

    except FileNotFoundError as e:
        logger('ERROR',f'Le fichier {nom_fichier_local} est introuvable : {e}')
        return 1
    except Exception as e:
        logger('ERROR',f'Une erreur inattendue s\'est produite : {e}')
        return 1