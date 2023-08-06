import requests
import urllib3
from .utils import *
from .setup_logger import logger
from .opendatacrawlerInterface import OpenDataCrawlerInterface as interface

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CkanCrawler(interface):

    def __init__(self, domain, data_types, path):
        self.domain = domain
        self.data_types = data_types
        self.path = path

    def get_package_list(self):

        # Make a request to CKAN API to obtain the package list
        response = requests.get(self.domain+"/api/3/action/package_list", verify=False)

        # Check if in the previous call there is a redirect
        # in this case, is used the package_searach endpoint
        if len(response.history) > 0:

            total = -1
            offset = 0
            packages = []

            # Iterate over the endpoint with the max of 1000 results until the end
            # and save the packages id on a list
            while total != len(packages):

                # Build query url
                url = "/api/3/action/package_search?rows=1000&start="
                url += str(offset)

                try:
                    response = requests.get(self.domain + url, verify=False)
                except Exception as e:
                    logger.error(e)

                if response.status_code == 200:
                    response = response.json()['result']
                    for r in response['results']:
                        packages.append(r['id'])

                    total = response['count']
                    offset += 1000
                else:
                    break
            return packages

        elif response.status_code == 200:
            packages = response.json()['result']
            return packages
        else:
            return []

    def get_package(self, id):

        # Obtain a package with all their metadata
        try:
            url = self.domain + "/api/3/action/package_show?id=" + id

            response = requests.get(url, verify=False)

            if response.status_code == 200:
                meta = response.json()['result']

                metadata = dict()

                metadata['id_portal'] = id
                metadata['id_custom'] = get_id_custom(metadata['id_portal']+self.domain)
                metadata['title'] = meta.get('title', None)
                metadata['img_portal'] = None
                metadata['description'] = meta.get('notes', None)
                metadata['language'] = meta.get('language', None)
                metadata['theme'] = meta.get('category', None)

                if metadata['theme'] is None:
                    metadata['theme'] = extract_tags(meta.get('tags', None))

                resource_list = []
                for res in meta['resources']:
                    if (self.data_types is None or
                    res['format'].lower() in self.data_types):
                        resource = dict()
                        resource['name'] = res.get('name', None)
                        resource['mediaType'] = [res['format'].lower()]
                        resource['size'] = res.get('size', None)
                        resource['downloadUrl'] = [res.get('url', None)]
                                
                        id = res.get('url', None).split("/")[-1].split(".")[0]
                        resource_list.append(resource)

                metadata['resources'] = resource_list
                metadata['modified'] = meta.get('metadata_modified', None)
                metadata['issued'] = meta.get('metadata_created', None)
                metadata['license'] = meta.get('license_id', None)
                metadata['source'] = self.domain
                metadata['source_name'] = None
                        
                coverage = dict()
                coverage['start_date'] = meta.get('temporal_begin_date', None)
                coverage['end_date'] = meta.get('temporal_end_date', None)
                        
                metadata['temporal_coverage'] = [coverage]
                metadata['spatial_coverage'] = None
                
                metadata['file_name'] = str(metadata['id_custom']) + '-' + str(self.domain.split('.')[1]) + '-' + str(metadata['id_portal'])
                
                # Saving all meta in a json file
                save_all_metadata(metadata['file_name'], meta, self.path)

                return metadata
            else:
                return None

        except Exception as e:
            logger.error(e)
            return None