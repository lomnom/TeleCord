from yaml import safe_load as yamlload
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from telegram import Bot
from TermManip import *

forwarded=0
prefs=yamlload(open("Prefs.yaml",'r').read())

def stats(update: Update, context: CallbackContext) -> None:
	update.message.reply_text(f"I have forwarded {forwarded} messages")

teleMsg=None
def gotTeleMessage(update: Update, context: CallbackContext) -> None:
	global teleMsg
	user=f"{update.effective_user.first_name} {update.effective_user.last_name}" if\
		   update.effective_user.last_name else update.effective_user.first_name
	log(f"Got a message from {user} on Telegram!")
	teleMsg=(update.message.text,user)

updater = Updater(prefs["Telegram"])

updater.dispatcher.add_handler(
	MessageHandler((Filters.text & Filters.chat(prefs['TelegramChannel']) & ~(Filters.command))
		,gotTeleMessage)
)
updater.dispatcher.add_handler(CommandHandler('stats', stats))

teleBot=Bot(prefs['Telegram'])

from threading import Thread
updater.start_polling()

log("Logged onto telegram!",type="success")

import discord
from discord.ext import commands,tasks
from discord.ext.commands import Bot

bot=commands.Bot(command_prefix="-")

def indent(str):
	return "    "+"\n    ".join(str.split("\n"))

from asyncio import sleep
@bot.event
async def on_ready(): #initialize
	global teleMsg,discordMsg
	log("Logged into discord as '{0.user}'!".format(bot),type='success')
	channel=bot.get_channel(prefs["DiscordChannel"])
	while True:
		await sleep(0.05)
		if teleMsg:
			await channel.send(f"```yaml\n{teleMsg[1]}:\n{indent(teleMsg[0])}\n```")
			log("Forwarded telegram message!",type="success")
			teleMsg=""
		if discordMsg:
			teleBot.send_message(prefs["TelegramChannel"],f"{discordMsg[1]}:\n{indent(discordMsg[0])}")
			log("Forwarded discord message!",type="success")
			discordMsg=""

discordMsg=None
@bot.event
async def on_message(message):
	global discordMsg
	if message.channel.id!=prefs['DiscordChannel'] or message.author==bot.user:
		return
	log(f"Got message from {str(message.author)} on discord!")
	discordMsg=(message.content,str(message.author))

bot.run(prefs["Discord"])