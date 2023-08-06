#!/usr/bin/env python3
import requests, json, csv
from requests.auth import HTTPBasicAuth
import os, sys
from datetime import datetime
import getopt, configparser

# USAGE
# This script list pastell documents in a specific state on time interval and export result in json file and a csv file.
# json file is a dict and can be used as inpur with pastell_delete.py script :
# option -e or --env => to select environnement execution (prod or preprod). default is preprod
# option -s or --status => pastell state to filter. eg : terminate#
# option -t or --type => Type de dossier. Exemple autres-studio-sans-tdt
#
# ./delete_any.py --env=preprod --status=terminate --type=autres-studio-sans-tdt
#
#

options, remainder = getopt.getopt(
      sys.argv[1:],
      'e:s:t:',
      ['env=','status=','type='])

xstart = datetime.now()

WKD = os.path.abspath(os.path.dirname(__file__))
ENV = 'preprod'
OUTPUT = "result"
LIMIT = 0
CLEAR = False
STATUS = "terminate"
TYPE = "autres-studio-sans-tdt"
START = "2015-01-01"
END = xstart.strftime("%Y-%m-%d")
FILE_SUCCESS = '%s/success' % WKD
FILE_TMP = '%s/tmp' % WKD
FILE_ERROR = '%s/errors' % WKD

config = configparser.ConfigParser()
config.read("%s/config.ini" % WKD)


for opt, arg in options:
  if opt in ('e', '--env'):
    ENV = arg
  elif opt in ('s', '--status'):
    STATUS = arg
  elif opt in ('t', '--type'):
    TYPE = arg


SERVER = config[ENV]['server']
user = config[ENV]['login']
pwd = config[ENV]['password']

FINISHED = False
while not FINISHED:
  url = "https://%s/api/v2/entite/1/document/?type=%s&last_action=%s" % (SERVER, TYPE, STATUS)
  request0 = requests.get(url, auth=HTTPBasicAuth(user, pwd))
  data = json.loads(request0.text)
  nb = len(data)
  print("Supression de %s documents" % str(nb))
  if nb == 0:
    FINISHED = True
  for doc in data:
    url2 = "https://%s/api/v2/entite/%s/document/%s/action/supression" % (SERVER, doc['id_e'], doc["id_d"])
    request = requests.post(url2, auth=HTTPBasicAuth(user, pwd))
    print(request.status_code)
    print(request.text)

xend = datetime.now()
print (str(xend))
print ("script execute en : " + str((xend-xstart).total_seconds()))
