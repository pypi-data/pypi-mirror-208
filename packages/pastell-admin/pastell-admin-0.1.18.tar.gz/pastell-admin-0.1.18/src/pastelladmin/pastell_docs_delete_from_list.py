#!/usr/bin/env python3
import requests, json
from requests.auth import HTTPBasicAuth
import datetime, os, logging, shutil
import argparse, configparser

# USAGE
# This script delete pastell documents listed in json file.
# json file is a dict with this mandatory properties id_e and document inside a docs array :
# {"docs": [{"id_e": "1", "document": "9uTg9B4"},...]}
# option -s or --source => path to json file containing list of documents to delete
# option -e or --env => to select environnement execution (prod or preprod). default is preprod
# option -l or --limit => define a limit of documents to delete. Default is 0 = no limit
#
# ./pastell_delete.py --env=preprod|prod [--limit=10] --source=myfile.json
#

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", type=str, help="Sélection de l'environnement", choices=['preprod','prod'], required=True)
parser.add_argument("-l", "--limit", type=int, help="Limite le nombre de suppression au nombre défini")
parser.add_argument("-s", "--source", required=True, type=str, help="Chemin vers le fichier json contenant les id_d des documents à supprimer")
args = parser.parse_args()

ENV = args.env
LIMIT = args.limit
FILE_DOCS_TO_DELETE = args.source
LOG_FILE = "/tmp/delete.log"

user_config_dir = os.path.expanduser("~")
user_config = user_config_dir + "/.pastell-admin"
if not os.path.isfile(user_config):
  os.makedirs(user_config_dir, exist_ok=True)
  shutil.copyfile("./pastell-admin.dist", user_config)

config = configparser.ConfigParser()
config.optionxform = lambda option: option
config.read(user_config)

SERVER = config[ENV]['server']
user = config[ENV]['login']
pwd = config[ENV]['password']

#logs
FORMAT = '%(asctime)s — %(name)s — %(levelname)s — %(message)s'
logging.basicConfig(filename=LOG_FILE, format=FORMAT)
logger = logging.getLogger('pastell-delete %s' % ENV)
logger.setLevel(logging.DEBUG) # better to have too much log than not enough

start = datetime.datetime.now()
logger.info("Début de la suppression des documents à %s" % start)

print("API PASTELL : Suppression des documents en %s" % ENV)

with open(FILE_DOCS_TO_DELETE, 'r', encoding='UTF8') as f:
    data = json.load(f)
docs = data["docs"]
logger.info("liste des documents à supprimer chargée %s" % FILE_DOCS_TO_DELETE)

TASK = 1
for doc in docs:
  if not LIMIT or TASK <= LIMIT:
    TASK +=1
    url1 = "https://%s/api/v2/entite/%s/document/%s/action/fatal-error" % (SERVER, doc['id_e'], doc["document"])
    request1 = requests.post(url1, auth=HTTPBasicAuth(user, pwd))
    if request1.status_code in [200, 201, 400, 403]:
        result1 = json.loads(request1.text)
        if "result" in result1:
            if result1["result"] == True:
                print("Suppression document %s/%s" % (doc['id_e'], doc["document"]))
                url = "https://%s/api/v2/entite/%s/document/%s/action/supression" % (SERVER, doc['id_e'], doc["document"])
                request = requests.post(url, auth=HTTPBasicAuth(user, pwd))
                print(request.status_code)
                print(request.text)
                if request.status_code in [200, 201, 400, 403]:
                    try:
                        result = json.loads(request.text)
                        keys = result.keys()
                        if "status" in keys:
                            if result["status"] == "error":
                                logger.warning("Erreur suppression du document %s/%s : %s" % (doc['id_e'],doc["document"],result["error-message"]))

                        elif "result" in keys:
                            if result["result"] == True:
                                logger.info("document %s/%s %s supprimé avec succès" % (doc['id_e'],doc["document"], result["message"]))

                    except ValueError as err:
                        logger.warning("Erreur %s" % err)
                else:
                    logger.warning("Erreur de requête : %s" % url)


end = datetime.datetime.now()
delta = end - start
msg = f"script exécuté en {delta.seconds // 60} minutes et {delta.seconds % 60} secondes"
print(msg)
logger.info(msg)
