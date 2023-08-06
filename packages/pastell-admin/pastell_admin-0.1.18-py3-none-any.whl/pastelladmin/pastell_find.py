#!/usr/bin/env python3
from itertools import count
import json, csv
import os
from datetime import datetime
import argparse
from .api.client import Session, Stat, Document
from .shared.configuration import getConfiguration

# USAGE
# This script list pastell documents in a specific state on time interval and export result in json file and a csv file.
# json file is a dict and can be used as inpur with pastell_delete.py script :
# option -e or --env => to select environnement execution (prod or preprod). default is preprod
# option -s or --status => pastell states to filter. eg : tdt-error,termine
# option -f or --flux => pastell flux to filter. eg : actes-generiques or actes-generique,deliberations-studio
# option -o or --output => define a name for 2 output files (csv + json). Default is result
# option -g or -- org => Filter to only one id_e
# option -d or --date => Filter to one date
# option -a or --start => Filter to date begin
# option -b or --end => Filter to date end
# option -m or --merge => to merge results in existing output file
# option -t or --transit => use transit status an not last status
# option -n or --count => to only count docs without details
# option -l or --list => export id documents as list
# option -j or --json => export result as json file
#

def summaryMessage(status, transit, flux, org, start, end, output):
  message = ["API PASTELL : Recherche des documents dont :"]
  if status:
    if not transit:
      message.append("le statut est : %s" % ", ".join(status))
    else:
      message.append("le statut est passé par : %s" % ", ".join(status))
  if flux:
    message.append("pour les flux : %s" % ", ".join(flux))
  else:
    message.append("pour tous les types de flux")
  if org:
    message.append("pour l'entité : %s" % org)
  else:
    message.append("pour toutes les entités")
  if start and end:
    message.append("entre le %s et le %s" % (start, end))
  elif start:
    message.append("depuis le %s" % start)
  elif end:
    message.append("antérieurs à %s" % end)
  if count:
    message.append("Analyse : dénombrement des dossiers concernés par flux et entité")
  elif list:
    message.append("Analyse : listing des dossiers concernés par flux et entité")
  if json:
    message.append("le fichier %s.json sera créé en sortie" % output)
  message.append("le fichier %s.csv sera créé en sortie" % output)
  print("\n".join(message))

def getStats(session, org=None):
  stats = False
  #Get stats from Pastell API. If ORG is None get all stats
  request = Stat(session).get(id_e=org)
  if request.success:
    stats = request.result
  return stats

def getDocs(session, entite, dossier, status, start, end, csv_list, json_list, err_list, transit=False, count=False, list=False):
  interval = start + " - " + end
  etat_msg = "l'état est"
  if transit:
    etat_msg += " passé par"
  print("Récupérations des documents du flux %s dont %s %s pour l'entité (%s)" % (dossier, etat_msg, status, entite["id_e"]))

  request = Document(session).getByFilter(entite["id_e"], dossier, status, start, end, transit)
  if request.success:
    docs_json = request.result
    if count:
      csv_list.append([interval, entite['id_e'], entite['denomination'], entite['siren'], dossier, status, len(docs_json)])
      json_list.append({"id_e" : entite['id_e'], "dossier": dossier, "documents": len(docs_json), "status": status })
    elif list:
      for document in docs_json:
        csv_list.append([interval, entite['id_e'], entite['denomination'], entite['siren'],
          dossier, status, document["id_d"], document["last_action_date"]])
        json_list.append({"id_e" : entite['id_e'], "dossier": dossier, "document": document["id_d"], "status": status })
    else:
      print("warning: Rien à faire choisir entre --count ou --list")
  else:
    err_list.append(entite['id_e'])


def writeResults(csv_file, csv_list, json_file, json_list, list, merge):
  header = ['interval', 'id', 'denomination', 'siren', 'dossier', 'statut', 'documents']
  if list:
    header.append('date')

  with open(csv_file, 'a', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    # write the header
    if not merge:
      writer.writerow(header)
    # write multiple rows
    writer.writerows(csv_list)

  if json_file:
    with open(json_file, 'w', encoding='UTF8') as f:
      json.dump({ "docs" : json_list }, f)


def script_wrapper():
  xstart = datetime.now()
  parser = argparse.ArgumentParser()
  parser.add_argument("-e", "--env", type=str, help="Sélection de l'environnement", choices=['preprod','prod'], required=True)
  parser.add_argument("-s", "--status", type=str, nargs="*", help="Etats à filtrer", required=True)
  parser.add_argument("-f", "--flux", type=str, nargs="*", default=[], help="Sélection du flux (type de dossier)")
  parser.add_argument("-o", "--output", type=str, help="Nom des fichiers exportés (csv + json)")
  parser.add_argument("-g", "--org", type=str, help="Sélection de l'entité")
  #parser.add_argument("-d", "--date", type=str, help="Date des documents")
  parser.add_argument("-a", "--start", type=str, help="Date de début")
  parser.add_argument("-b", "--end", type=str, help="Date de fin")
  parser.add_argument("-n", "--count", action="store_true", help="Exporte le nombre de documents concernés")
  parser.add_argument("-l", "--list", action="store_true", help="Exporte tous les id_d des documents")
  parser.add_argument("-j", "--json", action="store_true", help="Exporte en plus le résultat dans un fichier json")
  parser.add_argument("-m", "--merge", action="store_true", help="Merge les résultats dans un fichier existant")
  parser.add_argument("-t", "--transit", action="store_true", help="Utilise passé par l'état plutôt que le dernier état")
  args = parser.parse_args()
  #Print summary script message witl all options values
  summaryMessage(args.status, args.transit, args.flux, args.org, args.start, args.end, args.output)
  #Call main method with parameters
  find(env=args.env, org=args.org, output=args.output, flux=args.flux, status=args.status,
    start=args.start, end=args.end, count=args.count, list=args.list, json=args.json,
    merge=args.merge, transit=args.transit)

  xend = datetime.now()
  delta = xend - xstart
  msg = f"info : script exécuté en {delta.seconds // 60} minutes et {delta.seconds % 60} secondes"
  print(msg)

def find(env, org=None, output="result", flux=None, status=None, start="2015-01-01",
  end=datetime.now().strftime("%Y-%m-%d"), count=True, list=False, json=False, merge=False, transit=False):
 #Get parameters from config file ~/.pastell-admin
  config = getConfiguration()

  json_file = '%s.json' % (output)
  csv_file = '%s.csv' % (output)

  if os.path.isfile(csv_file) and not merge:
    os.remove(csv_file)
  if os.path.isfile(json_file):
    os.remove(json_file)

  server = config[env]['server']
  user = config[env]['login']
  pwd = config[env]['password']

  session = Session(server,  user, pwd)
  #Check if session is valid
  if not session.valid:
    exit()

  csv_list = [] # used for csv file output
  json_list = [] # used for json file output
  err_list = [] # used for static tmp error file

  #Get stats from Pastell API
  stats_entites_json = getStats(session, org)
  if stats_entites_json:
    # Boucle sur les entités
    for index in stats_entites_json:
      stats = stats_entites_json[index]
      #Boucle sur tous les types de flux
      for dossier in stats['flux']:
        # Filtre optionnel sur les flux
        if dossier in flux or not flux:
          #Boucle sur les statuts
          for _status in status:
            if _status in stats['flux'][dossier]:
              #Récupération individuelle de tous les documents concernés avec pagination (1000 documents)
              getDocs(session, stats['info'], dossier, _status, start, end, csv_list, json_list, err_list, transit, count, list)

    writeResults(csv_file, csv_list, json_file, json_list, list, merge)

if __name__ == '__main__':
  script_wrapper()

