
import numpy

def levenshtein(token1, token2):
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
            if (token1[t1-1] == token2[t2-1]):
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

    printDistances(distances, len(token1), len(token2))
    return distances[len(token1)][len(token2)]

class RequeteCommande(object) :

    def __init__(self, mode) :
        self.choix_on = False
        self.choix = []
        self.memoire_requete = None
        self.message_reponses = []
        self.mode = mode

    def display_code(self, code, langage):
        '''
        '''
        return f"```{langage}\n{code}\n```"

    def get_matching_list(self, commande_req, liste_commandes) :
        '''
        '''
        liste_match = []
        for commande in liste_commandes :
            if commande_req in commande :
                liste_match.append(commande)
            else :
                for fragment in commande.split("::") :
                    if levenshtein(commande_req, commande) <= 2 :
                        liste_match.append(commande)
                        break
        return liste_match

    def lancer_requete(self, bdd, commande, type_inf) :
        '''
        '''
        if commande in bdd:
            if not type_inf:
                descr = bdd[commande]['description']['texte']
                self.message_reponses.append(f"{commande} :\n{descr}")
                try :
                    code_descr = bdd[commande]['description']['code']
                    self.message_reponses.append(self.display_code(code_descr, self.mode))
                except (KeyError):
                    pass
            else :
                type_info = type_inf.lower()

                if type_info == "parametres" :
                    try :
                        self.message_reponses.append(f"{bdd[commande]['parametres']}")
                    except (KeyError) :
                        self.message_reponses.append(f"Pas de paramètre pour la commande : {commande}")

                elif type_info == "exemple" :
                    try :
                        input = bdd[commande]['exemple']['input']
                        self.message_reponses.append(f"input :")
                        self.message_reponses.append(self.display_code(input, self.mode))
                        try :
                            output = bdd[commande]['exemple']['output']
                            self.message_reponses.append(f"output :")
                            self.message_reponses.append(self.display_code(output, self.mode))
                        except (KeyError):
                            self.message_reponses.append(f"Pas d'output précisé.")
                    except (KeyError):
                        self.message_reponses.append(f"Pas d'exemple pour la commande {commande}.")

                else :
                    raise ValueError
        else :
            resultats = self.get_matching_list(commande, bdd.keys())
            if len(resultats) != 0 :
                self.choix = resultats
                liste_numerotee = '\n'.join([str(resultat[index]+1)+' - '+resultat for resultat in resultats]) #variable créée car le '\n' posait problème dans l'expression fstring qui suit
                self.message_reponses.append(f"Aucun match, vouliez-vous dire (répondez par le numéro de la commande recherchée): \n\{liste_numerotee}")
                self.choix_on = True
                self.memoire_requete = type_inf
            else :
                self.message_reponses.append(f"Commande complètement inconnue ! On a tous nos failles...")
