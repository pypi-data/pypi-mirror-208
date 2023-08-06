import requests
from .utils import *
import time
import traceback
from .setup_logger import logger
from .opendatacrawlerInterface import OpenDataCrawlerInterface as interface


class ZenodoCrawler(interface):
    
    def __init__(self, domain):
        self.domain = domain
        
        # Read token
        token = read_token()['zenodo_token']
        if token == "None" or not token:
            token = None
        self.token = token

    def get_package_list(self):
        """Get all the packages ids"""
        total_ids = []
        
        ids_csv = get_requests_ids('csv', self.token)
        ids_zip = get_requests_ids('zip', self.token)
        ids_xlsx = get_requests_ids('xlsx', self.token)
        
        # Add ids        
        cont_csv = 0
        for x in ids_csv:
            total_ids.append(x)
            cont_csv = cont_csv + 1
            
        cont_zip = 0    
        for y in ids_zip:
            total_ids.append(y)
            cont_zip = cont_zip + 1
            
        cont_xlsx = 0    
        for z in ids_xlsx:
            total_ids.append(z)
            cont_xlsx = cont_xlsx + 1
            
        return total_ids

    def get_package(self, id):
        """Build a dict of package metadata"""
        try:
            response = requests.get('https://zenodo.org/api/records/' + str(id))
            
            if response.status_code == 200:
                # Timer start counting
                timer_start()
                
                meta_json = response.json()

                metadata = dict()
                
                metadata['identifier'] = id
                
                meta = meta_json.get('metadata', None)
                
                if meta is not None:
                    metadata['title'] = meta.get('title', None)
                    metadata['description'] = meta.get('description', None)
                    if meta.get('keywords', None) is not None:
                        metadata['theme'] = extract_keywords(meta.get('keywords', None)[0])
                
                resource_list = []

                aux = dict()

                if meta_json.get('files', None) is not None:
                    url = meta_json.get('files', None)[0]
                    aux['downloadUrl'] = url.get('links', None).get('self', None)
                    aux['mediaType'] = url.get('type', None)

                resource_list.append(aux)

                metadata['resources'] = resource_list
                metadata['modified'] = meta.get('publication_date', None)
                #metadata['license'] = requests.get('https://zenodo.org/api/licenses/')
                metadata['license'] = None
                metadata['source'] = self.domain
                
                return metadata
            else:
                # Timer stops when it can't make any more calls to the API
                rest = timer_stop()
                if rest < 60:
                    time.sleep(60 - rest)
                    return (self.get_package(id))
        except Exception as e:
            print(traceback.format_exc())
            logger.info(e)
            return None