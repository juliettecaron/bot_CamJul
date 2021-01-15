
import numpy as np

def levenshtein(seq1, seq2):
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = np.zeros ((size_x, size_y))
    for x in xrange(size_x):
        matrix [x, 0] = x
    for y in xrange(size_y):
        matrix [0, y] = y

    for x in xrange(1, size_x):
        for y in xrange(1, size_y):
            if seq1[x-1] == seq2[y-1]:
                matrix [x,y] = min(
                    matrix[x-1, y] + 1,
                    matrix[x-1, y-1],
                    matrix[x, y-1] + 1
                )
            else:
                matrix [x,y] = min(
                    matrix[x-1,y] + 1,
                    matrix[x-1,y-1] + 1,
                    matrix[x,y-1] + 1
                )
    return (matrix[size_x - 1, size_y - 1])

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
