# Classes jeux bot

# -*- coding: utf-8 -*-

from collections import Counter
import random
import yaml

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
		self.question = ""
		self.answer = ""
        
	def add_questions(self,fic) : 
		with open (fic,"r",encoding="utf-8") as fic_questions :
			self.questions.update(yaml.safe_load(fic_questions))

	def create_question(self, ) :
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
			self.mots.extend(voc.read().split(','))
            
	def create_anag(self) :
		self.answer = random.choice(self.mots)
		liste = list(self.answer)
		mix = random.sample(liste,len(liste))
		self.anag = ''.join(mix)
