'''
Classe représentant une requête sur une base de données de documentation
et fonction levenshtein
'''

# -*- coding: utf-8 -*-

import numpy

def levenshtein(token1, token2):
    '''
    Calcule la distance de levenshtein entre 2 tokens (token1, token2)
    renvoie la distance
    @credit https://blog.paperspace.com/implementing-levenshtein-distance-word-autocomplete-autocorrect/
    '''
    distances = numpy.zeros((len(token1) + 1, len(token2) + 1))

    for t1 in range(len(token1) + 1):
        distances[t1][0] = t1

    for t2 in range(len(token2) + 1):
        distances[0][t2] = t2

    a = 0
    b = 0
    c = 0

    for t1 in range(1, len(token1) + 1):
        for t2 in range(1, len(token2) + 1):
            if (token1[t1 - 1] == token2[t2 - 1]):
                distances[t1][t2] = distances[t1 - 1][t2 - 1]
            else:
                a = distances[t1][t2 - 1]
                b = distances[t1 - 1][t2]
                c = distances[t1 - 1][t2 - 1]

                if (a <= b and a <= c):
                    distances[t1][t2] = a + 1
                elif (b <= a and b <= c):
                    distances[t1][t2] = b + 1
                else:
                    distances[t1][t2] = c + 1

    return distances[len(token1)][len(token2)]

class RequeteCommande(object) :
    '''
    Classe RequeteCommande : permet de faire des requêtes sur des bases de
    données de documentation, et de garder
    mode = le langage de la documentation (cpp, python...)
    choices_on = True si des propositions de commandes proches sont en cours (default False)
    choices = les commandes proches
    choices_nb = le nombre de commandes proches trouvées
    request_memory = stockage du type d'info demandé (exemple/paramètre)
    message_responses = liste de messages de réponse à envoyer en retour à la requête
    display_start = indice à partir duquel montrer 20 commandes (pour les propositions de commandes proches)
    '''
    def __init__(self, mode) :

        self.choices_on = False
        self.choices = []
        self.choices_nb = 0
        self.request_memory = None
        self.message_responses = []
        self.mode = mode
        self.display_start = 0

    def display_code(self, code, langage):
        '''
        Renvoie une string qui s'affichera comme du code sur discord
        code : le code à mettre en forme
        langage : le langage du code
        '''
        return f"```{langage}\n{code}\n```"

    def get_matching_list(self, commande_req, liste_commandes) :
        '''
        Renvoie la liste des commandes proches d'une commande
        commande_req : commande en entrée
        liste_commandes : liste de toute les commandes dans lesquelles chercher
        '''
        liste_match = []
        for commande in liste_commandes :
            if all(token in commande for token in commande_req.split()) :
                liste_match.append(commande)
            else :
                for fragment in commande.split("::") :
                    if levenshtein(commande_req, commande) <= 1 :
                        liste_match.append(commande)
                        break

        return liste_match

    def lancer_requete(self, bdd, commande, type_inf) :
        '''
        lance une requête à partir d'une commande
        bdd : base de données (dict of dict) dans laquelle chercher
        commande : nom de la commandes
        type_info : infos précises rechercher (parametres, exemple etc...)
        '''
        if commande in bdd :
            # pas d'info précise, retourne la description de la commande
            if not type_inf :
                descr = bdd[commande]['description']['texte']
                self.message_responses.append(f"{commande} :\n{descr}")
                try :
                    code_descr = bdd[commande]['description']['code'] #cas où il y a du code dans la description
                    self.message_responses.append(self.display_code(code_descr, self.mode))
                except (KeyError):
                    pass

            # info précise demandée
            else :
                type_info = type_inf.lower().replace('è','e')

                if type_info == "parametres" :
                    try :
                        self.message_responses.append(f"{bdd[commande]['parametres']}")
                    except (KeyError) :
                        self.message_responses.append(f"Pas de paramètre pour la commande : {commande}")

                elif type_info == "exemple" :
                    try :
                        input = bdd[commande]['exemple']['input']
                        self.message_responses.append(f"input :")
                        self.message_responses.append(self.display_code(input, self.mode))
                        try :
                            output = bdd[commande]['exemple']['output']
                            self.message_responses.append(f"output :")
                            self.message_responses.append(self.display_code(output, self.mode))
                        except (KeyError):
                            self.message_responses.append(f"Pas d'output précisé.")
                    except (KeyError):
                        self.message_responses.append(f"Pas d'exemple pour la commande {commande}.")

                else :
                    raise ValueError

        #cas de la commande non trouvée dans la bdd  :
        # on cherche s'il y a des commandes proches, puis on les propose
        # (20 à la fois si trop de résultats à cause de la limite discord)
        else :
            self.choices = self.get_matching_list(commande, bdd.keys())
            self.choices_nb = len(self.choices)

            #s'il existe des commandes proches
            if self.choices_nb != 0 :
                list_results = '\n'.join([str(self.choices.index(resultat) + 1) + ' - ' + resultat for resultat in self.choices[0:20]]) #variable créée car le '\n' posait problème dans l'expression fstring qui suit
                self.message_responses.append(f"Aucun match, vouliez-vous dire (répondez par le numéro de la commande recherchée): \n{list_results}")
                if self.choices_nb > 20 :
                    self.message_responses.append("(répondez **\"next\"** pour voir les autres résultats)")
                self.choices_on = True
                self.request_memory = type_inf #sauvegarder le type d'info demandé
                #(pour si l'utilisateur choisit une commande parmi celles trouvées)

            #s'il n'existe pas de commandes proches
            else :
                self.message_responses.append(f"Commande complètement inconnue ! On a tous nos failles...")
