# Bot Discord

# -*- coding: utf-8 -*-

from discord.ext.commands import Bot
import giphy_client
import re
import os
from games import *

discord_token = os.getenv('DISCORD_TOKEN')
giphy_token = os.getenv('GIPHY_TOKEN')

bot = Bot(command_prefix = '!')

#utilisation de l'API Giphy pour pouvoir générer des gifs 
api = giphy_client.DefaultApi()

help = "Utilisation du bot : \n- Pour des informations sur les matières/devoirs : !devoirs <niveau> <matiere>"

with open("files/devoirs.yaml", 'r', encoding="utf-8") as stream:
	devoirs = yaml.safe_load(stream)

corres_mat = {r"python|(langages? de )?scripts?" : "langages de script", r"fouilles?( de textes?)?" : "fouille de texte", "lexico" : "lexicologie", r"mod(é|e)l(isation)?" : "modelisation"}
corres_niv = {r"m(aster)?\s?1" : "m1", r"m(aster)?\s?2" : "m2"}

async def search_gifs(keyword):

	#on recherche les gifs les + pertinents dans la base Giphy en fonction du mot-clé
	result = api.gifs_search_get(giphy_token, keyword, limit=5, rating='g')
	result_list = list(result.data)

	#un gif sera sélectionné au hasard parmi les plus pertinents
	gif = random.choices(result_list)
	return gif[0].url

@bot.command(name = 'devoirs')
async def infos_cours(ctx, *args):
	rep_niveaux = f"Les niveaux disponibles sont : {' :star: '.join([niv for niv in devoirs])}\n\n{help}"
	if not args :
		await ctx.send(help)
	else :
		niv = args[0].lower()
		for exp in corres_niv : 
			if re.search(exp,niv) :
				niv = corres_niv[exp]
	if len(args) == 1 :
		if niv in devoirs :
			if devoirs[niv] == None :
				await ctx.send("Aucune matière enregistrée pour ce niveau (pour le moment !)\n\nHarcelez JMD pour plus d'informations.")
				gif = await search_gifs("oops")
				await ctx.send(gif)				 
			else :
				await ctx.send(f"Les matières du niveau {niv} sont :\n {' :star: '.join([dev for dev in devoirs[niv]])}\n\nPour connaître les devoirs, tapez !devoirs {niv} <matiere>")
		else : 
			await ctx.send(rep_niveaux)
	if len(args) > 1 :
		mat = args[1].lower()
		for exp in corres_mat : 
			if re.search(exp,mat) :
				mat = corres_mat[exp]
	if len(args) == 2 :
		if niv in devoirs :
			if mat in devoirs[niv] :
				if devoirs[niv][mat] == None :
					await ctx.send("Aucun devoir enregistré pour ce cours.")
					gif = await search_gifs("lucky")
					await ctx.send(gif)
				else :
					for dev in devoirs[niv][mat] :
						await ctx.send(f"Pour le {dev} : {devoirs[niv][mat][dev]}")
			else :
				await ctx.send(f"{mat} Les matières du niveau {niv} sont :\n {' :star: '.join([dev for dev in devoirs[niv]])}\n\nPour connaître les devoirs, tapez !devoirs {niv} <matiere>")
		else :
			await ctx.send(rep_niveaux)
			
	if len(args) > 2 :
		await ctx.send(f"Trop d'aguments.\n{help}")

#------------------------------

list_games = []
quiz = Quiz()
quiz.add_questions("files/questions.yaml")  
list_games.append(quiz)

anagramme = Anagramme()
anagramme.add_voc_anag("files/mots.txt")
list_games.append(anagramme)

@bot.command(name = 'anag')
async def anag_game(ctx):
	if anagramme.on == True : 
		await ctx.send(f"Déjà en cours : de quel mot >>> {anagramme.anag} <<< est-il l'anagramme ?")
	else :
		anagramme.on = True
		anagramme.answer = random.choice(anagramme.mots)
		anagramme.create_anag()
		await ctx.send(f"Anagramme :   :arrow_right:   {anagramme.anag}   :arrow_left:	 Quel est le mot original ?")

@bot.command(name='quiz')
async def quiz_game(ctx):
	if quiz.on == True : 
		await ctx.send(f"Déjà en cours ! Question : {quiz.question}")
	else :
		quiz.on = True
		quiz.question = random.choice(list(quiz.questions.keys()))
		quiz.answer = quiz.questions[quiz.question]
		await ctx.send(f"Question : {quiz.question}")

@bot.command(name = 'scores')
async def scores(ctx, game) :
	game = game.lower()
	try :
		game = eval(game)
		if game.scores == {} :
			await ctx.send(f"Aucun score enregistré pour le jeu >> {game.name} << ! Lancez-le vite : :arrow_right: {game.start} :arrow_left:")
		else :
			for pers in game.scores :
				await ctx.send(f"{pers} : {game.scores[pers]}")
	except : 
		await ctx.send("Utilisation : scores <jeu>\n---------------")
		await ctx.send(f"Jeux disponibles : :game_die: {' :game_die: '.join([game.name for game in list_games])}")
		await ctx.send(f"Lancement : :video_game: {' :video_game: '.join([game.start for game in list_games])}")

@bot.event
async def on_message(message):

	for game in list_games :
		if game.on :
			if message.content == game.answer  : 
				game.on = False
				game.scores[message.author.name] += 1
				await message.channel.send(f"Bravo {message.author.name} ! :partying_face: {game.scores[message.author.name]}")
				gif = await search_gifs("bravo")
				await message.channel.send(gif)

	await bot.process_commands(message)

bot.run(discord_token)	
