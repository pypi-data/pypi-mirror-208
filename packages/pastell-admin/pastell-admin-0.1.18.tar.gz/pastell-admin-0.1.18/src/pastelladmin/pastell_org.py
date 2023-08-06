#!/usr/bin/env python3
import csv, argparse
from datetime import datetime
from .api.client import Session, Entity
from .shared.configuration import getConfiguration

# USAGE
# This script list pastell entities with sub entities.

def writeResults(OUTPUT, csv_list, ACTIVE):
  header = ['id_e', 'denomination', 'siren', 'type', 'centre_de_gestion', 'entite_mere']
  if ACTIVE:
    header.append('is_active')

  with open(OUTPUT, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    # write the header
    writer.writerow(header)
    # write multiple rows
    writer.writerows(csv_list)

def script_wrapper():
  xstart = datetime.now()
  parser = argparse.ArgumentParser()
  parser.add_argument("-e", "--env", type=str, help="Sélection de l'environnement", choices=['preprod','prod'], required=True)
  parser.add_argument("-c", "--csv", help="Fichier csv en sortie. /tmp/organismes.csv par défaut")
  parser.add_argument("-a", "--active", help="Retourne l'information active", action="store_true")
  args = parser.parse_args()

  org(env=args.env, csv=args.csv, active=args.active)

  xend = datetime.now()
  delta = xend - xstart
  msg = f"info : script exécuté en {delta.seconds // 60} minutes et {delta.seconds % 60} secondes"
  print(msg)


def org(env, csv="/tmp/organismes.csv", active=False):
  #Get parameters from config file ~/.pastell-admin
  config = getConfiguration()

  ENV = env
  OUTPUT = csv
  ACTIVE = active
  SERVER = config[ENV]['server']
  user = config[ENV]['login']
  pwd = config[ENV]['password']
  #START PROCESS
  session = Session(SERVER,  user, pwd)
  #Check if session is valid
  if not session.valid:
    exit()

  csv_list = []
  #Get Entities from Pastell API
  if ACTIVE:
    entities = Entity(session).getAllWithStatus()
  else:
    entities = Entity(session).getAll()
  if entities.success:
    if ACTIVE:
      entites_json = entities.result["all"]
    else:
      entites_json = entities.result
    # Boucle sur les entités
    for entite in entites_json:
      id_e = entite['id_e']
      denomination = entite['denomination']
      siren = entite['siren']
      type = entite['type']
      centre_de_gestion = entite['centre_de_gestion']
      entite_mere = entite['entite_mere']
      #Enregistrement dans la liste csv
      raw = [id_e, denomination, siren, type, centre_de_gestion, entite_mere]
      if ACTIVE:
        raw.append(entite['is_active'])
      csv_list.append(raw)

    writeResults(OUTPUT, csv_list, ACTIVE)

if __name__ == '__main__':
  script_wrapper()





