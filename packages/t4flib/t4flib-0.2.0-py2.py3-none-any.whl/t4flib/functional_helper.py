from log_helper import logger
from file_helper import get_all_file_by_filemask
from data_helper import verify_date_format, get_safety_positional_data
import os
import csv 
from datetime import datetime


__SCHEMA_HEADER_AP__= [[0,1 ],[1,11],[11,61],[61,76],[76,86],[86,106],[106,110],[110,210],[210,235],[235,265],[265,285],[285,315],[315,325],[325,345],[345,355],[355,405],[405,415],[415,425],[425,435],[435,460],[460,464],[464,494],[494,504],[504,514],[514,534],[534,544],[544,594],[594,609],[609,629],[629,639],[639,640],[640,660],[660,690],[690,720],[720,750],[750,780],[780,810],[810,840],[840,870],[870,900],[900,930],[930,960],[960,990],[990,1020],[1020,1050],[1050,1080],[1080,1110],[1110,1140],[1140,1170],[1170,1200],[1200,1230],[1230,1260],[1260,1290],[1290,1320],[1320,1350],[1350,1380],[1380,1410],[1410,1440],[1440,1480]]
__SCHEMA_BODY_AP__ = [[0,1],[1,11],[11,61],[61,76],[76,91],[91,116],[116,136],[136,137],[137,147],[147,247],[247,262],[262,263],[263,264],[264,289],[289,339],[339,399],[399,424],[424,449],[449,474],[474,494],[494,514],[514,534],[534,554],[554,574],[574,594],[594,834],[834,854],[854,874],[874,894],[894,914],[914,915],[915,945],[945,970],[970,995],[995,102],[1020,1040],[1040,1041],[1041,1056],[1056,1057],[1057,1058],[1058,1088],[1088,1118],[1118,1148],[1148,1178],[1178,1208],[1208,1238],[1238,1268],[1268,1298],[1298,1328],[1328,1358],[1358,1388],[1388,1418],[1418,1448],[1448,1478],[1478,1508],[1508,1538],[1538,1568],[1568,1598],[1598,1628],[1628,1658],[1658,1688],[1688,1718],[1718,1748],[1748,1778],[1778,1808],[1808,1838],[1838,1868],[1868,1898],[1898,1928],[1928,1958],[1958,1988],[1988,2018],[2018,2048],[2048,2078],[2078,2108],[2108,2138],[2138,2175]]
__SCHEMA_HEADER_AR__ = [[0, 1],[1, 11],[11, 26],[26, 36],[36, 37],[37, 57],[57, 72],[72, 87],[87, 117],[117, 132],[132, 142],[142, 162],[162, 182],[182, 202],[202, 222],[222, 242],[242, 392],[392, 412],[412, 422],[422, 572],[572, 575],[575, 605],[605, 615],[615, 625],[625, 675],[675, 705],[705, 735],[735, 755],[755, 775],[775, 795],[795, 805],[805, 835],[835, 836]]
__SCHEMA_BODY_AR__ = [[0, 1],[1, 11],[11,41],[41,191],[191, 211],[211, 216],[216, 236],[236, 251],[251, 271],[271, 291],[291, 311],[311, 331],[331, 351],[351, 371],[371, 391],[391, 411],[411, 431],[431, 451],[451, 471],[471, 491],[491, 511],[511, 531],[531, 551],[551, 571],[571, 591],[591, 611],[611, 626],[626, 756],[756, 757]]

def extract_all_positional_data(line, positions):
    return_array=[]
    for position in positions:
        return_array.append(get_safety_positional_data(line, position))
    return return_array



def concatenate_ap_output(src_dir, dest_dir):

    try:
        logger('INFO', 'Demarrage de la concaténation des output ORACLE AP')

        # trouver tout les output
        AP_OUTPUT_FILEMASK='ACAP*'
        EXECUTION_TIMESTAMP=datetime.now().strftime('%Y%m%d%H%M%S')

        outputs_ar = get_all_file_by_filemask(src_dir, AP_OUTPUT_FILEMASK)

        if True if len(outputs_ar) > 0 else False:
            output_body_file=os.path.join(dest_dir, f'body_ap_{EXECUTION_TIMESTAMP}.csv')
            output_header_file= os.path.join(dest_dir, f'header_ap_{EXECUTION_TIMESTAMP}.csv')

            with open(output_header_file, 'w+') as header_output, open(output_body_file, 'w+') as body_output:

                header_writer=csv.writer(header_output, delimiter=';')
                body_writer=csv.writer(body_output, delimiter=';')

                for output_ar in outputs_ar:

                    with open(str(output_ar.absolute()), 'r', encoding='iso-8859-1') as output_f:

                        logger('DEBUG', f'{output_ar.name}')

                        filename_splitted=(output_ar.name).split('-')
                        file_execution_timestamp= verify_date_format(((filename_splitted[1]).replace("_","").replace('.dat', '')),'%Y%m%d%H%M%S') if len(filename_splitted) >=2 else EXECUTION_TIMESTAMP
                        file_code_si=(filename_splitted[0]).replace('ACAP_FACT_TESSI', '') if len(filename_splitted) >=2 else '0'

                        for line in output_f:
                            if line.startswith('1'):
                                header_line=[
                                    file_execution_timestamp,
                                    file_code_si
                                  ] + extract_all_positional_data(line, __SCHEMA_HEADER_AP__)
                                header_writer.writerow(header_line)

                            elif line.startswith('2'):
                                body_line=[
                                    file_execution_timestamp,
                                    file_code_si
                                ] + extract_all_positional_data(line, __SCHEMA_BODY_AP__)
                                body_writer.writerow(body_line)

    except Exception as e:
        logger('ERROR', f'ERREUR : {str(e)}')
    finally:
        logger('INFO', 'Fin de la concaténation des output ORACLE AP')


def concatenate_ar_output(src_dir, dest_dir):
    try:
        logger('INFO', 'Demarrage de la concaténation des output ORACLE AR')

        # trouver tout les output
        AR_OUTPUT_FILEMASK='ACAR*'
        EXECUTION_TIMESTAMP=datetime.now().strftime('%Y%m%d%H%M%S')

        outputs_ar = get_all_file_by_filemask(src_dir, AR_OUTPUT_FILEMASK)

        if True if len(outputs_ar) > 0 else False:
            output_body_file=os.path.join(dest_dir, f'body_ar_{EXECUTION_TIMESTAMP}.csv')
            output_header_file= os.path.join(dest_dir, f'header_ar_{EXECUTION_TIMESTAMP}.csv')

            with open(output_header_file, 'w+') as header_output, open(output_body_file, 'w+') as body_output:

                header_writer=csv.writer(header_output, delimiter=';')
                body_writer=csv.writer(body_output, delimiter=';')

                for output_ar in outputs_ar:

                    with open(str(output_ar.absolute()), 'r', encoding='iso-8859-1') as output_f:

                        logger('DEBUG', f'{output_ar.name}')

                        #ACAR_MOVE_MAPPING_024_20230517_133526.dat

                        filename_splitted=(output_ar.name).split('_')
                        file_execution_timestamp= verify_date_format((filename_splitted[4] + filename_splitted[5].replace('.dat', '')),'%Y%m%d%H%M%S') if len(filename_splitted) >= 6 else EXECUTION_TIMESTAMP
                        file_code_si= filename_splitted[3]  if len(filename_splitted) >=4 else '0'

                        for line in output_f:
                            if line.startswith('1'):
                                header_line=[
                                    file_execution_timestamp,
                                    file_code_si
                                  ] + extract_all_positional_data(line, __SCHEMA_HEADER_AR__)
                                header_writer.writerow(header_line)

                            elif line.startswith('2'):
                                body_line=[
                                    file_execution_timestamp,
                                    file_code_si
                                ] + extract_all_positional_data(line, __SCHEMA_BODY_AR__)
                                body_writer.writerow(body_line)

    except Exception as e:
        logger('ERROR', f'ERREUR : {str(e)}')
    finally:
        logger('INFO', 'Fin de la concaténation des output ORACLE AP')