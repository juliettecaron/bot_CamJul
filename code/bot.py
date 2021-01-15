# Bot Discord

# -*- coding: utf-8 -*-

from discord.ext.commands import Bot
import giphy_client
import re
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
	'''
	#on recherche les gifs les + pertinents dans la base Giphy en fonction du mot-clé
	result = api.gifs_search_get(giphy_token, keyword, limit=5, rating='g')
	result_list = list(result.data)

	#un gif sera sélectionné au hasard parmi les plus pertinents
	gif = random.choices(result_list)
	return gif[0].url

with open("files/devoirs.yaml", 'r', encoding="utf-8") as stream:
	devoirs = yaml.safe_load(stream)

with open("files/docs/cpp.json", 'r', encoding="utf-8") as fic_in:
	doc_cpp = json.load(fic_in)

requete = RequeteCommande(mode="")

list_games = []

quiz = Quiz()
quiz.add_questions("files/quiz")
list_games.append(quiz)

anagram = Anagram()
anagram.add_voc_anag("files/mots.txt")
list_games.append(anagram)

bot = Bot(command_prefix = '!')

#-------------------------

bot.remove_command('help')

help_dict = { "devoirs" : f":calendar: **INFORMATIONS SUR LES DEVOIRS** (exercices, projets, partiels...)\n\
\n__Commande__ : **!devoirs <niveau> <matiere>**\n\n__Exemple__ : !devoirs m2 java",
	"anag" : f":placard: ANAGRAMME\n\nL'anagramme d'un mot du vocabulaire du TAL vous est proposé, \
	\nvous devez retrouver le mot original. Vous gagnez un point à chaque fois que vous trouvez un mot !\n\n__Commande__ : **!anag**",
	"quiz" : f":books: QUIZ\n\nLe bot vous pose une question, à vous de trouver la réponse ! \
	\nVous gagnez un point à chaque bonne réponse !\n\n__Commande__ : **!quiz** ou **!quiz <theme>** pour une question sur un thème spécifique\n\n*Thèmes disponibles : {', '.join(quiz.themes)}*",
	"scores" : f":chart_with_upwards_trend: SCORES\n\nPour connaître les scores des jeux !\n\
	\n__Commande__ : **!scores** pour tous les scores, **!scores <jeu>** pour les scores d'un jeu spécifique !",
	"cpp" : f":placard: C++\n\n__Commande__ : \n\n**!cpp <commande>** pour une description de la commande (...)\
	\n**!cpp <commande> <parametres>**  pour les paramètres de la commande\
	\n**!cpp <commande> <exemple>**  pour un exemple d'utilisation de la commande" }

@bot.command(name = 'help')
async def help_bot(ctx, commande = None):
		if commande :
			try :
				await ctx.send(help_dict[commande])
			except (KeyError) :
				await ctx.send(f"La commande \"{commande}\" n'existe pas\nListe des commandes : !{' / !'.join(help_dict.keys())}")
		else :
			await ctx.send(f":arrow_right:  UTILISATION DU BOT  :arrow_left: \n----------------------------------------\n\
		    \n{help_dict['devoirs']}\n----------------------------------------\n:game_die: **JEUX**\n\
			\n{help_dict['anag']}\n\
			\n{help_dict['quiz']}\n\
			\n{help_dict['scores']}\
			\n----------------------------------------\n:computer: DOCUMENTATION\n\nPour obtenir de la documentation sur différents langages de programmation\n\
			\n{help_dict['cpp']}\
			\n----------------------------------------")

#------------------------------


corres_mat = {r"python\b|(langages? de )?scripts?\b" : "langages de script", r"fouilles?( de textes?)?\b" : "fouille de texte",
				r"lexico|termino(logie)?" : "lexicologie", r"mod(é|e)l(isation)?s?( des connaissances)?\b" : "modelisation",
				r"calcul(abilit(é|e))?\b" : "calculabilite", r"r(é|e)seau(x)?( de neurone(s)?)?\b" :"reseaux de neurones",
				r"s(é|e)mantique( des textes)?\b" : "semantique", r"xml|document(s)? structur(é|e)s?\n" : "documents structures",
				"programmation objet" : "java", r"(traitements? )?statistiques?( de corpus)?" : "statistiques"}

corres_niv = {r"m(aster)?\s?1" : "m1", r"m(aster)?\s?2" : "m2"}

@bot.command(name = 'devoirs')
async def infos_cours(ctx, niv=None, mat=None):

	if not niv and not mat :
		await ctx.send(help_dict['devoirs'])

	elif niv :
		niv = niv.lower()
		for exp in corres_niv :
			if re.search(exp,niv) :
				niv = corres_niv[exp]
		if niv in devoirs :
			if devoirs[niv] == None :
				await ctx.send(f"Aucune matière enregistrée pour le niveau {niv} (pour le moment !)\n\n{help_dict['devoirs']}")

			elif mat :
				mat = mat.lower()
				for exp in corres_mat :
					if re.search(exp,mat) :
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

corres_games = {r"anag(ram(me)?)?s?\b" : anagram, r"quiz+e?\b" : quiz}

@bot.command(name = 'anag')
async def anag_game(ctx):
	if anagram.on == True :
		await ctx.send(f"Déjà en cours : de quel mot >>> {anagram.anag} <<< est-il l'anagramme ?")
	else :
		anagram.on = True
		anagram.create_anag()
		await ctx.send(f"Anagramme :   :arrow_right:   {anagram.anag}   :arrow_left:	 Quel est le mot original ?")

@bot.command(name='quiz')
async def quiz_game(ctx, theme=None):
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
async def scores(ctx, game=None) :

	def print_scores(one_game) :
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
			if re.search(game_re,str(game)) :
				game = corres_games[game_re]

		if game in list_games :
			await ctx.send(print_scores(game))
		else :
			await ctx.send("Utilisation de la commande : !scores <jeu>\n---------------")
			await ctx.send(f"Jeux disponibles : :game_die: {' :game_die: '.join([game.name for game in list_games])}")
			await ctx.send(f"Lancement des jeux : :video_game: {' :video_game: '.join([game.start for game in list_games])}")

#------------------------------

@bot.command(name = 'cpp')
async def get_cpp(ctx, com=None, type_inf=None):

	if com :
		commande = com.lower()
		global requete
		requete = RequeteCommande(mode = "cpp")
		try :
			requete.lancer_requete(doc_cpp, com, type_inf)
			for message in requete.message_reponses :
				await ctx.send(message)
		except ValueError :
			await help_bot(ctx,"cpp")
	else :
		await help_bot(ctx,"cpp")

#--------------------------
@bot.event

async def on_message(message):

	if message.author.bot:
		return

	for game in list_games :
		if game.on :
			if game.answer in message.content.lower() :
				game.on = False
				game.scores[message.author.name] += 1
				await message.channel.send(f"Bravo {message.author.name} ! :partying_face:  Score : {game.scores[message.author.name]}")
				gif = await search_gifs("bravo")
				await message.channel.send(gif)

	if requete.choix_on :
		if message.content.rstrip().isdigit():
			try :
				if requete.mode == "cpp" :
					commande = requete.choix[int(message.content)-1]
					await get_cpp(message.channel, commande, requete.memoire_requete)
			except IndexError :
				await message.channel.send("Ce chiffre ne fait pas partie de la liste des commandes proposées.")
		if "next" in message.content :
			requete.display_start = requete.display_start+20
			liste_numerotee = '\n'.join([str(requete.choix.index(resultat)+1)+' - '+resultat for resultat in requete.choix[requete.display_start:requete.display_start+20]])
			await message.channel.send(f"suite commandes :  \n{liste_numerotee}")
			if requete.nb_choix > requete.display_start+20 :
				await message.channel.send("(répondez \"next\" pour voir les autres résultats)")


	await bot.process_commands(message)

bot.run(discord_token)
