# Bot Discord

# -*- coding: utf-8 -*-

from discord.ext.commands import Bot
import giphy_client
import re
import json
import os
from games import *

discord_token = os.getenv('DISCORD_TOKEN')
giphy_token = os.getenv('GIPHY_TOKEN')

bot = Bot(command_prefix = '!')

#utilisation de l'API Giphy pour pouvoir générer des gifs
api = giphy_client.DefaultApi()

help_devoirs = "Utilisation du bot : \n- Pour des informations sur les matières/devoirs : !devoirs <niveau> <matiere>"
help_cpp = "Utilisation du bot : \n- Pour chercher une commande cpp : !cpp <nom_commande> opt( 'parametres' | 'exemple' )"

with open("files/devoirs.yaml", 'r', encoding="utf-8") as stream:
	devoirs = yaml.safe_load(stream)

corres_mat = {r"python\b|(langages? de )?scripts?\b" : "langages de script", r"fouilles?( de textes?)?\b" : "fouille de texte", "lexico" : "lexicologie", r"mod(é|e)l(isation)?s?\b" : "modelisation"}
corres_niv = {r"m(aster)?\s?1" : "m1", r"m(aster)?\s?2" : "m2"}

async def search_gifs(keyword):

	#on recherche les gifs les + pertinents dans la base Giphy en fonction du mot-clé
	result = api.gifs_search_get(giphy_token, keyword, limit=5, rating='g')
	result_list = list(result.data)

	#un gif sera sélectionné au hasard parmi les plus pertinents
	gif = random.choices(result_list)
	return gif[0].url

@bot.command(name = 'devoirs')
async def infos_cours(ctx, niv=None, mat=None):

	if not niv and not mat :
		await ctx.send(help_devoirs)

	elif niv :
		niv = niv.lower()
		for exp in corres_niv :
			if re.search(exp,niv) :
				niv = corres_niv[exp]
		if niv in devoirs :
			if devoirs[niv] == None :
				await ctx.send(f"Aucune matière enregistrée pour le niveau {niv} (pour le moment !)\n\n{help_devoirs}")

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
			await ctx.send(f"Les niveaux disponibles sont : {' :star: '.join([niv for niv in devoirs])}\n\n{help_devoirs}")


#------------------------------

list_games = []

quiz = Quiz()
quiz.add_questions("files/quiz")
list_games.append(quiz)

anagram = Anagram()
anagram.add_voc_anag("files/mots.txt")
list_games.append(anagram)

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

with open("files/docs/cpp.json", 'r', encoding="utf-8") as fic_in:
	doc_cpp = json.load(fic_in)

def get_matching_list(commande, liste_commande):
	liste = []
	return liste

def display_code(code, langage):
	return f"```{langage} \n{code}\n```"

@bot.command(name = 'cpp')
async def get_cpp(ctx, com=None, type_inf=None):

	if com :
		commande = com.lower()
		if commande in doc_cpp:
			await ctx.send("niveau 1 OK")

			if not type_inf:
				await ctx.send(f"{commande} : {doc_cpp[commande]['description']['texte']}")
			else :
				type_info = type_inf.lower()
				if type_info == "exemple" :
					input = doc_cpp[commande]['exemple']['input']
					output = doc_cpp[commande]['exemple']['output']
					await ctx.send(f"input :")
					await ctx.send(display_code(input, "cpp"))
					try :
						output = doc_cpp[commande]['exemple']['output']
						await ctx.send(f"output :")
						await ctx.send(display_code(output, "cpp"))
					except (KeyError):
						await ctx.send(f"Pas d'output précisé.")

				if type_info == "parametres" :
					await ctx.send(f"{doc_cpp[commande]['parametres']}")

		else :
			resultats = get_matching_list(commande, doc_cpp.keys())
			if len(resultats) != 0 :
				await ctx.send(f"Aucun match, vouliez-vous dire : ")
			else :
				await ctx.send(f"Commande complètement inconnue ! On a tous nos failles...")
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

	await bot.process_commands(message)

bot.run(discord_token)
