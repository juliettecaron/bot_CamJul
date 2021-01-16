'''
Bot Discord pour le serveur Plurital

Utile :
- Donne des informations sur les devoirs des différentes sections
- Génère la documentation d'un langage de programmation

Divertissant :
- Propose des jeux (quiz, anagramme)

Et bien sûr, envoie des gifs !
'''

# -*- coding: utf-8 -*-

from discord.ext.commands import Bot
import giphy_client
import json
import os
from requeteCode import *
from games import *

discord_token = os.getenv('DISCORD_TOKEN')
giphy_token = os.getenv('GIPHY_TOKEN')

#utilisation de l'API Giphy pour pouvoir générer des gifs
api = giphy_client.DefaultApi()

async def search_gifs(keyword):
	'''
	Fonction pour rechercher des gifs dans la base Giphy
	Arg : 'keyword' -> le mot-clé qui servira à trouver un gif pertinent
	Renvoie le lien d'un gif sélectionné au hasard parmi les + pertinents
	'''
	result = api.gifs_search_get(giphy_token, keyword, limit=5, rating='g')
	result_list = list(result.data)
	gif = random.choices(result_list)
	return gif[0].url

#stockage des données pour les devoirs et la doc. cpp
with open("files/devoirs.yaml", 'r', encoding="utf-8") as fic_dev:
	devoirs = yaml.safe_load(fic_dev)

with open("files/docs/cpp.json", 'r', encoding="utf-8") as fic_in:
	doc_cpp = json.load(fic_in)

with open("files/docs/python.json", 'r', encoding="utf-8") as fic_in:
	doc_py = json.load(fic_in)

#initialisation d'un objet RequeteCommande
requete = RequeteCommande(mode = "")

#initialisation d'une liste de jeux
list_games = []

#initialisation des objets représentant les jeux et chargement des données pour ces jeux
quiz = Quiz()
quiz.add_questions("files/quiz")
list_games.append(quiz)

anagram = Anagram()
anagram.add_voc_anag("files/mots.txt")
list_games.append(anagram)

#on établit qu'une commande adressée au bot doit commencer par !
bot = Bot(command_prefix = '!')

#-------------------------

#Suppression de la commande 'help' par défaut (pour pouvoir la personnaliser)
bot.remove_command('help')

help_dict = { "devoirs" : f":calendar: **INFORMATIONS SUR LES DEVOIRS** (exercices, projets, partiels...)\n\
\n__Commande__ : **!devoirs <niveau> <matiere>**\n\n__Exemple__ : !devoirs m2 java",
	"anag" : f":placard: ANAGRAMME\n\nL'anagramme d'un mot du vocabulaire du TAL vous est proposé, \
	\nvous devez retrouver le mot original. Vous gagnez un point à chaque fois que vous trouvez un mot !\n\n__Commande__ : **!anag**",
	"quiz" : f":books: QUIZ\n\nLe bot vous pose une question, à vous de trouver la réponse ! \
	\nVous gagnez un point à chaque bonne réponse !\n\n__Commande__ : **!quiz** ou **!quiz <theme>** pour une question sur un thème spécifique\n\n*Thèmes disponibles : {', '.join(quiz.themes)}*",
	"scores" : f":chart_with_upwards_trend: SCORES\n\nPour connaître les scores des jeux !\n\
	\n__Commande__ : **!scores** pour tous les scores, **!scores <jeu>** pour les scores d'un jeu spécifique !",
	"cpp" : f":placard: C++\n\n__Commande__ : \n\n**!cpp <commande>** pour une description de la commande\
	\n**!cpp <commande> <parametres>**  pour les paramètres de la commande\
	\n**!cpp <commande> <exemple>**  pour un exemple d'utilisation de la commande\n",
	"python" : f":snake: Python\n\n__Commande__ : \n\n**!python <commande>** pour une description de la commande\
	\n**!python <commande> <parametres>**  pour les paramètres de la commande\
	\n**!python <commande> <exemple>**  pour un exemple d'utilisation de la commande" }

@bot.command(name = 'help')
async def help_bot(ctx, commande = None):
		'''
		Fonction associée à la commande !help
		Arg : 'commande' (None par défaut)

		Affiche les consignes pour l'utilisation du bot
		-> les consignes d'une commande si elle est précisée, sinon toutes les consignes
		'''
		if commande :
			try :
				await ctx.send(help_dict[commande])
			except (KeyError) :
				await ctx.send(f"La commande \"{commande}\" n'existe pas\nListe des commandes : !{' / !'.join(help_dict.keys())}")
		else :
			await ctx.send(f":arrow_right:  **UTILISATION DU BOT**  :arrow_left: \n----------------------------------------\n\
		    \n{help_dict['devoirs']}\n----------------------------------------\n:game_die: **JEUX**\n\
			\n{help_dict['anag']}\n\
			\n{help_dict['quiz']}\n\
			\n{help_dict['scores']}\
			\n----------------------------------------\n:computer: **DOCUMENTATION**\n\nPour obtenir de la documentation sur différents langages de programmation\n\
			\n{help_dict['cpp']}\
			\n{help_dict['python']}\
			\n----------------------------------------")

#------------------------------

#dictionnaires de correspondances pour les matières et les niveaux (regex)
corres_mat = {r"python\b|(langages? de )?scripts?\b" : "langages de script", r"fouilles?( de textes?)?\b" : "fouille de texte",
				r"lexico|termino(logie)?" : "lexicologie", r"mod(é|e)l(isation)?s?( des connaissances)?\b" : "modelisation",
				r"calcul(abilit(é|e))?\b" : "calculabilite", r"r(é|e)seau(x)?( de neurone(s)?)?\b" :"reseaux de neurones",
				r"s(é|e)mantique( des textes)?\b" : "semantique", r"xml|document(s)? structur(é|e)s?\n" : "documents structures",
				"programmation objet" : "java", r"(traitements? )?statistiques?( de corpus)?" : "statistiques"}

corres_niv = {r"m(aster)?\s?1" : "m1", r"m(aster)?\s?2" : "m2"}

@bot.command(name = 'devoirs')
async def infos_cours(ctx, niv=None, mat=None):
	'''
	Fonction associée à la commande !devoirs
	Affiche les informations disponibles (devoirs/partiels/projets) pour un niveau et une matière
	(s'ils sont spécifiés et présents dans les données)

	-> Si aucun argument : affiche les consignes pour la commande !devoirs
	-> Si seul le niveau est précisé : affiche les matières de ce niveau et rappelle les consignes de la commande
	(si le niveau n'est pas dans la base : rappelle les consignes et affiche les niveaux disponibles)
	-> Si le niveau et la matière sont précisés : affiche les devoirs (s'il y en a)
	(si le niveau n'est pas dans la base : rappelle les consignes et affiche les niveaux disponibles ;
	si la matière n'est pas dans la base : rappelle les consignes et affiche les matières disponibles)
	'''
	if not niv and not mat :
		await ctx.send(help_dict['devoirs'])

	elif niv :
		niv = niv.lower()
		for exp in corres_niv :
			if re.search(exp, niv) :
				niv = corres_niv[exp]
		if niv in devoirs :
			if devoirs[niv] == None :
				await ctx.send(f"Aucune matière enregistrée pour le niveau {niv} (pour le moment !)\n\n{help_dict['devoirs']}")

			elif mat :
				mat = mat.lower()
				for exp in corres_mat :
					if re.search(exp, mat) :
						mat = corres_mat[exp]
				if mat in devoirs[niv] :
					if devoirs[niv][mat] == None :
						await ctx.send("Aucun devoir enregistré pour ce cours.")
						gif = await search_gifs("lucky")
						await ctx.send(gif)
					else :
						for dev in devoirs[niv][mat] :
							await ctx.send(f"Pour le {dev} : {devoirs[niv][mat][dev]}")
			else :
				await ctx.send(f"Les matières du niveau {niv} sont :\n {' :star: '.join([dev for dev in devoirs[niv]])}\n\nPour connaître les devoirs, tapez !devoirs {niv} <matiere>")
		else :
			await ctx.send(f"Les niveaux disponibles sont : {' :star: '.join([niv for niv in devoirs])}\n\n{help_dict['devoirs']}")

#------------------------------

#dictionnaire de correspondances pour les noms des jeux
corres_games = {r"anag(ram(me)?)?s?\b" : anagram, r"quiz+e?\b" : quiz}

@bot.command(name = 'anag')
async def anag_game(ctx) :
	'''
	Fonction associée à la commande !anag
	-> La commande lance le jeu "anagram" (un anagramme est proposé, il faut retrouver le mot original)
	Si le jeu est déjà en cours : rappelle l'anagramme en cours
	Sinon : génère et affiche un nouvel anagramme

	(Voir games.py)
	'''
	if anagram.on == True :
		await ctx.send(f"Déjà en cours : de quel mot >>> {anagram.anag} <<< est-il l'anagramme ?")
	else :
		anagram.on = True
		anagram.create_anag()
		await ctx.send(f"Anagramme :   :arrow_right:   {anagram.anag}   :arrow_left:	 Quel est le mot original ?")

@bot.command(name = 'quiz')
async def quiz_game(ctx, theme=None):
	'''
	Fonction associée à la commande !quiz
	Arg : 'theme' (None par défaut)

	-> La commande lance le jeu "quiz" (une question est affichée, il faut trouver la réponse)
	Si le jeu est déjà en cours : rappelle la question en cours
	Sinon : génère et affiche une nouvelle question

	Si un thème est précisé, génère et affiche une question de ce thème
		-> Si le thème n'est pas dans la base, affiche les thèmes disponibles

	(Voir games.py)
	'''
	if quiz.on == True :
		await ctx.send(f"Déjà en cours ! Question : {quiz.question}")
	else :
		if theme :
			theme = theme.lower()
			if theme in quiz.themes :
				quiz.on = True
				quiz.create_question(theme)
				await ctx.send(f"Question : {quiz.question}")
			else :
				await ctx.send(f"Vous ne pouvez pas choisir le thème {theme} !")
				await ctx.send(f"Thèmes disponibles :  {' :star: '.join(quiz.themes)}")
		else :
			quiz.on = True
			quiz.create_question()
			await ctx.send(f"Question : {quiz.question}")

@bot.command(name = 'scores')
async def scores(ctx, game = None) :
	'''
	Fonction associée à la commande !scores
	Arg : 'game' (None par défaut)

	Affiche les scores :
	-> d'un jeu spécifique s'il est précisé en argument,
	-> de tous les jeux sinon

	Si l'arg. ne correspond pas à un jeu disponible, rappelle les consignes de la commande

	(Voir games.py)
	'''
	def print_scores(one_game) :
		'''
		Sous-fonction qui définit les messages à afficher pour les scores d'un jeu
		Arg : 'one_game', le nom d'un jeu
		Renvoie une chaîne correspondant au message à afficher
		(Les scores de chaque joueur si le jeu est dans la base, les consignes de la commande sinon)
		'''
		to_print = ""
		if one_game.scores == {} :
			to_print = f"Aucun score enregistré pour le jeu > {game.name} < ! Lancez-le vite : :arrow_right: {game.start} :arrow_left:"
		else :
			to_print = f"Scores {game.name} :"
			for pers in one_game.scores.most_common() :
				to_print += f"\n:arrow_forward:  {pers[0]} : {one_game.scores[pers[0]]}"
		return to_print

	if not game :
		for game in list_games :
			await ctx.send(print_scores(game))
	else :
		game = game.lower()
		for game_re in corres_games :
			if re.search(game_re, str(game)) :
				game = corres_games[game_re]

		if game in list_games :
			await ctx.send(print_scores(game))
		else :
			await ctx.send("Utilisation de la commande : !scores <jeu>\n---------------")
			await ctx.send(f"Jeux disponibles : :game_die: {' :game_die: '.join([game.name for game in list_games])}")
			await ctx.send(f"Lancement des jeux : :video_game: {' :video_game: '.join([game.start for game in list_games])}")

#------------------------------

@bot.command(name = 'cpp')
async def get_cpp(ctx, com = None, type_inf = None):
	'''
	Fonction associée à la commande !cpp
	Genère et affiche la documentation du langage C++

	Arg : 'com' - la commande à chercher dans la doc (None par défaut),
	'type_inf' - l'information précise à chercher, "parametres" ou "exemple" (None par défaut)

	Renvoie le help de !cpp si la commande est mal formée
	si la commande n'est pas trouvée telle quelle dans la bdd, propose des commandes proches
	l'utilisateur peut en choisir une en renvoyant son numéro

	Requete effectuée via un objet RequeteCommande
	(Voir requeteCode.py)

	'''
	if com :
		commande = com.lower()
		global requete
		requete = RequeteCommande(mode = "cpp")
		try :
			requete.lancer_requete(doc_cpp, com, type_inf)
			for message in requete.message_responses :
				await ctx.send(message)
		except ValueError :
			await help_bot(ctx, "cpp")
	else :
		await help_bot(ctx, "cpp")

#--------------------------

@bot.command(name = 'python')
async def get_python(ctx, com = None, type_inf = None):
	'''
	Fonction associée à la commande !cpp
	Genère et affiche la documentation du langage C++

	Arg : 'com' - la commande à chercher dans la doc (None par défaut),
	'type_inf' - l'information précise à chercher, "parametres" ou "exemple" (None par défaut)

	Renvoie le help de !cpp si la commande est mal formée
	si la commande n'est pas trouvée telle quelle dans la bdd, propose des commandes proches
	l'utilisateur peut en choisir une en renvoyant son numéro

	Requete effectuée via un objet RequeteCommande
	(Voir requeteCode.py)

	'''
	if com :
		commande = com.lower()
		global requete
		requete = RequeteCommande(mode = "python")
		try :
			requete.lancer_requete(doc_py, com, type_inf)
			for message in requete.message_responses :
				await ctx.send(message)
		except ValueError :
			await help_bot(ctx, "python")
	else :
		await help_bot(ctx, "python")

#--------------------------

@bot.event
async def on_message(message) :
	'''
	Fonction qui permet au bot d'analyser les messages du serveur (hors commandes)
	Arg : 'message' -> chaque message du serveur

	Permet de reconnaître les réponses justes des jeux,
	d'afficher un message pour les gagnants (avec un petit gif) et d'augmenter leurs scores

	Permet de récupérer les réponses le choix d'un utilisateur parmi les propositions de
	commandes proches / d'afficher les commandes proches suivantes
	'''

	#le bot ne prend pas en compte les messages des autres bots
	if message.author.bot :
		return

	for game in list_games :
		if game.on :
			if game.answer in message.content.lower() :
				game.on = False
				game.scores[message.author.name] += 1
				await message.channel.send(f"Bravo {message.author.name} ! :partying_face:  Score : {game.scores[message.author.name]}")
				gif = await search_gifs("bravo")
				await message.channel.send(gif)

	#si des propositions de commandes proches sont en cours
	if requete.choices_on :
		#si le message est un numéro
		if message.content.rstrip().isdigit():
			try :
				commande = requete.choices[int(message.content) - 1]
				if requete.mode == "cpp" :
					await get_cpp(message.channel, commande, requete.request_memory)
				elif requete.mode == "python" :
					await get_python(message.channel, commande, requete.request_memory)
			except IndexError :
				await message.channel.send("Ce chiffre ne fait pas partie de la liste des commandes proposées.")
		#si le message est une instruction next
		elif "next" in message.content :
			requete.display_start = requete.display_start + 20
			#s'il reste des commandes proches à afficher
			if requete.display_start < requete.choices_nb :
				#afficher les 20 prochaines commandes (ou moins si il en reste moins de 20)
				list_results = '\n'.join([str(requete.choices.index(resultat) + 1) + ' - ' + resultat for resultat in requete.choices[requete.display_start:requete.display_start + 20]])
				await message.channel.send(f"suite commandes :  \n{list_results}")
				if requete.choices_nb > requete.display_start + 20 :
					await message.channel.send("(répondez **\"next\"** pour voir les autres résultats)")

	#ligne qui permet de faire fonctionner le bloc précédé de @bot.event ET les blocs précédés de @bot.command
	await bot.process_commands(message)

#lancement du bot
bot.run(discord_token)
