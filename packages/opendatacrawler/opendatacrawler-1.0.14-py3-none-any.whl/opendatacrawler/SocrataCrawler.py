from sodapy import Socrata
from .utils import *
from .opendatacrawlerInterface import OpenDataCrawlerInterface as interface
from .setup_logger import logger

class SocrataCrawler(interface):
    def __init__(self, domain, data_types):
        self.domain = domain
        self.data_types = data_types
        # Read the token from the config
        token = read_config()['soda_token']
        if token == "None" or not token:
            token = None
        self.client = Socrata(clean_url(self.domain), token)

    def get_package_list(self):
        """Get all the packages ids"""
        packages = [p['resource']['id'] for p in self.client.datasets()]
        return packages

    def get_package(self, id):
        """Build a dict of package metadata"""
        try:
            meta = self.client.get_metadata(id)
        except Exception:
            logger.warning("Metadata can't be collected %s", id)
            return None

        metadata = dict()

        metadata['identifier'] = id
        metadata['title'] = meta.get('title', None)
        if metadata['title'] is None:
            metadata['title'] = meta.get('name', None)
        metadata['description'] = meta.get('description', None)
        metadata['theme'] = meta.get('category', None)
        if metadata['theme'] == "unknow":
            metadata['theme'] = extract_tags(meta.get('tags', None))

        resource_list = []

        aux = dict()

        url = "/api/views/" + id + "/rows.csv?accessType=DOWNLOAD"
        aux['downloadUrl'] = self.domain + url
        aux['mediaType'] = "csv"
        aux['modified'] = meta.get('rowsUpdatedAt', None)
        if aux['modified'] is None:
            aux['modified'] = meta.get('indexUpdatedAt', None)

        resource_list.append(aux)

        metadata['resources'] = resource_list
        metadata['license'] = meta.get('license', None)
        metadata['source'] = self.domain

        return metadata
