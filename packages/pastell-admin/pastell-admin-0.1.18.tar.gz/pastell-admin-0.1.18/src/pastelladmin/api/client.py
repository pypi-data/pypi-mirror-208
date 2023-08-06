#!/usr/bin/env python3
from ast import Assert, Param
from distutils.log import error
from fcntl import F_DUPFD
import requests, json
from requests.auth import HTTPBasicAuth
from urllib.parse import urlencode
from datetime import datetime

class Session():
    """
    Classe permettant d'instancier les informations de session
    Serveur + Authentification
    """
    def __init__(self, server, user, password):
        """
        Usage :
            from pastell.api import Session
            session = Session(url_pastell, user, password)
            if session.valid:
                ...

        Args:
            server ( str ): URL du serveur Pastell
            user ( str ) : user du compte Pastell à utiliser
            password ( str ) : Mot de passe associé
        """
        self.server = server
        self.auth = HTTPBasicAuth(user, password)
        #Check if session is valid
        version = Version(self).get()
        self.valid =  version.success == True
        if self.valid:
            print(f" ------------------------\nPastell version {version.result['version']} \n ------------------------")
        else:
            print(version.result)



class PastellSession():
    """
    Classe permettant de stocker les informations de session
    Serveur + Authentification
    Cette classe est ensuite étendue par toutes les classes suivantes
    ce qui permet de partager les propriétés server et auth
    """
    def __init__(self, session):
        self.server = session.server
        self.auth = session.auth

class Result():

    def __init__(self, success, result):
        self.success = success
        self.result = result

class Version(PastellSession):

    def __init__(self, session):
        super().__init__(session)

    def get(self):
        url = f"https://{self.server}/api/v2/version"
        request = requests.get(url, auth=self.auth)
        if request.status_code == 200:
            result = json.loads(request.text)
            success = True
        else:
            result = request.text
            success = False

        return Result(success, result)

class Role(PastellSession):

    def __init__(self, session):
        super().__init__(session)

    def get(self):
        url = f"https://{self.server}/api/v2/role"
        request = requests.get(url, auth=self.auth)
        if request.status_code == 200:
            result = json.loads(request.text)
            success = True
        else:
            result = request.text
            success = False

        return Result(success, result)


class Utilisateur(PastellSession):

    def __init__(self, session):
        super().__init__(session)

    def create(self, params):
        url = f"https://{self.server}/api/v2/utilisateur"
        request = requests.post(url, data=params, auth=self.auth)
        if request.status_code == 201:
            result = json.loads(request.text)
            success = True
        else:
            result = request.text
            success = False

        return Result(success, result)

    def delete(self, id_u):
        url = f"https://{self.server}/api/v2/utilisateur/{id_u}"
        request = requests.delete(url, auth=self.auth)
        result = json.loads(request.text)
        if "result" in result and result["result"] == 'ok':
            result = json.loads(request.text)
            success = True
        else:
            result = request.text
            success = False

        return Result(success, result)

    def removeRole(self, id_u, id_e, role):
        url = f"https://{self.server}/api/v2/utilisateur/{id_u}/role?role={role}&id_e={id_e}"
        request = requests.delete(url, auth=self.auth)
        if request.status_code == 200:
            result = json.loads(request.text)
            success = True
        else:
            result = request.text
            success = False

        return Result(success, result)

    def addRole(self, id_u, role):
        url = f"https://{self.server}/api/v2/utilisateur/{id_u}/role"
        request = requests.post(url, data={"role": role}, auth=self.auth)
        if request.status_code == 201:
            result = json.loads(request.text)
            success = True
        else:
            result = request.text
            success = False

        return Result(success, result)

    def getRoles(self, id_u):
        url = f"https://{self.server}/api/v2/utilisateur/{id_u}/role"
        request = requests.get(url, auth=self.auth)
        if request.status_code == 200:
            result = json.loads(request.text)
            success = True
        else:
            result = request.text
            success = False

        return Result(success, result)



class Stat(PastellSession):

    def __init__(self, session):
        super().__init__(session)

    def get(self, id_e=None, type=None):
        url = f"https://{self.server}/api/v2/document/count"
        if id_e or type:
            params = {}
            if id_e:
                params["id_e"] = id_e
            if type:
                params["type"] = type
            url = f"{url}?{urlencode(params)}"
        request = requests.get(url, auth=self.auth)
        if request.status_code == 200:
            result = json.loads(request.text)
            success = True
        else:
            result = request.text
            success = False

        return Result(success, result)


class Entity(PastellSession):

    def __init__(self, session):
        super().__init__(session)

    def getAllWithStatus(self):
        """
        Méthode permettant de retourner tous les organismes actifs(entités) Pastell

        Returns:
             dict: with 2 keys success (bool) and result (dict with 3 lists)
        """
        stats = Stat(self).get()
        success = False
        if stats.success:
            active = []
            no_active = []
            for ide, obj in stats.result.items():
                if obj["info"]["is_active"] == "1":
                    active.append(obj["info"])
                else:
                    no_active.append(obj["info"])
            print(f"info: {len(no_active)} entités sont inactives et {len(active)} entités sont actives")
            succcess = True
            result = {'all': [*active, *no_active],'active': active, 'no_active': no_active}
        else:
            result = stats.result
        return Result(True, result)



    def getAll(self):
        """
        Méthode permettant de retourner tous les organismes (entités) Pastell

        Returns:
             dict: with 2 keys success (bool) and result (list)
        """

        url = f"https://{self.server}/api/v2/entite"
        request = requests.get(url, auth=self.auth)

        if request.status_code == 200:
            result = json.loads(request.text)
            success = True
        else:
            result = request.text
            success = False

        return Result(success, result)

    def getFilles(self, id_e, tree=None):
        """
        Méthode permettant de retourner tous les organismes filles (entités/services)  d'une entité Pastell

        Returns:
             dict: with 2 keys success (bool) and result (list)
        """
    #Interdit pour entité racine 0
        assert int(id_e) > 0

        entities = [id_e]
        work = [id_e]
        level = 1
        calls = 0
        erreur = False
        while len(work) > 0 and not erreur:
            newLevel = []
            finished = []
            for ide in work:
                request = Entity(self).detail(ide)
                if request.success:
                    calls +=1
                    filles = []
                    if len(request.result["entite_fille"]) > 0:
                        filles = [e["id_e"] for e in request.result["entite_fille"]]
                        entities.extend(filles)
                        newLevel.extend(filles)
                    #print (f"level : {level} : call {calls} : {ide} --> {filles}")
                    finished.append(ide)
                else:
                    erreur = True
                    result = request.result
                    break
            if not erreur:
                for id in finished:
                    work.remove(id)
                work.extend(newLevel)
                level += 1
        entities.sort(key = int)
        result = [{"id_e": entity} for entity in entities]
        return Result(not erreur, result)









    def detail(self, id_e):
        """
        Méthode permettant de retourner le détail d'un organisme donné (fourni par id_e)

        Args:
            id_e ( str ): identifiant de l'entité.

        Returns:
            dict: with 2 keys success (bool) and result (dict)
        """
        assert isinstance(id_e, str)
        url = f"https://{self.server}/api/v2/entite/{id_e}"
        request = requests.get(url, auth=self.auth)
        if request.status_code == 200:
            result = json.loads(request.text)
            success = True
        else:
            result = request.text
            success = False

        return Result(success, result)

class Connector(PastellSession):

    def __init__(self, session):
        super().__init__(session)

    def __addToDict(self, item, dictionary):
        if not item["id_e"] in dictionary.keys():
            dictionary[item["id_e"]] = { item["libelle"] : [item["id_ce"]] }
        else:
            if not item["libelle"] in dictionary[item["id_e"]]:
                dictionary[item["id_e"]][item["libelle"]] = [item["id_ce"]]
            else:
                dictionary[item["id_e"]][item["libelle"]].append(item["id_ce"])

    def getAll(self, scope, id_connecteur=None, outputFormat='list'):
        """
        Get all connectors with one id_connecteur (option) (eg 'depot-pastell')
        for one id_e or all organisms

        Args:
            scope (str): 'all' or id_e
            id_connecteur (str): id_connecteur eg "depot-pastell"
            outputFormat (str): 'list' or 'dict'. Defaults = 'list'

        Returns:
            dict: with 2 keys success (bool) and result (dict)
            result dic structure item :{id_e:{"lib_connector":[id_ce]}} or
            result list structure = raw response from Pastell
            sample result dict : {"123":{"myfirst_connector":["47"]}, {"mysecond_connector":["48"]},"124":{...}}
        """
        url = f"https://{self.server}/api/v2/entite/{scope}/connecteur"
        if scope == 'all':
            url = f"https://{self.server}/api/v2/connecteur/{scope}/"
            if id_connecteur:
                url = f"https://{self.server}/api/v2/connecteur/{scope}/{id_connecteur}"

        request = requests.get(url, auth=self.auth)
        if request.status_code == 200:
            success = True
            connectors = json.loads(request.text)
            if outputFormat == 'list':
                if not id_connecteur:
                    #raw response from PAstell
                    result = connectors
                else:
                    #raw response from PAstell filtered by id_connecteur
                    result = [connector for connector in connectors if connector["id_connecteur"] == id_connecteur]
            elif outputFormat == 'dict':
                #create dict id_e:libelle:[id_ce]
                result = {}
                for connector in connectors:
                    if not id_connecteur or (id_connecteur and connector["id_connecteur"] == id_connecteur):
                        self.__addToDict(connector, result)

        else:
            success = False
            result = request.text

        return Result(success, result)

    def delete(self, id_e, id_ce):
        url = f"https://{self.server}/api/v2/entite/{id_e}/connecteur/{id_ce}"
        request = requests.delete(url, auth=self.auth)
        result = json.loads(request.text)
        if request.status_code == 200:
            print(f"info: Connecteur: {id_ce} supprimé avec succès")

    def update(self, id_e, id_ce, parameters, file=None):
        """_summary_

        Args:
            id_e (_type_): _description_
            id_ce (_type_): _description_
            parameters (_type_): _description_

        Returns:
            _type_: _description_
        """
        if file:
            urlConnecteur = f"https://{self.server}/api/v2/entite/{id_e}/connecteur/{id_ce}/file/definition"
            responseConnecteur = requests.post(urlConnecteur, data=parameters, files=file, auth=self.auth)
        else:
            urlConnecteur = f"https://{self.server}/api/v2/entite/{id_e}/connecteur/{id_ce}/content/"
            responseConnecteur = requests.patch(urlConnecteur, data=parameters, auth=self.auth)

        success = False
        if responseConnecteur.ok:
            success = True
        else:
            print(f"error: Creation config connecteur {id_ce} KO erreur:{responseConnecteur.text}")

        return Result(success, None)

    def create(self, id_e, definition):
        """
        Creation du connecteur sans sa configuration pour l'IDE sélectionnée

        Args:
            id_e (str): Identifiant de l'entité
            definition (dict): Dictionnaire de clés valeurs

        Returns:
            dict: with 2 keys success (bool) and result (str) id_ce created
        """

        url = f"https://{self.server}/api/v2/entite/{id_e}/connecteur/"
        request = requests.post(url, data=definition, auth=self.auth)
        if request.ok:
            data = json.loads(request.text)
            result = data["id_ce"]
            success = True
        else:
            success = False
            result = request.text

        return Result(success, result)

    def action(self, id_e, id_ce, action):
        url = f"https://{self.server}/api/v2/entite/{id_e}/connecteur/{id_ce}/action/{action}"
        request = requests.post(url, auth=self.auth)
        if request.ok:
            data = json.loads(request.text)
            result = data["last_message"]
            success = data["result"]
        else:
            success = False
            result = request.text

        return Result(success, result)

    def detail(self, id_e, id_ce):
        url = f"https://{self.server}/api/v2/entite/{id_e}/connecteur/{id_ce}"
        request = requests.get(url, auth=self.auth)
        if request.ok:
            result = json.loads(request.text)
            success = True
        else:
            success = False
            result = request.text

        return Result(success, result)


class Association(PastellSession):

    def __init__(self, session):
        super().__init__(session)


    def getByEntity(self, id_e, id_ce=None, flux=None):
        """
        Returns list off all flux associations for organism and in option, with the connector identified by his id_ce

        Args:
            id_e (str): Identifiant de l'organisme
            id_ce (str, optional): Identifiant du connecteur. Defaults to None.
            flux (_type_, optional): Identifiant du flux. Defaults to None.

        Returns:
            dict: with 2 keys success (bool) and result (list) of associations
        """
        url = f"https://{self.server}/api/v2/entite/{id_e}/flux"
        request = requests.get(url, auth=self.auth)
        if request.status_code == 200:
            data = json.loads(request.text)
            if id_ce:
                associations = []
                for association in data:
                    if flux:
                        if association["id_ce"] == id_ce and association["flux"] == flux:
                            associations.append(association)
                    else:
                        if association["id_ce"] == id_ce:
                            associations.append(association)
            else:
                associations = data

            success = True
            result = associations
        else:
            result = request.text
            success = False

        return Result(success, result)

    def delete(self, id_e, id_fe):
        url = f"https://{self.server}/api/v2/entite/{id_e}/flux?id_fe={id_fe}"
        request = requests.delete(url, auth=self.auth)
        result = json.loads(request.text)
        if request.status_code == 200:
            print(f"info: Suppression de l'association {id_fe} pour l'entité ({id_e} effectuée)")

    def create(self, id_e, flux, id_ce, type):
        """
        Méthode permettant d'associer un connecteur à un flux

        Args:
            id_e (str): Identifiant de l'organisme
            flux (str): Identifiant du flux
            id_ce (str): Identifiant du connecteur
            type (str): type de connecteur (GED...)
        """
        data = {"type": type}
        # Association avec le flux fournis en paramètre
        url = f"https://{self.server}/api/v2/entite/{id_e}/flux/{flux}/connecteur/{id_ce}/"
        response = requests.post(url, data=data, auth=self.auth)
        if response.ok:
            print(f"info: Association connecteur {id_ce} ok type_flux:{flux}, id_e:{id_e}")
        else:
            print(f"error: Association connecteur {id_ce} KO erreur:{response.text}")


class Document(PastellSession):

    def __init__(self, session):
        super().__init__(session)

    def detail(self, id_e, id_d):
        url = f"https://{self.server}/api/v2/entite/{id_e}/document/{id_d}"
        request = requests.get(url, auth=self.auth)
        success = None
        if request.status_code == 200:
            result = json.loads(request.text)
            success = True
        else:
            result = request.text
            success = False

        return Result(success, result)

    def update(self, id_e, id_d, data):
        url = f"https://{self.server}/api/v2/entite/{id_e}/document/{id_d}"
        request = requests.patch(url, auth=self.auth, data=data)
        success = None
        if request.status_code == 200:
            result = json.loads(request.text)
            success = True
        else:
            result = request.text
            success = False

        return Result(success, result)

    def action(self, id_e, id_d, action):
        url = f"https://{self.server}/api/v2/entite/{id_e}/document/{id_d}/action/{action}"
        request = requests.post(url, auth=self.auth)
        success = None
        if request.status_code == 201:
            result = json.loads(request.text)
            success = True
        else:
            result = request.text
            success = False

        return Result(success, result)

    def getByFilter(self, id_e, dossier=None, status=None, start=None, end=None, transit=False, pagination=1000 ):
        #check types
        date_format = "%Y-%m-%d"
        for date in (start, end):
            if date:
                assert datetime.strptime(date, date_format)
        assert type(pagination) == int
        assert type(transit) == bool
        success = None
        # On positionne l'offset à 0 pour la première requête
        offset = 0
        completed = False
        parameters = {}
        result = []
        #Construct URL parameters
        if dossier:
            parameters["type"] = dossier
        if status and transit:
            parameters["etatTransit"] = status
            if start:
                parameters["state_begin"] = start
            if end:
                parameters["state_end"] = end
        elif status and not transit:
            parameters["lastetat"] = status
            if start:
                parameters["last_state_begin"] = start
            if end:
                parameters["last_state_end"] = end

        while not completed:
            pagination_parameters = {
                'limit': pagination,
                'offset': offset
            }
            url = f"https://{self.server}/api/v2/entite/{id_e}/document"
            request = requests.get(url, params={**parameters, **pagination_parameters}, auth=self.auth)
            if request.status_code == 200:
                docs_json = json.loads(request.text)
                if len(docs_json) > 0:
                    # On augmente l'offset de la limite pour une éventuelle prochaine requête
                    offset += pagination
                    result.extend(docs_json)
                else:
                    # 0 enregistrement donc on a tout récupérer
                    completed = True
                    success = True
                if len(docs_json) < pagination:
                    completed = True
                    success = True
            else:
                result = f"erreur de récupération des documents pour l'entité {id_e}"
                success = False
                break

        return Result(success, result)








