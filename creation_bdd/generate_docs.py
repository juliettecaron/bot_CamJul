# -*- coding: utf-8 -*-

'''
Classes de convertisseur pour uniformiser des données de DOCUMENTATION
en une base de données json
'''

import lxml.etree as ET
import lxml.html
import json
from collections import defaultdict
import re

class ConvertDocCPP():
    '''
    Convertisseur pour du code html de documentation CPP
    fichier_path : le chemin du fichier json à convertir
    bdd_converti : la base de données convertie au format dict of dict
    bdd_string : la base de données convertie au format json version string, prête a écrire
    filtres : filtres pour les chemins des pages à ne pas traiter
    '''

    def __init__(self):
        self.fichier_path = ""
        self.bdd_converti = defaultdict(dict)
        self.bdd_string = ""
        self.filtres = ["header", "language", "index"]

    def get_commande(self, contenu_arbre):
        '''
        Renvoie le nom de la commande CPP à partir d'un fragment de doc HTML
        contenu_arbre : le noeud racine du fragment
        '''
        commande_brut = contenu_arbre.xpath('.//h1')[0].text_content().rstrip()
        commande_nett = re.sub('<[^>]*>', '', commande_brut)
        commande_nett = re.sub('^(std::)', '', commande_nett)
        commande_nett = commande_nett.lower()
        return commande_nett

    def get_description(self,contenu_arbre):
        '''
        Renvoie la description (texte ou texte+code) d'une commande  CPP à partir d'un
        fragment de doc HTML
        contenu_arbre : le noeud racine du fragment
        returns - description : dictionnaire contenant les éléments de la description et leur valeur
        '''
        description = {}
        description_node =  contenu_arbre.xpath('.//p')[0]
        description['texte'] = description_node.text_content()
        noeud_suivant = description_node.getnext()
        while noeud_suivant.tag != "h3" :
            if noeud_suivant.tag == "p" :
                description['texte'] += noeud_suivant.text_content()
            if "class" in noeud_suivant.attrib and noeud_suivant.attrib['class'] == "cpp source-cpp":
                description['code'] = noeud_suivant.text_content()
                break
            noeud_suivant = noeud_suivant.getnext()
        return description

    def get_param(self,contenu_arbre):
        '''
        Trouve les paramètres d'une commande CPP, s'ils sont précisés
        contenu_arbre : le noeud racine du fragment
        returns - string représentant la description des paramètres
        '''
        param_node = contenu_arbre.xpath(".//table[preceding-sibling::h3[1][@id='Parameters']]")
        if param_node :
            return param_node[0].text_content()

    def get_exemple(self,contenu_arbre):
        '''
        Trouve un code d'exemple d'utilisation d'une commande CPP, s'il y en a
        contenu_arbre : le noeud racine du fragment
        returns - dict contenant l'input et son code, et optionnellement l'output et son code
        '''
        exemple= {}
        exemple_node = contenu_arbre.xpath(".//div[@class='t-example']/div")
        if exemple_node:
            exemple["input"] = exemple_node[0].text_content()
            if len(exemple_node)>1 :
                exemple["output"] = exemple_node[1].text_content()
            return exemple

    def get_commande_info(self,contenu_html) :
        '''
        Renvoie l'ensemble des infos cherchées sur une commande CPP présentée dans une page de documentation
        contenu_html : les données html (non parsées) de la page html
        returns - commande_info : defaultdict(dict), contient les informations sur la commande
        '''
        commande_info = defaultdict(dict)
        contenu_arbre = lxml.html.fromstring(contenu_html)
        try :
            commande = self.get_commande(contenu_arbre)
            commande_info[commande]['description'] = self.get_description(contenu_arbre)
            param = self.get_param(contenu_arbre)
            if param is not None:
                commande_info[commande]['parametres'] = param
            exemple = self.get_exemple(contenu_arbre)
            if exemple is not None:
                commande_info[commande]['exemple'] = exemple

        except (AttributeError, IndexError):
            return {}

        return commande_info

    def convert(self, fichier_json):
        '''
        Converti un fichier json de paire chemin/bloc_html de documentation CPP
        en une base de données filtrée et uniformisée
        fichier_json : le fichier à convertir
        output : attribut bdd_converti <-- base de données converties au format dict of dict
                 attribut bdd_string <-- base de données converties au format json/ version string
        '''
        self.fichier_path = fichier_json
        with open(fichier_json, "r") as fichier_in:
            self.fichier_parse = json.load(fichier_in)

        for page_chemin, page_contenu in self.fichier_parse.items():
            if not any(filtre in page_chemin for filtre in self.filtres):
                self.bdd_converti.update(self.get_commande_info(page_contenu))

        self.bdd_string = json.dumps(self.bdd_converti, indent=4)

class ConvertDocPython():
    '''
    Convertisseur pour du code html de documentation Python
    fichier_path : le chemin du fichier json à convertir
    bdd_converti : la base de données convertie au format dict of dict
    bdd_string : la base de données convertie au format json version string, prête a écrire
    filtres : filtres pour les chemins des pages à ne pas traiter
    '''
    def __init__(self):
        self.fichier_path = ""
        self.bdd_converti = defaultdict(dict)
        self.bdd_string = ""
        self.filtres = ["index"]

    def get_commande(self, commande_node):
        '''
        Renvoie le nom de la commande Python à partir d'un fragment de doc HTML
        '''
        commande_brut = commande_node.attrib['id'].rstrip()
        commande_nett = re.sub('<[^>]*>', '', commande_brut)
        commande_nett = re.sub('^(std::)', '', commande_nett)
        commande_nett = commande_nett.lower()
        return commande_nett

    def get_description(self, commande_node):
        '''
        Renvoie la description (texte ou texte+code) d'une commande Python à partir d'un
        fragment de doc HTML
        contenu_node : le noeud <dt> contenant l'id de la commande
        returns - description : dictionnaire contenant les éléments de la description et leur valeur
        '''
        description = {}
        description_node =  commande_node.xpath('./following-sibling::dd[1]//p[1]')[0]
        description['texte'] = description_node.text_content()
        noeud_suivant = description_node.getnext()
        while noeud_suivant is not None:
            if noeud_suivant.tag == "p" :
                description['texte'] += noeud_suivant.text_content()
            if noeud_suivant.tag == "pre":
                description['code'] = noeud_suivant.text_content()
                break
            noeud_suivant = noeud_suivant.getnext()
        return description

    def get_param(self, commande_node, description):
        '''
        Trouve les paramètres d'une commande Python, s'ils sont précisés
        contenu_node : le noeud <dt> contenant l'id de la commande
        returns - string représentant la description des paramètres
        '''
        parametres = []
        full_commande = commande_node.findall('./code')[0].text_content()
        params = re.findall(r'\((.*?)\)', full_commande)
        if params :
            params = params[0].split(",")
            sentences = description.split(".")
            for param in params :
                param_norm = param.replace("[", "").replace("]", "").split("=")[0]
                parametres.append(f"{param}    {'. '.join([sentence for sentence in sentences if param_norm in sentence])}")

            return "\n".join(parametres)

    def get_exemple(self,commande_node):
        '''
        Trouve un code d'exemple d'utilisation d'une commande Python, s'il y en a
        contenu_arbre : le noeud <dt> contenant l'id de la commande
        returns - dict contenant l'input et son code (pas d'output car inclu dans le même cadre pour la doc Python)
        '''
        exemple = {}
        exemple_node = commande_node.xpath('./following-sibling::dd/pre[1]')
        if exemple_node :
            exemple["input"] = exemple_node[0].text_content()
            return exemple

    def get_commande_info(self, commande_node) :
        '''
        Renvoie l'ensemble des infos cherchées sur une commande Python présentée dans une page de documentation
        commande_node : le noeud <dt> contenant l'id de la commande
        returns - commande_info : defaultdict(dict), contient les informations sur la commande
        '''
        commande_info = defaultdict(dict)

        try :
            commande = self.get_commande(commande_node)
            commande_info[commande]['description'] = self.get_description(commande_node)
            param = self.get_param(commande_node,commande_info[commande]['description']['texte'])
            if param is not None:
                commande_info[commande]['parametres'] = param
            exemple = self.get_exemple(commande_node)
            if exemple is not None:
                commande_info[commande]['exemple'] = exemple

        except (AttributeError, IndexError, KeyError):
            return {}

        return commande_info

    def get_commandes_page(self, content_html) :
        '''
        extrait toutes les commandes d'une page html de doc python, et leurs infos filtrées
        content_html :  les données html (non parsées) de la page html
        returns - commandes_page : dictionnaire contenant les commandes et leurs informations
        '''
        commandes_page = {}
        content_tree = lxml.html.fromstring(content_html)
        for commande in content_tree.findall(".//dt") :
            commandes_page.update(self.get_commande_info(commande))
        return commandes_page

    def convert(self, fichier_json) :
        '''
        Converti un fichier json de paire chemin/bloc_html de documentation Python
        en une base de données filtrée et uniformisée
        fichier_json : le fichier à convertir
        output : attribut bdd_converti <-- base de données converties au format dict of dict
                 attribut bdd_string <-- base de données converties au format json/ version string
        '''

        self.fichier_path = fichier_json
        with open(fichier_json, "r") as fichier_in:
            self.fichier_parse = json.load(fichier_in)

        for page_path, page_content in self.fichier_parse.items() :
            if not any(filtre in page_path for filtre in self.filtres) :
                self.bdd_converti.update(self.get_commandes_page(page_content))

        self.bdd_string = json.dumps(self.bdd_converti, indent=4)

##Pour lancer sur un fichier CPP, par exemple :
#convertisseur = ConvertDocCPP()
#convertisseur.convert("cpp_original.json")
#with open("cpp.json","w") as fichier_out:
    #fichier_out.write(convertisseur.bdd_string)

##Pour lancer sur un fichier Python, par exemple :
#convertisseur = ConvertDocPython()
#convertisseur.convert("python_original.json")
#with open("python.json","w") as fichier_out:
    #fichier_out.write(convertisseur.bdd_string)
