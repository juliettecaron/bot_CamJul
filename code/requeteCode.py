
class RequeteCommande(object) :

    def __init__(self, mode) :
        self.choix = False
        self.message_reponses = []
        self.mode = mode

    def display_code(self, code, langage):
    	return f"```{langage}\n{code}\n```"

    def get_matching_list(self, commande, liste_commandes) :
        return []

    def lancer_requete(self, bdd, com, type_inf) :
        if commande in bdd:
            if not type_inf:
                descr = bdd[commande]['description']['texte']
                self.message_reponses.append(f"{commande} : {descr}")
                try :
                    code_descr = bdd[commande]['description']['code']
                    self.message_reponses.append(self.display_code(code_descr, "cpp"))
                except (KeyError):
                    pass
            else :
                type_info = type_inf.lower()
                if type_info == "exemple" :
                    try :
                        input = bdd[commande]['exemple']['input']
                        self.message_reponses.append(f"input :")
                        self.message_reponses.append(self.display_code(input, "cpp"))
                        try :
                            output = bdd[commande]['exemple']['output']
                            self.message_reponses.append(f"output :")
                            self.message_reponses.append(self.display_code(output, "cpp"))
                        except (KeyError):
                            self.message_reponses.append(f"Pas d'output précisé.")
                    except (KeyError):
                        self.message_reponses.append(f"Pas d'exemple la commande {commande}.")

                if type_info == "parametres" :
                    try :
                        self.message_reponses.append(f"{bdd[commande]['parametres']}")
                    except (KeyError) :
                        self.message_reponses.append(f"Pas de paramètre pour la commande : {commande}")

                else :
                    raise ValueError
        else :
            resultats = self.get_matching_list(commande, bdd.keys())
            if len(resultats) != 0 :
                self.message_reponses.append(f"Aucun match, vouliez-vous dire : ")
            else :
                self.message_reponses.append(f"Commande complètement inconnue ! On a tous nos failles...")
