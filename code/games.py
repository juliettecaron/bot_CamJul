# Classes jeux bot

# -*- coding: utf-8 -*-

from collections import Counter
import random
import yaml
import glob
import re

class Game :

	def __init__(self):
		self.name = ""
		self.start = ""
		self.on = False
		self.answer = None
		self.scores = Counter()
        
	def __repr__(self):
		return self.name

class Quiz(Game) :

	def __init__(self) :
		Game.__init__(self)
		self.name = "quiz"
		self.start = "!quiz"
		self.questions = {}
		self.themes = []
		self.questions_theme = {}
		self.question = ""
		self.answer = ""
        
	def add_questions(self,rep) : 
		for name_file in glob.glob(f"{rep}/quiz_*.yaml") :
			with open(name_file, "r", encoding = "utf-8") as file :
				file_dic = yaml.safe_load(file) 
				self.questions.update(file_dic)
				theme = re.search(r"quiz_(.+).yaml",name_file)[1]
				self.themes.append(theme)
				self.questions_theme[theme] = list(file_dic.keys())

	def create_question(self, theme=None) :
		if theme : 
			self.question = random.choice(self.questions_theme[theme])
		else :
			self.question = random.choice(list(self.questions.keys()))
		self.answer = self.questions[self.question].lower()

				  
class Anagram(Game) :

	def __init__(self) :
		Game.__init__(self)
		self.name = "anagramme"
		self.start = "!anag"
		self.mots = []
		self.anag = ""
        
	def add_voc_anag(self,fic) : 
		with open (fic,"r",encoding="utf-8") as voc :
			self.mots.extend(voc.read().split('\n'))
            
	def create_anag(self) :
		self.answer = random.choice(self.mots)
		liste = list(self.answer)
		mix = random.sample(liste,len(liste))
		self.anag = ''.join(mix)
