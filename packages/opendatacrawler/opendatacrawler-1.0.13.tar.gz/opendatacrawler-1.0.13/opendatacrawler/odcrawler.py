import requests
import urllib3
import json
from .utils import *
import re
import os
from .SocrataCrawler import SocrataCrawler
from .CkanCrawler import CkanCrawler
from .worldbankcrawler import WorldBankCrawler
from .eurostatcrawler import EurostatCrawler
from .datosgobescrawler import datosGobEsCrawler
from .ZenodoCrawler import ZenodoCrawler
from .OpenDataSoftCrawler import OpenDataSoftCrawler
from .INECrawler import INECrawler
from .setup_logger import logger
from sys import exit
import time


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class OpenDataCrawler():

    def __init__(self, domain, path,
                 data_types=None, sec=None):

        self.domain = domain
        self.dms = None
        self.dms_instance = None
        self.max_sec = sec
        if not path:
            directory = os.getcwd()
            path = directory+"/data/"
            create_folder(path)
        self.save_path = path + clean_url(self.domain)
        self.resume_path = path + "resume_"+clean_url(self.domain)+".txt"

        if data_types:
            self.data_types = [x.lower() for x in list(data_types)]
        else:
            self.data_types = None

        print("Detecting DMS")
        self.detect_dms()

    def detect_dms(self):
        """Detect the domain DMS and create and instantece according to it"""
        dms = dict()

        dms['Socrata'] = "/api/catalog/v1"
        dms['CKAN'] = "/api/3/action/package_list"
        dms['WorldBank'] = '/ddhxext/DatasetList'
        dms['EuroStat'] = '/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&dir=metadata'
        dms['datosGobEs'] = '/apidata/catalog/dataset?_sort=title&_pageSize=1'
        dms['Zenodo'] = '/api/records/'
        dms['OpenDataSoft'] = '/api/v2/catalog'
        dms['INE'] = '/wstempus/js/ES/OPERACIONES_DISPONIBLES'

        for k, v in dms.items():
            try:
                # Delete / if exist
                if self.domain[-1] == "/":
                    self.domain = self.domain[:-1]

                response = requests.get(self.domain+v, verify=False)
                # If the content-type not is a webpage(we want a json api response) and the result code is 200
                if response.status_code == 200 and response.headers['Content-Type']!="text/html":
                    self.dms = k
                    logger.info("DMS detected %s", k)

                    if not create_folder(self.save_path):
                        logger.info("Can't create folder" + self.save_path)
                        exit()
                    break
            except Exception as e:
                logger.info(e)

        # Create an instance of the corresponding dms
        if self.dms == 'CKAN':
            self.dms_instance = CkanCrawler(self.domain, self.data_types, self.save_path)
        if self.dms == 'Socrata':
            self.dms_instance = SocrataCrawler(self.domain, self.data_types)
        if self.dms == 'WorldBank':
            self.dms_instance = WorldBankCrawler(self.domain, self.data_types)
        if self.dms == 'EuroStat':
            self.dms_instance = EurostatCrawler(self.domain)
        if self.dms == 'datosGobEs':
            self.dms_instance = datosGobEsCrawler(self.domain, self.data_types)
        if self.dms == 'Zenodo':
            self.dms_instance = ZenodoCrawler(self.domain)
        if self.dms == 'OpenDataSoft':
            self.dms_instance = OpenDataSoftCrawler(self.domain, self.save_path)
        if self.dms == 'INE':
            self.dms_instance = INECrawler(self.domain, self.save_path)
        if self.dms is None:
            print("The domain " + self.domain + " is not supported yet")
            logger.info("DMS not detected in %s", self.domain)
        

    def save_dataset(self, url, ext):
        """ Save a dataset from a given url and extension"""
        try:
            # Web page is not consideret a dataset
            if url[-4] != 'html':

                logger.info("Saving... %s ", url)

                with requests.get(url, stream=True, timeout=60, verify=False) as r:
                    if r.status_code == 200:
                        # Try to obtain the file name inside the link, else
                        # use the last part of the url with the dataset extension
                        if "Content-Disposition" in r.headers.keys():
                            fname = re.findall("filename=(.+)", r.headers["Content-Disposition"])[0]
                        else:
                            fname = url.split("/")[-1]
                            if len(fname.split(".")) == 1:
                                fname += "."+ext

                        path = self.save_path+"/"+fname.replace('"', '')

                        # Write the content on a file
                        with open(path, 'wb') as outfile:
                            t = time.time()
                            partial = False
                            for chunk in r.iter_content(chunk_size=1024):

                                if self.max_sec and ((time.time() - t) > self.max_sec):
                                    partial = True
                                    logger.warning('Timeout! Partially downloaded file %s', url)
                                    break

                                if chunk:
                                    outfile.write(chunk)
                                    outfile.flush()

                        if not partial:
                            logger.info("Dataset saved from %s", url)

                        return path
                    else:
                        logger.warning('Problem obtaining the resource %s', url)

                        return None

        except Exception as e:
            logger.error('Error saving dataset from %s', url)
            logger.error(e)
            return None

    def save_partial_dataset(self, url, ext):
        """ Save a dataset from a given url and extension"""
        try:
            # Web page is not consideret a dataset
            if url[-4] != 'html':

                logger.info("Saving... %s ", url)
               
                with requests.get(url, stream=True, timeout=20, verify=False) as r:
                    if r.status_code == 200:
                        # Try to obtain the file name inside the link, else
                        # use the last part of the url with the dataset extension
                        if "Content-Disposition" in r.headers.keys():
                            fname = re.findall("filename=(.+)", r.headers["Content-Disposition"])[0]
                        else:
                            fname = url.split("/")[-1]
                            if len(fname.split(".")) == 1:
                                fname += "."+ext

                        path = self.save_path+"/"+fname.replace('"', '')

                        # Write the content on a file
                        loader = requests.get(url, stream=True)

                        encoding = "cp1252"
                        if loader.apparent_encoding == 'utf-8':
                            encoding = 'utf-8'
                        if loader.apparent_encoding == 'iso8859_11':
                            encoding = 'iso-8859-1'
                        if loader.apparent_encoding == 'windows-1256':
                            encoding = 'windows-1256'
                        lines = []
                        lines_csv = []
                        max_lines = 50  # Max lines to download
                        if 'datos.gob.es' in self.domain:
                            elements = url.split('/')
                            ext = 'csv' in elements[-1:][0]

                        for i, line in enumerate(loader.iter_lines()):
                            if line:
                                if ext and i < max_lines:
                                    decoded_line = line.decode(encoding)
                                    lines_csv.append(decoded_line+"\n")
                                elif ext and i >= max_lines:
                                    break
                                elif not ext:
                                    decoded_line = line.decode(encoding)
                                    lines.append(decoded_line+"\n")

                        logger.info('Dataset partially saved from %s', url)
                        f = open(path, 'w', encoding='utf-8')
                        if ext == 'csv':
                            f.writelines(lines_csv)
                        else:
                            f.writelines(lines)
                        f.close()

                        return path
                    else:
                        logger.warning('Problem obtaining the resource %s', url)

                        return None

        except Exception as e:
            logger.error('Error saving dataset from %s', url)
            logger.error(e)
            return None

    def save_metadata(self, data):

        """ Save the dict containing the metadata on a json file"""
        try:
            with open(self.save_path + "/meta_"+str(data['file_name'])+'.json',
                      'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error('Error saving metadata  %s',
                         self.save_path + "/meta_"+data['file_name']+'.json')
            logger.error(e)

    def get_package_list(self):
        return self.dms_instance.get_package_list()

    def get_package(self, id):
        return self.dms_instance.get_package(id)