import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import csv
import os
from t4flib.config import FT_PARAM_FILEPATH, FT_GRAVITEE_KEY, FT_GRAVITEE_URL
from t4flib.log_helper import logger
from t4flib.file_helper import get_all_file_by_filemask
import shutil
import time
import urllib3


class ft_flow:
    flow_name = ''
    server = ''
    ft_key = ''
    filemask = ''
    path_to_get_file = ''
    path_out = ''
    path_to_log = ''

    def __init__(self, flow_name, server, ft_key, filemask, path_to_get_file, path_out, path_to_log):
        self.flow_name = flow_name
        self.server = server
        self.ft_key = ft_key
        self.filemask = filemask
        self.path_to_get_file = path_to_get_file
        self.path_out = path_out
        self.path_to_log = path_to_log


def get_element_safely(arr, index):
    """
    Retourne l'élément d'un tableau `arr` à l'index `index` de manière sûre
    sans provoquer d'erreur si l'index est en dehors des limites du tableau.
    Si l'index est invalide, la fonction renvoie None.

    Args:
    arr (list): Le tableau dans lequel chercher l'élément
    index (int): L'index de l'élément à récupérer

    Returns:
    L'élément à l'index spécifié, ou None si l'index est invalide.
    """
    if index < 0 or index >= len(arr):
        # L'index est en dehors des limites du tableau, retourner None
        return None
    else:
        # L'index est valide, retourner l'élément correspondant
        return arr[index]


def get_flow_attributes_in_file(flow_name):
    logger('INFO', f'Vérification de l\' existance du flux {flow_name}')

    if FT_PARAM_FILEPATH is not None and os.path.exists(FT_PARAM_FILEPATH):
        with open(FT_PARAM_FILEPATH, 'r+', encoding='utf-8') as ft_param_file:
            csv_reader = csv.reader(ft_param_file, delimiter=';')
            for line_flow in csv_reader:
                if get_element_safely(line_flow, 0) == flow_name:
                    logger('INFO', f'le flux {flow_name} a été trouve')
                    return ft_flow(
                        get_element_safely(line_flow, 0),
                        get_element_safely(line_flow, 1),
                        get_element_safely(line_flow, 2),
                        get_element_safely(line_flow, 3),
                        get_element_safely(line_flow, 4),
                        get_element_safely(line_flow, 5),
                        get_element_safely(line_flow, 6),
                    )
            logger('ERROR', f'Le flux {flow_name} est introuvable')
            return None

    else:
        logger('ERROR', f'Le fichier de paramètre {FT_PARAM_FILEPATH} n\'existe pas ')


def send_file_by_filetransfer(flow_name):
    logger('INFO', f'Envoi dans filetransfer du flux {flow_name}')
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    ft_flow_to_send = get_flow_attributes_in_file(flow_name)

    if ft_flow_to_send is not None:
        session = requests.Session()
        retry = Retry(total=5, backoff_factor=0.1, status_forcelist=[401, 403, 404, 429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        headers = {
            "Content-type": "application/json",
            "X-Gravitee-api-Key": FT_GRAVITEE_KEY
        }

        logger('DEBUG', ft_flow_to_send.path_to_get_file)
        for file in get_all_file_by_filemask(ft_flow_to_send.path_to_get_file, ft_flow_to_send.filemask):

            shutil.copy(str(file.absolute()), ft_flow_to_send.path_out)

            body_request = json.dumps({
                "flow": ft_flow_to_send.flow_name,
                "userId": ft_flow_to_send.server,
                "authKey": ft_flow_to_send.ft_key,
                "uri": str(file)
            })

            try:
                response = requests.post(FT_GRAVITEE_URL, headers=headers, data=body_request, verify=False)
                ret = response.status_code
            except requests.exceptions.RequestException as e:
                logger("Error", f"{e}")
                ret = None

            if ret in [202, 200]:

                logger("INFO", f"Le flux {flow_name} contenant le fichier {str(file)} est parti")
            else:

                logger('ERROR', f"Un code erreur API : {ret} a eu lieu")
                logger('ERROR', f"Erreur lors de l'appel à l'API statut => {ret}")
