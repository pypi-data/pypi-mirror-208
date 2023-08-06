import requests
import re
from .setup_logger import logger
from .opendatacrawlerInterface import OpenDataCrawlerInterface as interface


class EurostatCrawler(interface):
    def __init__(self, domain):
        # Obtain all metadata from all packages
        # this is a special case due to the config of the portal
        self.meta_data = self.get_meta()
        self.domain = domain

    def get_meta(self):
        """Create a dict with all metadata from the packages"""

        url = 'https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=table_of_contents_en.txt'

        try:
            response = requests.get(url)
        except Exception as e:
            logger.error(e)

        datos = dict()

        if response.status_code == 200:
            last_cat = ""
            res = response.text

            # Iterate over each line of the file that has a unusual format
            for i in res.split('\n'):

                # Split the element between commas
                parts = re.split(r"""("[^"]*"|'[^']*')""", i)
                parts[::2] = map(lambda s: "".join(s.split()), parts[::2])
                parts = list(map(lambda s: s.replace('"', '').strip(), parts))

                # Obtain the category of the dataset
                if 'folder' in parts:
                    last_cat = parts[1]

                # Extract the metadata of the dataset
                if 'dataset' in parts:
                    aux = dict()
                    aux['name'] = parts[1]
                    aux['cat'] = last_cat
                    aux['date'] = parts[9]
                    datos[parts[3]] = aux

        return datos

    def get_package_list(self):

        """Dowload the list of packages and get the ids"""

        url = 'http://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&downfile=dic%2Fen%2Ftable_dic.dic'

        try:
            response = requests.get(url)
        except Exception as e:
            logger.error(e)

        ids = []
        if response.status_code == 200:
            for line in response.text.split('\n'):
                if(len(line) > 1):
                    ids.append(line.split()[0].lower())

        return ids

    def get_package(self, id):

        """Get the metadata from the dic from a given id"""

        meta = self.meta_data[id]

        metadata = dict()

        metadata['identifier'] = id
        metadata['title'] = meta.get('name', None)
        metadata['description'] = ""
        metadata['theme'] = meta.get('cat', None)

        resource_list = []
        aux = dict()
        aux['name'] = meta.get('name', None)
        aux['downloadUrl'] = 'https://ec.europa.eu/eurostat/wdds/rest/data/v2.1/json/en/' + id
        aux['mediaType'] = 'json'
        resource_list.append(aux)

        metadata['resources'] = resource_list
        metadata['modified'] = meta.get('date', None)
        metadata['license'] = '<a href="https://ec.europa.eu/eurostat/about/policies/copyright">Eurostat</a>'
        metadata['source'] = self.domain

        return metadata
