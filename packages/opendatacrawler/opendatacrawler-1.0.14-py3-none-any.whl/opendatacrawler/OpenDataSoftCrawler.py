import requests
import traceback
from .utils import *
from .setup_logger import logger
from .opendatacrawlerInterface import OpenDataCrawlerInterface as interface


class OpenDataSoftCrawler(interface):
    
    def __init__(self, domain, path):
        self.domain = domain
        self.path = path

    def get_package_list(self):
        """Get all the packages ids"""
        try:
            total_ids = []
            response = requests.get(self.domain + '/api/v2/catalog/datasets?lang=es&timezone=UTC&limit=-1')
            if response.status_code == 200:
                data = response.json()
                datasets = data.get('datasets', None)
                    
                for p in datasets:
                    id = p['dataset'].get('dataset_id', None)
                    total_ids.append(id)
            return total_ids
        except Exception as e:
            print(traceback.format_exc())
            logger.info(e)
            return None

    def get_package(self, id):
        """Build a dict of package metadata"""
        try:
            response = requests.get(self.domain + '/api/v2/catalog/datasets/' + str(id) + '?lang=es&timezone=UTC')
            
            if response.status_code == 200:                
                meta_json = response.json()
                
                metadata = dict()
                
                metadata['id_portal'] = id
                metadata['id_custom'] = get_id_custom(metadata['id_portal'] + 'OPENDATASOFT')
                
                dataset = meta_json.get('dataset', None)
                
                if dataset is not None:
                    meta_default = dataset.get('metas', None).get('default', None)
                    meta_dcat = dataset.get('metas', None).get('dcat', None)
                    metadata['title'] = meta_default.get('title', None)
                    metadata['img_portal'] = None
                    metadata['description'] = meta_default.get('description', None)
                    metadata['language'] = meta_default.get('metadata_languages', None)
                    metadata['theme'] = meta_default.get('theme', None)
                
                    resource_list = []
                    mediaList = []
                    linkList = []
                    resource = dict()

                    res = requests.get(self.domain + '/api/v2/catalog/datasets/' + str(id) + '/exports')
                    if res.status_code == 200:
                        mediaTypes = res.json()
                        mediaTypesLinks = mediaTypes.get('links', None)
                        for m in mediaTypesLinks:
                            if m.get('rel', None) != 'self':
                                mediaList.append(m.get('rel', None))
                                linkList.append(m.get('href', None))
                    
                    resource['downloadUrl'] = linkList
                    resource['mediaType'] = mediaList

                    resource_list.append(resource)

                    metadata['resources'] = resource_list
                    metadata['modified'] = meta_default.get('modified', None)
                    
                    if meta_dcat:
                        metadata['source'] = self.domain
                        metadata['issued'] = meta_dcat.get('issued', None)
                        metadata['license'] = meta_default.get('license', None)
                        metadata['source_name'] = meta_dcat.get('creator', None)
                        coverage = dict()
                        coverage['start_date'] = meta_dcat.get('temporal_coverage_start', None)
                        coverage['end_date'] = meta_dcat.get('temporal_coverage_end', None) 
                        metadata['temporal_coverage'] = [coverage]
                        metadata['spatial_coverage'] = meta_dcat.get('spatial', None)
                    if self.domain.split('.')[1] == 'opendatasoft':
                        metadata['file_name'] = str(metadata['id_custom']) + '-' + str(self.domain.split('//')[1].split('.')[0]) + '-' + str(metadata['id_portal'])
                    else:
                        metadata['file_name'] = str(metadata['id_custom']) + '-' + str(self.domain.split('.')[1]) + '-' + str(metadata['id_portal'])
                # Saving all meta in a json file
                save_all_metadata(metadata['file_name'], meta_json, self.path)
                
                return metadata
            else:
                return None
        except Exception as e:
            print(traceback.format_exc())
            logger.info(e)
            return None