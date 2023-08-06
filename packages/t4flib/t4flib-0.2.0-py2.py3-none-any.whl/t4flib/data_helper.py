from log_helper import logger

import datetime

def get_safety_positional_data(line : str, arr_index : list):
    try:
        if len(arr_index) == 2:
            index_start=arr_index[0]
            index_end=arr_index[1]
            if len(line) > index_end:
                return str.strip(line[index_start:index_end])
        logger('WARNING', f'les paramètres sont mal reseigné {len(arr_index)} au lieu de 2 élément dans le tableau')
    except UnicodeDecodeError:
            print(f'Erreur d\'encodage lors de la lecture du fichier')


def verify_date_format(str_date, format):
    try:
          logger('INFO', f'Verification de la date {str_date}')
          datetime.datetime.strptime(str_date, format)
          logger('INFO', f'Date valide')
          return str_date
    
    except Exception as e:
         logger('ERROR', 'Date non valide, utilisation du timestamp actuel')
         return datetime.datetime.now().strftime(format)
    
         
    