import requests
from .utils import *
from .setup_logger import logger
from .opendatacrawlerInterface import OpenDataCrawlerInterface as interface


class INECrawler(interface):
    
    def __init__(self, domain, path):
        self.domain = domain
        self.path = path
        self.tourism_operations = [61, 62, 63, 132, 180, 238, 239, 240, 241, 328, 329, 330, 334]
        
    def get_package_list(self):
        """Get all the operations ids"""
        total_ids = []
        response = requests.get(self.domain + '/wstempus/js/ES/OPERACIONES_DISPONIBLES')
        if response.status_code == 200:
            operations = response.json()
            if len(operations) > 0:
                for p in operations:
                    total_ids.append(p['Id'])
        return total_ids
    
    def get_package(self, id):
        """Build a dict of elements metadata"""
        # operation_id = id
        operation_name = get_operation_name(id)

        try:
            response = requests.get('https://servicios.ine.es/wstempus/js/ES/TABLAS_OPERACION/' + str(id))
            if response.status_code == 200:
                meta = response.json()
                
                if len(meta) > 0:
                    packages = []
                    for x in meta:
                        metadata = dict()
                        
                        table_id = str(x.get('Id', None))
                        
                        metadata['id_portal'] = str(id) + '_' + table_id
                        metadata['id_custom'] = get_id_custom(metadata['id_portal'] + 'INE')
                        metadata['title'] = x.get('Nombre', None)
                        metadata['img_portal'] = None
                        metadata['description'] = operation_name + ': ' + metadata['title']
                        metadata['language'] = 'ES' # the url says that the query results are in spanish -> /ES/
                        
                        if id in self.tourism_operations:
                            metadata['theme'] = ['Turismo'] # this field is an array
                        else:
                            metadata['theme'] = None
                        
                        resources = dict()
                        resources['name'] = 'Datos tabla: ' + metadata['title']
                        resources['mediaType'] = 'csv'
                        resources['size'] = None
                        resources['downloadUrl'] = 'https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/' + table_id + '.csv?nocab=1'
                        
                        metadata['resources'] = [resources]
                        metadata['modified'] = x.get('Ultima_Modificacion', None)
                        metadata['issued'] = x.get('Anyo_Periodo_ini', None)
                        metadata['license'] = 'INE License'
                        metadata['source'] = self.domain
                        metadata['source_name'] = 'Instituto Nacional de Estadística'
                        
                        coverage = dict()
                        coverage['start_date'] = metadata['issued']
                        coverage['end_date'] = x.get('FechaRef_fin', None)
                        
                        metadata['temporal_coverage'] = [coverage]
                        metadata['spatial_coverage'] = None
                        
                        metadata['file_name'] = str(metadata['id_custom']) + '-INE-' + str(metadata['id_portal'])
                        
                        packages.append(metadata)
                        
                        # Saving all meta in a json file
                        save_all_metadata(metadata['file_name'], x, self.path)                    
                
                return packages
            else:
                return None
        except Exception as e:
            logger.info(e)
            return None
