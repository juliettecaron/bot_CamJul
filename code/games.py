'''
Classes représentant les jeux d'un bot
'''

# -*- coding: utf-8 -*-

from collections import Counter
import random
import yaml
import glob
import re

class Game :
	'''
	Représente un jeu, caractérisé par un nom ('name'), un nom de commande ('start'), 
	un statut ('on' : en cours = True, sinon False), une réponse ('answer' ; None par défaut),
	et un dictionnaire Counter() pour stocker les scores des joueurs
    '''
	def __init__(self) :
		self.name = ""
		self.start = ""
		self.on = False
		self.answer = None
		self.scores = Counter()
        
	def __repr__(self):
		return self.name

class Quiz(Game) :
	'''
	Hérite de la classe Game
	Représente le jeu 'quiz' (question -> réponse)

	Caractéristiques supplémentaires : un dictionnaire pour associer une question à une réponse ('question'),
	une liste de thèmes ('theme'), un dict. pour stocker les questions de chaque thème ('questions_theme'),
	une variable prévue pour la question en cours ('question')
    '''
	def __init__(self) :
		Game.__init__(self)
		self.name = "quiz"
		self.start = "!quiz"
		self.questions = {}
		self.themes = []
		self.questions_theme = {}
		self.question = ""
		self.answer = ""
        
	def add_questions(self, rep) : 
		'''
		Méthode pour ajouter des questions au quiz
		Arg : 'rep' -> le chemin + nom du répertoire contenant des fichiers de questions au format yaml
		(le nom d'un fichier doit respecter le format quiz_theme)

		Ajoute les questions et leurs thèmes à la base de données du quiz
		'''
		for name_file in glob.glob(f"{rep}/quiz_*.yaml") :
			with open(name_file, "r", encoding = "utf-8") as file :
				file_dic = yaml.safe_load(file) 
				self.questions.update(file_dic)
				theme = re.search(r"quiz_(.+).yaml", name_file)[1]
				self.themes.append(theme)
				self.questions_theme[theme] = list(file_dic.keys())

	def create_question(self, theme=None) :
		'''
		Méthode pour générer une question et une réponse
		Arg : 'theme' (None par defaut)

		Une question est choisie au hasard parmi les questions disponibles
		et est associée à l'attribut 'question' représentant la question en cours
		-> Question d'un thème spécifique si le thème est précisé 

		La réponse à cette question est associée à l'attribut "answer" 
		'''
		if theme : 
			self.question = random.choice(self.questions_theme[theme])
		else :
			self.question = random.choice(list(self.questions.keys()))
		self.answer = self.questions[self.question].lower()

				  
class Anagram(Game) :
	'''
	Hérite de la classe Game
	Représente le jeu 'Anagram' (un anagramme est généré, il faut retrouver le mot original)

	Caractéristiques supplémentaires : une liste de mots ('mots') pour les mots originaux,
	et une variable pour stocker l'anagramme généré à partir d'un mot ('anag')
    '''
	def __init__(self) :
		Game.__init__(self)
		self.name = "anagramme"
		self.start = "!anag"
		self.mots = []
		self.anag = ""
        
	def add_voc_anag(self, fic) : 
		'''
		Méthode pour ajouter des mots à la liste de mots du jeu
		Arg : 'fic' -> le chemin + nom du fichier txt contenant les mots (un mot par ligne)

		Ajoute les mots à la liste de l'attribut 'mots'
		'''
		with open (fic,"r", encoding="utf-8") as voc :
			self.mots.extend(voc.read().split('\n'))
            
	def create_anag(self) :
		'''
		Méthode pour choisir un mot et générer un anagramme

		Un mot est choisi au hasard parmi les mots disponibles et est associé à l'attribut 'answer',
		un anagramme de ce mot est ensuite créé et associé à l'attribut 'anag'
		'''
		self.answer = random.choice(self.mots)
		liste = list(self.answer)
		mix = random.sample(liste,len(liste))
		self.anag = ''.join(mix)
