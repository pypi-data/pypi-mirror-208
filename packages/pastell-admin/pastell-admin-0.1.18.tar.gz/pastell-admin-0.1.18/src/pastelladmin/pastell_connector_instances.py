#!/usr/bin/env python3
import csv
from datetime import datetime
import argparse
from .api.client import Session, Connector
from .shared.configuration import getConfiguration

# USAGE
# This script list pastell all connector instances and export result in a csv file.
# option -e or --env => to select environnement execution (prod or preprod). default is preprod
# option -i or --ide => pastell entity to filter. eg : 1
#
# ./pastell_connector_instances.py --env=preprod --ide=1
#
#

def script_wrapper():
  xstart = datetime.now()
  parser = argparse.ArgumentParser()
  parser.add_argument("-e", "--env", type=str, help="Sélection de l'environnement", choices=['preprod','prod'], required=True)
  parser.add_argument("-o", "--org", help="id_e de l'entité", default='all')
  parser.add_argument("-c", "--csv", help="Fichier csv en sortie. /tmp/instances.csv par défaut")
  args = parser.parse_args()

  instances(env=args.env, org=args.org, csv=args.csv)

  xend = datetime.now()
  delta = xend - xstart
  msg = f"info : script exécuté en {delta.seconds // 60} minutes et {delta.seconds % 60} secondes"
  print(msg)

def instances(env, org='all', csv="/tmp/instances.csv" ):
  #Get parameters from config file ~/.pastell-admin
  config = getConfiguration()

  server = config[env]['server']
  user = config[env]['login']
  pwd = config[env]['password']
  session = Session(server,  user, pwd)


  fields = ['id_ce', 'id_e', 'libelle', 'id_connecteur', 'type']
  csv_list = []
  connectors = Connector(session).getAll(org).result
  for instance in connectors:
    data = []
    for field in fields:
      data.append(instance[field])
    csv_list.append(data)

  writeResults(csv_list, csv, fields)

def writeResults(csv_list, output, fields):
  with open(output, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    # write the header
    writer.writerow(fields)
    # write multiple rows
    writer.writerows(csv_list)

if __name__ == '__main__':
  script_wrapper()
