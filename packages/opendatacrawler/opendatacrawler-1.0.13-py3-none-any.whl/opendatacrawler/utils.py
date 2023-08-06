import configparser
import os
import pathlib
import time
import json
import requests
import traceback
import hashlib
from w3lib.url import url_query_cleaner
from url_normalize import url_normalize
from .setup_logger import logger

timer = 0
# Funtions to control a timer for ZenodoCrawler calls to the API
def timer_start():
    global timer
    # Starts if == 0, else it continues
    if timer == 0:
        timer = time.perf_counter()
            
def timer_stop():
    global timer
    # Obtain the time when it stops
    end = time.perf_counter()
    rest = end - timer
    timer_restart()
    # Returns the total time it has been counting
    return rest

def timer_restart():
    global timer
    # Restarts the timer
    timer = 0

def clean_url(u):
    """Clean a url string to obtain the mainly domain without protocols."""

    u = url_normalize(u)
    parameters = ['utm_source',
                  'utm_medium',
                  'utm_campaign',
                  'utm_term',
                  'utm_content']

    u = url_query_cleaner(u, parameterlist=parameters,
                          remove=True)

    if u.startswith("http://"):
        u = u[7:]
    if u.startswith("https://"):
        u = u[8:]
    if u.startswith("www."):
        u = u[4:]
    if u.endswith("/"):
        u = u[:-1]
    return u.split('/')[0]


def extract_tags(tags):
    """ Extract the tag names from tag list"""
    return [tag['display_name'] for tag in tags]

def extract_keywords(keywords):
    """ Extract the keywords from keyword list"""
    if keywords:
        if len(keywords) > 0:
            theme = keywords.split(", ")
            return theme
        else:
            return None
    else:
        return None


def read_config():
    d = dict()

    config = configparser.ConfigParser()

    current_path = pathlib.Path(__file__).parent.resolve()
    config.read(str(current_path) + '/config.ini')

    d['soda_token'] = config['Soda']['token']

    return d

def read_token():
    d = dict()

    config = configparser.ConfigParser()

    current_path = pathlib.Path(__file__).parent.resolve()
    config.read(str(current_path) + '/config.ini')

    d['zenodo_token'] = config['Zenodo']['token']

    return d


def check_url(url):
    """ Check if exist a well-formed url"""
    if url[:8] == "https://" or url[:7] == "http://":
        return True
    else:
        return False


def lower_list(li):
    """ Convert all element of a list to lowercase"""
    if li:
        return [x.lower() for x in li]
    else:
        return None


def create_folder(path):
    if not os.path.isdir(path):
        try:
            os.mkdir(path)
        except OSError:
            print("Creation of the dir %s failed" % path)
            return False
        else:
            print("Successfully created the dir %s " % path)
            return True
    else:
        return True


def print_intro():

    """ Print the content inside intro.txt"""
    path = os.path.dirname(os.path.abspath(__file__))
    f = open(path + "/intro.txt", "r")
    for x in f:
        print(x, end='')


def load_resume_id(path):
    try:
        f = open(path, "r")
        return f.read()

    except Exception:
        return None


def save_resume_id(path, id):
    f = open(path, "w")
    f.write(str(id))
    f.close()


def remove_resume_id(path):

    if os.path.exists(path):
        os.remove(path)

def get_requests_ids(file_type, token):
    skip = 1
    ids = []
    fin = False
        
    while not fin:
        response = requests.get('https://zenodo.org/api/records/?type=dataset&file_type=' + file_type + '&size=200&page='+str(skip)+'&access_token='+str(token))
        if response.status_code == 200:
            packages = response.json()['hits']['hits']
            if len(packages) > 0:
                skip += 1
                for p in packages:
                    ids.append(p['id'])
            else:
                fin = True
        else:
            fin = True
    return ids

def get_operation_name(id):
    try:
        info = ''
        response = requests.get('https://servicios.ine.es/wstempus/js/ES/OPERACIONES_DISPONIBLES')
        if response.status_code == 200:
            operations = response.json()
            if len(operations) > 0:
                for p in operations:
                    if p['Id'] == id:
                        info = p['Nombre']
        return info
        
    except Exception as e:
        print(traceback.format_exc())
        logger.info(e)
        return None


def save_all_metadata(id, meta, path): 
    # Saving all meta in a json file
    try:
        with open(path + "/all_" + str(id) + '.json',
                'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error('Error saving metadata  %s',
                    path + "/all_" + str(id) + '.json')
        logger.error(e)


def get_id_custom(name):
    if name and name != '':
        id = hashlib.md5()
        id.update(name.encode())
        return str(int(id.hexdigest(), 16))[0:12]
    else:
        return None
