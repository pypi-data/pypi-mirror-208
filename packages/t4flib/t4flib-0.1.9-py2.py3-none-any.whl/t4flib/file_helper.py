import os
from .log_helper import logger
import shutil
import fnmatch
import datetime
import pathlib
import json
import zipfile
import glob
import pandas as pd
import csv


def __validate_filemask__(filename, filemask):
    return fnmatch.fnmatch(filename, filemask)


def zip_folder(source_dir, dest_dir, output_filename):
    logger('INFO', f'Zippage du dossier de ouf {source_dir}')
    try:
        with zipfile.ZipFile(os.path.join(dest_dir, output_filename), 'w', zipfile.ZIP_DEFLATED) as zipf:
            files=get_all_file_by_filemask(source_dir, '*')
            if len(files) == 0:
                logger('WARNING', 'Pas de fichier à zipper')
                return
            
            for file in files:
                file_path=str(file.absolute())
            
                zipf.write(file_path, os.path.relpath(file_path, source_dir))

        logger('INFO', f'Le dossier {source_dir} a été zippé avec succès dans {output_filename}')
    except Exception as e:
        logger('ERROR', f'{str(e)}')
        raise


def purge_directory(directory):
    logger("INFO", f"Démarrage de la purge du dossier {directory}")
    try:
        # obtenir la liste de tous les fichiers et dossiers dans le dossier source
        files = glob.glob(os.path.join(directory, '*'))

        # supprimer chaque fichier et dossier individuellement
        for f in files:
            if os.path.isfile(f):
                os.remove(f)
            elif os.path.isdir(f):
                shutil.rmtree(f)

    except Exception as e:
        logger('ERROR', f'{str(e)}')
        raise

    logger("INFO", f"Fin de la purge du dossier {directory}")


def move_files_by_filemask(source_dir, dest_dir, filemask):
    logger('INFO',
           f'Début du déplacement des fichiers commencant par {filemask} du dossier {source_dir} vers {dest_dir}')

    try:
        # obtenir la liste de tous les fichiers correspondant au masque de fichier
        file_list = get_all_file_by_filemask(source_dir, filemask)

        # déplacer chaque fichier individuellement
        for file in file_list:
            shutil.move(str(file.absolute()), os.path.join(dest_dir, file.name))

    except Exception as e:
        logger('ERROR', f'{str(e)}')
        raise

    logger('INFO', f'Fin du déplacement des fichiers commencant par {filemask} du dossier {source_dir} vers {dest_dir}')


def read_and_concatenate_csv_files(source_dir, dest_dir, output_filename ,delimiter=';', isNeedSkipHeader=False):
    
    logger('INFO', f'Démarrage de la concaténation des CSV du dossier {source_dir}')
    
    try:
    
        filenames=get_all_file_by_filemask(source_dir, '*.csv')
        
        if len(filenames) == 0:
            logger('WARNING', 'Aucun fichier n\'a été detecté')
            return None
        
        with open(os.path.join(dest_dir, output_filename), 'w', newline='') as output_file:
            writer = csv.writer(output_file, delimiter=delimiter)
            
            for file in filenames:
                with open(file, 'r') as input_file:
                        reader = csv.reader(input_file, delimiter=delimiter)
                        if isNeedSkipHeader:
                            next(reader)
                        writer.writerows(reader)
   
    except Exception as e:
        logger('ERROR', str(e))     
    finally:    
        logger('INFO', f'Fin de la concaténation des CSV du dossier {source_dir}')


def is_file_older_than_nb_day(filepath, datetime_to_inspect):
    logger('INFO', f'Vérification que le fichier {filepath} soit plus ancien que {datetime_to_inspect} jour')
    try:
        if os.path.exists(filepath):
            modification_datetime = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
            logger('DEBUG', f'Date de modification fichier : {modification_datetime}')
            date_jour = datetime.datetime.now()
            if (date_jour - modification_datetime).days > (datetime_to_inspect - 1):
                return True
            return False
        logger('WARNING', f"Le fichier {filepath} n'existe pas, la valeur par défaut est True")
        return True

    except Exception as e:
        logger('ERROR', str(e))
        raise


def backup_file(filepath):
    logger('INFO', f'Début de la backup du fichier {filepath}')
    if not os.path.exists(filepath):
        logger('WARNING', f"Le fichier {filepath} n'existe pas")
    else:
        try:
            shutil.move(filepath, '_'.join([filepath, 'backup']))
        except Exception as e:
            logger('ERROR', f'Une erreur est surevenu : {e}')
            raise
    logger('INFO', f'LE fichier {filepath} a été backup')


def rename_file(source_dir, old_name, new_name):
    try:
        filepath = os.path.join(source_dir, old_name)
        new_filepath = os.path.join(source_dir, new_name)
        if not os.path.exists(filepath):
            logger('ERROR', f"{filepath} n'existe pas")
        else:
            shutil.move(filepath, new_filepath)
    except Exception as e:
        logger('ERROR', str(e))
        raise
    logger('INFO', f'Le fichier {old_name} a été renommé en {new_name}')


def get_all_file_by_filemask(source_dir, filemask):
    try:
        source_dir_pathlib = pathlib.Path(source_dir)
        files = [file for file in list(source_dir_pathlib.rglob(filemask))]

    except Exception as e:
        logger('ERROR', str(e))
        raise
    logger('INFO', f'{len(files)} fichier(s) ont été récupéré(s)')
    return files


def safe_json_loads(json_string):
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError:
        data = None
    return data


def copy_files_by_filemask(source_dir, dest_dir, filemask):
    logger('INFO', f'Copie des ficher du dossier {source_dir} vers {dest_dir}')

    try:
        files = get_all_file_by_filemask(source_dir, filemask)

        for file in files:
            shutil.copyfile(str(file.absolute()), os.path.join(dest_dir, file.name))
    except Exception as e:
        logger('ERROR', str(e))
        raise
    logger('INFO', 'L\'ensemble des fichiers ont été copiés')




