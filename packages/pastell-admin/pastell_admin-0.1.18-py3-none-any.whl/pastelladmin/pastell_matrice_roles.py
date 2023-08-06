#!/usr/bin/env python3
import csv
import random
import string
from datetime import datetime
import argparse
from .api.client import Session, Utilisateur, Role
from .shared.configuration import getConfiguration

"""
Ce script permet de générer un fichier csv avec la matrice des roles Pastell

  Args:
    option -e or --env => to select environnement execution (prod or preprod). default is preprod
    option -c or --csv => Chemin et nom du fichier csv généré. Optional


  Usage :
    ./role_matrice.py --env=preprod --csv=matrice.csv

"""

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


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
  parser.add_argument("-c", "--csv", help="Fichier csv en sortie. /tmp/matrice-YYYY-MM-DD.csv par défaut")
  args = parser.parse_args()

  matrice(env=args.env,csv=args.csv)

  xend = datetime.now()
  delta = xend - xstart
  msg = f"info : script exécuté en {delta.seconds // 60} minutes et {delta.seconds % 60} secondes"
  print(msg)

def matrice(env, csv=None):
  #Get parameters from config file ~/.pastell-admin
  config = getConfiguration()

  ladate = datetime.now()
  xdate = ladate.strftime("%Y-%m-%d")
  ENV = env
  OUTPUT = csv or "/tmp/matrice-%s.csv" % xdate
  SERVER = config[ENV]['server']
  user = config[ENV]['login']
  pwd = config[ENV]['password']

  csv_headers = ['role', 'droit']
  #START PROCESS
  session = Session(SERVER,  user, pwd)
  #Check if session is valid
  if not session.valid:
    exit()
  csv_list = []
  #Create fake user
  paramUser = {"id_e" : "0", "login": "fakeuser", "nom": "foo", "prenom": "bar", "email": "fake@megalis.bretagne.bzh","password": get_random_string(8)}
  clientUser = Utilisateur(session).create(params=paramUser)
  #print(clientUser.success)
  if clientUser.success and "id_u" in clientUser.result:
    id_u = clientUser.result["id_u"]
    #Get infos from Pastell API
    request = Role(session).get()
    if request.success:
      roles = request.result
      for r in roles:
        role = r["role"]
        #Ajout du role au fakeuser
        clientRole = Utilisateur(session).addRole(id_u, role)
        #print(role, clientRole.success)
        clientRoles = Utilisateur(session).getRoles(id_u)
        for _role in clientRoles.result:
          droits = _role["droits"]
          for droit in droits:
            csv_list.append([role, droit])

        #Suppression du role au fakeuser
        clientRole = Utilisateur(session).removeRole(id_u, id_e="0", role=role)


      clientUser = Utilisateur(session).delete(id_u)
      writeResults(OUTPUT, csv_list, csv_headers)

  else:
    print(clientUser.result)

if __name__ == '__main__':
  script_wrapper()





