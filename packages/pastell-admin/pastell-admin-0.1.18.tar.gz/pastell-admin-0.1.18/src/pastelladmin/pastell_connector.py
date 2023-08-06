#!/usr/bin/env python3
import  json, re
import os, tempfile
from datetime import datetime
import argparse
from .api.client import Session, Entity, Association, Connector
from .shared.configuration import getConfiguration

"""
Ce script permet de gérer des connecteurs pour une instance Pastell:

     - statut d'un connecteur (absence, présence, doublons) unitaire ou en masse
     - création de connecteurs et association unitaire ou en masse
     - Mise à jour d'un connecteur unitaire ou en masse
     - Mise à jour et création si nécessaire d'un connecteur unitaire ou en masse
     - Désassociation d'un connecteur unitaire ou en masse
     - Suppression d'un connecteur unitaire ou en masse

  Args:
    option -e or --env => to select environnement execution (prod or preprod). default is preprod
    option -a or --action => Mandatory : choose between [create, update, append, dissociate, delete, status]
    option -o or --org => pastell entity to filter. eg : 1. Optional
    option -f or --flux => Type de dossier (flux). Exemple autres-studio-sans-tdt; Mandatory for action (dissociate and delete without source file )
    option -s or --source => fichier json contenant la définition du connecteur ou la liste des connecteurs à supprimer [{"id_e":"", "id_ce"},]
    option -l or --libelle => Libellé du connecteur. Mandatory for status, dissociate, delete
    option -t or --type => type de connecteur (eg. GED). Mandatory for dissociate and delete
    option -i or --id_connector => id_connecteur (eg. depot-pastell). Mandatory for dissociate and delete
    option -d or --details => A utiliser avec l'action status. Pour afficher les id_e des entités concernées.
    option -r or --recursive => : précise si les entités filles sont également concernées. A associer avec --org=


  Usage :
    ./pastell_connector.py --env=preprod --action=status --libelle=ged-megalis-opendata-sans-tdt --details
    ./pastell_connector.py --env=preprod --org=7 --action=create --flux=autres-studio-sans-tdt --source=connectors/opendata-sans-tdt.json
    ./pastell_connector.py --env=preprod --org=7 --action=update --flux=autres-studio-sans-tdt --source=connectors/opendata-sans-tdt.json
    ./pastell_connector.py --env=preprod --org=7 --recursive --action=append --flux=autres-studio-sans-tdt --source=connectors/opendata-sans-tdt.json
    ./pastell_connector.py --env=preprod --org=7 --action=dissociate --flux=autres-studio-sans-tdt --type=GED --libelle=ged-megalis-opendata-sans-tdt --id_connector=depot-pastell
    ./pastell_connector.py --env=preprod --org=7 --action=delete --type=GED --libelle=ged-megalis-opendata-sans-tdt --id_connector=depot-pastell# ./pastell_connector.py --env=preprod --org=7 --action=delete --source=connectors/connectors_to_delete.json

"""

def variables_substitution(o):
  result = o.copy()
  for key, val in o.items():
    variable = re.findall('{{(.*?)}}', val)
    if variable and os.getenv(variable[0]):
      result[key] = os.getenv(variable[0])
  return result

def taskConnectorFor(session, scope, action, connector_template, delete_list, flux_associes, lib_connector, type_connector, id_connector, details, recursive, scheduler, file):
  global connector
  if scope == 'all':
    # Get all entities from Pastell API
    request = Entity(session).getAll()
    if request.success:
      entities = request.result
    else:
      print(f"error : {request.result}")
  elif recursive:
    request = Entity(session).getFilles(scope)
    if request.success:
      entities = request.result
    else:
      print(f"error : {request.result}")
  else:
    # Create list with the id_e passed in parameter
    entities = [{"id_e": scope }]
  # DELETE action WITH LIST
  if action == 'delete' and delete_list:
    for connector in delete_list:
      deleteConnector(connector["id_e"],connector["id_ce"])
  else:
    #Get complete list of connectors with id_connecteur type (eg depot-pastell) for the scope (one id_e if not recursive option or all id_e)
    if recursive and len(entities) > 1:
      scope = 'all'
    request = Connector(session).getAll(scope, id_connecteur=id_connector, outputFormat='dict')
    connectors = {}
    if request.success:
      connectors = request.result

    #Filter entities list for create action and delete action
    # create action for entities without the lib_connector
    # update action for entities with the lib_connector
    if action in ['status', 'create', 'update', 'delete']:
      #select existing id_e with this connector
      existing_same_connectors = [ide for ide, v in connectors.items() if lib_connector in v.keys()]
      doublons = [ide for ide, v in connectors.items() if lib_connector in v.keys() and len(v[lib_connector]) > 1 ]
      if action in ('create', 'status'):
        print(f"info : {len(existing_same_connectors)} entité(s) dispose(nt) déjà du connecteur {lib_connector}")
        if len(doublons) > 0:
          print(f"warning : connecteur {lib_connector} en doublons pour {len(doublons)} entité(s)")
        #Filter entities to include only entities with not this connector
        entities = [{"id_e": entity["id_e"]} for entity in entities if entity["id_e"] not in existing_same_connectors]
        if len(entities) == 0:
          if scope == 'all':
            print(f"info : toutes les entités disposent déjà du connecteur {lib_connector}")
        else:
           print(f"warning : {len(entities)} n'ont pas encore le connecteur {lib_connector}")
        if action == 'status':
          tirets = "--------------------------------------------------------------------"
          #if input("Voulez-vous afficher le détail? (y/n): ").lower().strip()[:1] == "y":
          if details:
            if len(existing_same_connectors) > 0:
              print(f"info: entités déjà pourvues : \n{existing_same_connectors}\n{tirets}")
            if len(doublons) > 0:
              print(f"info: Doublons : \n{doublons}\n{tirets}")
            if len(entities) > 0:
              print(f"info: Entités sans le connecteur : \n{[e['id_e'] for e in entities]}\n{tirets}")

      elif action in ['update', 'delete']:
        #Filter entities to include only entities with this connector
        entities = [{"id_e": ide} for ide in existing_same_connectors]


    #Sort entities by id_e ASC
    entities = sorted(entities, key=lambda x:int(x['id_e']))

    for entity in entities:
      id_e = entity["id_e"]
      #export id_e to os environnement to use it in connector template
      os.environ["ID_E"] = id_e
      #Check if connector libelle exists for this entity
      if id_e in connectors.keys() and lib_connector in connectors[id_e].keys():
        id_ce_list = connectors[id_e][lib_connector]
        # Its possible have many connectors with the same libelle
        if len(id_ce_list) > 1:
          print(f"warning : des doublons existent pour le connecteur {lib_connector} de l'entité {id_e}")
        # get only the first id_ce
        id_ce = id_ce_list[0]
        if action in ['append', 'update']:
          print(f"info : entité : {id_e} : mise à jour du connecteur : {id_ce}")
          if type_connector == "transformation":
            parameters = {'file_name': 'definition.json'}
          else:
            parameters = variables_substitution(connector_template["parameters"])
          result = Connector(session).update(id_e, id_ce, parameters, file)
          if result and flux_associes:
            for flux in flux_associes:
              Association(session).create(id_e, flux, id_ce, type_connector)
          if result.success and scheduler:
            Connector(session).action(id_e, id_ce, "purge-async")

        elif action == 'dissociate':
          #Dissociate only with the flux specified
          for flux in flux_associes:
            deleteAssociations(session, id_e, id_ce, flux)
        elif action == 'delete':
          deleteConnector(session, id_e, id_ce)
        elif action == 'create':
          # Does not occurs because entities are filtered for this connector
          print(f"warning : le connecteur existe déjà : {id_ce} pour l'entité : {id_e}")
      else:
        if action in ['create', 'append']:
          #Only create connector if does not exists yet
          print(f"info : création du connecteur pour l'entité : {id_e}")
          createConnecteur(session, id_e, connector_template, flux_associes, lib_connector, type_connector, scheduler, file)
        elif action in ['delete', 'update']:
          # Does not occurs because entities are filtered for this connector
          print(f"warning: Aucun connecteur de type {type_connector}:{id_connector} et libellé {lib_connector} trouvé pour l'entité ({id_e})")


def deleteConnector(session, id_e, id_ce):
  #delete associations for this connector
  deleteAssociations(session, id_e, id_ce)
  # then delete connector
  Connector(session).delete(id_e, id_ce)


def deleteAssociations(session, id_e, id_ce, flux=None):
  #Get all Flux/connector associations for the connector with this id_ce and optional flux if specified
  request = Association(session).getByEntity(id_e, id_ce, flux)
  if request.success:
    associations = request.result
  else:
    print(f"error : {request.result}")
  #Delete all association for this connector
  for association in associations:
    if flux:
      print(f"info : désassociation du connecteur {id_ce} avec le flux {association['flux']}")
    else:
      print(f"info: désassociation du connecteur {id_ce} avec tous les flux")
    Association(session).delete(id_e, association["id_fe"])


def createConnecteur(session, id_e, connector_template, flux_associes, lib_connector, type_connector, scheduler, file):
  definition = variables_substitution(connector_template["definition"])
  if type_connector == "transformation":
    parameters = {'file_name': 'definition.json'}
  else:
    parameters = variables_substitution(connector_template["parameters"])
  #Etape 1 Creation du connecteur sans sa configuration pour l'IDE sélectionnée
  request = Connector(session).create(id_e, definition)
  if request.success:
    id_ce = request.result
  else:
    print(f"error : {request.result}")

  if id_ce:
    # ETAPE 2: configuration du connecteur précédemment créé avec injection des paramètres
    request = Connector(session).update(id_e, id_ce, parameters, file)
    if request.success and flux_associes:
      for flux in flux_associes:
        Association(session).create(id_e, flux, id_ce, type_connector)
    if request.success and scheduler:
      Connector(session).action(id_e, id_ce, "purge-async")

  else:
    print(f"error : Création du connecteur {lib_connector} KO erreur:{request.result}")

def script_wrapper():
  xstart = datetime.now()
  parser = argparse.ArgumentParser()
  parser.add_argument("-e", "--env", type=str, help="Sélection de l'environnement", choices=['preprod','prod'])
  parser.add_argument("-a", "--action", type=str, help="Sélection de l'action", choices=['create','update', 'append', 'dissociate', 'delete', 'status'])
  parser.add_argument("-o", "--org", type=str, help="Sélection de l'entité")
  parser.add_argument("-f", "--flux", type=str, help="Sélection du flux (type de dossier)")
  parser.add_argument("-s", "--source", type=str, help="fichier json contenant la définition du connecteur ou la liste des connecteurs à supprimer")
  parser.add_argument("-l", "--libelle", type=str, help="Libellé du connecteur")
  parser.add_argument("-t", "--type", type=str, help="type de connecteur (eg. GED)")
  parser.add_argument("-i", "--id_connector", type=str, help="id_connecteur (eg. depot-pastell)")
  parser.add_argument("-d", "--details", action="store_true", help="A utiliser avec l'action status. Pour afficher les id_e des entités concernées")
  parser.add_argument("-r", "--recursive", action="store_true", help="Sélection de l'environnement")
  parser.add_argument("-c", "--scheduler", action="store_true", help="Launch connecteur with existing asynchrone scheduler")
  args = parser.parse_args()

  connector(env=args.env, action=args.action, org=args.org, flux_associes=args.flux, source=args.source,
    type_connector=args.type, id_connector=args.id_connector, lib_connector=args.libelle,
    details=args.details, recursive=args.recursive, scheduler=args.scheduler)

  xend = datetime.now()
  delta = xend - xstart
  msg = f"info : script exécuté en {delta.seconds // 60} minutes et {delta.seconds % 60} secondes"
  print(msg)


def connector(env, action, org=None, flux_associes=None, source=None, type_connector=None, id_connector=None, lib_connector=None, details=None, recursive=None, scheduler=None):
  #Get parameters from config file ~/.pastell-admin
  config = getConfiguration()

  delete_list = None
  connector_template = None
  file_transformation = None

  #Export var to OS environnement
  for var, value in config[env].items():
    if var not in ('server', 'login', 'password'):
      os.environ[var] = value

  #Check for mandatory parameters
  assert action in ['status', 'create', 'append', 'update', 'delete', 'dissociate']
  #if create or append then source is mandatory
  if flux_associes:
      flux_associes = flux_associes.split(",")
  else:
    flux_associes = []
  if action in ['create', 'append', 'update']:
    assert source != None
    # Opening JSON file
    f = open(source)
    # returns JSON object as dictionary
    connector_template = json.load(f)
    # Récupération des propriétés du connecteur & substitution des variables
    assert all( key in connector_template.keys() for key in ["definition", "parameters"])
    assert all(key in connector_template["definition"].keys() for key in ["libelle", "id_connecteur", "type"])
    lib_connector = connector_template["definition"]["libelle"]
    id_connector = connector_template["definition"]["id_connecteur"]
    type_connector = connector_template["definition"]["type"]
    if type_connector == "transformation":
      parameters = connector_template["parameters"]
      #Create temporary file from parameters
      tmpfile = tempfile.NamedTemporaryFile()
      with open(tmpfile.name, "w") as f:
        f.write(json.dumps(parameters))
      file_transformation = {'file_content': open(tmpfile.name, "rb")}



  #if delete
  elif action == 'delete':
    assert (lib_connector and type_connector and id_connector) or source
    if source:
      f = open(source)
      # returns JSON object as dictionary
      delete_list = json.load(f)
      # Chek if All items in delete_list contains keys id_ce and id_e
      assert all(key in item.keys() for item in delete_list for key in ["id_ce", "id_e"])
  elif action == 'dissociate':
    assert (lib_connector and type_connector and id_connector and len(flux_associes)>0)
  elif action == 'status':
    assert (lib_connector)


  server = config[env]['server']
  user = config[env]['login']
  pwd = config[env]['password']
  #Session used by all the script
  session = Session(server,  user, pwd)
  #Check if session is valid
  if not session.valid:
    exit()
  if action in ['status', 'create', 'append', 'dissociate', 'delete', 'update']:
    scope = 'all'
    if org:
      scope = org
    taskConnectorFor(session, scope, action, connector_template, delete_list, flux_associes, lib_connector, type_connector, id_connector, details, recursive, scheduler, file=file_transformation)
    if file_transformation and tmpfile:
      tmpfile.close()

if __name__ == '__main__':
  script_wrapper()



