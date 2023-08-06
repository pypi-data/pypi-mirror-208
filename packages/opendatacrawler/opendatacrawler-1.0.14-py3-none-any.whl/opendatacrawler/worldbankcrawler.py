import requests
from .utils import *
from .setup_logger import logger
from .opendatacrawlerInterface import OpenDataCrawlerInterface as interface


class WorldBankCrawler(interface):

    def __init__(self, domain, data_types):
        self.domain = domain
        self.data_types = data_types

    def get_package_list(self):
        """Get all the packages ids"""
        skip = 0
        ids = []
        fin = False
        while not fin:
            response = requests.get('https://datacatalogapi.worldbank.org/ddhxext/DatasetList?$top=100&$skip='+str(skip))
            packages = response.json()['data']
            if len(packages) == 0:
                fin = True
            skip += 100
            for p in packages:
                ids.append(p['dataset_unique_id'])

        return ids

    def get_package(self, id):
        """Build a dict of package metadata"""
        try:
            response = requests.get('https://datacatalogapi.worldbank.org/ddhxext/DatasetView?dataset_unique_id=' + id)
        except Exception as e:
            logger.info(e)

        if response.status_code == 200:
            meta = response.json()

            metadata = dict()

            metadata['identifier'] = id
            metadata['title'] = meta.get('identification', None).get('title',None)
            metadata['description'] = meta.get('identification', None).get('description',None)
            metadata['theme'] = extract_tags(meta.get('priority_tags', None))

            resource_list = []
            for res in meta['Resources']:
                if (self.data_types is None or
                   res['name'].lower() in self.data_types):
                    aux = dict()
                    aux['name'] = res.get('name', None)
                    if res.get('format', None) != 'HTML':
                        aux['downloadUrl'] = 'https://datacatalogapi.worldbank.org/ddhxext/ResourceDownload?resource_unique_id='+ res.get('resource_unique_id')
                    else:
                        aux['downloadUrl'] = res.get('harvest_source', None)
                    aux['mediaType'] = res.get('format', None)
                    resource_list.append(aux)

            metadata['resources'] = resource_list
            metadata['modified'] = meta.get('metadata_modified', None)
            metadata['license'] = meta.get('license_title', None)
            metadata['source'] = self.domain

            return metadata
        else:
            return None
