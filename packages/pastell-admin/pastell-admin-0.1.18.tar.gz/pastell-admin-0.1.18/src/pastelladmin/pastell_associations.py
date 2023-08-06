#!/usr/bin/env python3
import csv
from datetime import datetime
import argparse
from .api.client import Session, Association, Entity
from .shared.configuration import getConfiguration

def writeResults(csv_list, output, fields):
  with open(output, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    # write the header
    writer.writerow(fields)
    # write multiple rows
    writer.writerows(csv_list)

def script_wrapper():
  xstart = datetime.now()
  parser = argparse.ArgumentParser()
  parser.add_argument("-e", "--env", type=str, help="Sélection de l'environnement", choices=['preprod','prod'], required=True)
  parser.add_argument("-o", "--org", help="id_e de l'entité")
  parser.add_argument("-c", "--csv", help="Fichier csv en sortie. /tmp/associations.csv par défaut")
  args = parser.parse_args()

  associations(env=args.env, org=args.org, csv=args.csv)

  xend = datetime.now()
  delta = xend - xstart
  msg = f"info : script exécuté en {delta.seconds // 60} minutes et {delta.seconds % 60} secondes"
  print(msg)


def associations(env, org=None, csv="/tmp/associations" ):
  #Get parameters from config file ~/.pastell-admin
  config = getConfiguration()

  server = config[env]['server']
  user = config[env]['login']
  pwd = config[env]['password']
  session = Session(server,  user, pwd)
  #START PROCESS
  fields = ['id_fe', 'id_e', 'flux', 'id_ce', 'type']
  csv_list = []
  #Get stats from Pastell API
  entites = False
  if org:
    entites = [{"id_e": org}]
  else:
    entites = Entity(session).getAll().result
  if entites:
    # Boucle sur les entités
    for entite in entites:
      id_e = entite['id_e']
      #Get all associations
      associations = Association(session).getByEntity(id_e).result
      #url = f"https://{server}/api/v2/entite/{id_e}/flux/"
      #request = requests.get(url, auth=HTTPBasicAuth(user, pwd))
      #associations = json.loads(request.text)
      for association in associations:
        data = []
        for field in fields:
          data.append(association[field])
        csv_list.append(data)

    writeResults(csv_list, csv, fields)

if __name__ == '__main__':
  script_wrapper()







