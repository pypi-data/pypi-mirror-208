#!/usr/bin/env python3
import csv
from datetime import datetime
import argparse
from .api.client import Session, Stat
from .shared.configuration import getConfiguration

"""
Ce script permet de générer un fichier csv de statistiques

  Args:
    option -e or --env => to select environnement execution (prod or preprod). default is preprod
    option -o or --org => pastell entity to filter. eg : 1. Optional
    option -c or --csv => Chemin et nom du fichier csv généré. Optional
    option -i or --infos => pour afficher le statut des organismes et  notamment si l'entité est active. Par défault, affiche les statistiques sur les flux.


  Usage :
    ./pastell_stats.py --env=preprod --org=1 --csv=info.csv --infos
    ./pastell_stats.py --env=preprod  --csv=/tmp/statistiques_flux.csv

"""

def writeResults(OUTPUT, csv_list, csv_headers):

  with open(OUTPUT, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    # write the header
    writer.writerow(csv_headers)
    # write multiple rows
    writer.writerows(csv_list)

def script_wrapper():
  xstart = datetime.now()
  parser = argparse.ArgumentParser()
  parser.add_argument("-e", "--env", type=str, help="Sélection de l'environnement", choices=['preprod','prod'], required=True)
  parser.add_argument("-o", "--org", help="id_e de l'entité")
  parser.add_argument("-f", "--flux", help="type de flux")
  parser.add_argument("-c", "--csv", help="Fichier csv en sortie. /tmp/stats-YYYY-MM-DD.csv par défaut")
  parser.add_argument("-i", "--infos", help="pour afficher le statut des organismes et  notamment si l'entité est active. Par défault, affiche les statistiques sur les flux", action="store_true")
  args = parser.parse_args()

  stats(env=args.env, org=args.org, csv=args.csv, infos=args.infos, flux=args.flux)

  xend = datetime.now()
  delta = xend - xstart
  msg = f"info : script exécuté en {delta.seconds // 60} minutes et {delta.seconds % 60} secondes"
  print(msg)

def stats(env, org=None, csv=None, infos=None, flux=None):
  #Get parameters from config file ~/.pastell-admin
  config = getConfiguration()

  ladate = datetime.now()
  xdate = ladate.strftime("%Y-%m-%d")
  ENV = env
  OUTPUT = csv or "/tmp/stats-%s.csv" % xdate
  ORG = org
  INFOS = infos
  TYPE = flux

  SERVER = config[ENV]['server']
  user = config[ENV]['login']
  pwd = config[ENV]['password']

  csv_headers = ['date', 'id_e', 'flux', 'statut', 'nombre']
  if INFOS:
    csv_headers = ['id_e', 'type', 'denomination', 'siren', 'date_inscription', 'etat', 'entite_mere', 'centre_de_gestion', 'is_active']
  #START PROCESS
  session = Session(SERVER,  user, pwd)
  #Check if session is valid
  if not session.valid:
    exit()
  csv_list = []
  #Get stats from Pastell API
  stats = Stat(session).get(id_e=ORG, type=TYPE)
  if stats.success:
    stats_entites_json = stats.result
    if stats_entites_json:
      # Boucle sur les entités
      for index in stats_entites_json:
        stats = stats_entites_json[index]
        infos = stats['info']
        if INFOS:
          raw_data = []
          for prop in csv_headers:
            raw_data.append(infos[prop])
          csv_list.append(raw_data)
        else:
          id_e = infos['id_e']
          #Boucle sur tous les types de flux
          for dossier in stats['flux']:
            #Boucle sur les statuts
            for status in stats['flux'][dossier]:
              total_docs = int(stats['flux'][dossier][status])
              #Enregistrement dans la liste csv
              csv_list.append([xdate, id_e, dossier, status, total_docs])

      writeResults(OUTPUT, csv_list, csv_headers)

    else:
      print(stats.result)

if __name__ == '__main__':
  script_wrapper()





