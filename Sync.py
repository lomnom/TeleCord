from yaml import safe_load as yamlload
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from telegram import Bot
from TermManip import *

forwarded=0
prefs=yamlload(open("Prefs.yaml",'r').read())

teleMsgStack=[]
def gotTeleMessage(update: Update, context: CallbackContext) -> None:
	global teleMsgStack
	user=f"{update.effective_user.first_name} {update.effective_user.last_name}" if\
		   update.effective_user.last_name else update.effective_user.first_name
	log(f"Got a message from {user} on Telegram!")
	teleMsg=(
		update.message.text if update.message.text else 'Blank',user,
		bool(update.message.effective_attachment)
	)
	teleMsgStack+=[teleMsg]

updater = Updater(prefs["Telegram"])

updater.dispatcher.add_handler(
	MessageHandler((Filters.chat(prefs['TelegramChannel']) & ~(Filters.command)),gotTeleMessage)
)

teleBot=Bot(prefs['Telegram'])

from threading import Thread
updater.start_polling()

log("Logged onto telegram!",type="success")

import discord
from discord.ext import commands,tasks
from discord.ext.commands import Bot

bot=commands.Bot(command_prefix="-")

def start(str,startCh):
	return startCh+('\n'+startCh).join(str.split("\n"))

from asyncio import sleep
@bot.event
async def on_ready(): #initialize
	global teleMsgStack,discordMsgStack
	log("Logged into discord as '{0.user}'!".format(bot),type='success')
	channel=bot.get_channel(prefs["DiscordChannel"])
	while True:
		await sleep(0.05)
		if teleMsgStack:
			teleMsg=teleMsgStack.pop(0)
			await channel.send(
				f"__**{teleMsg[1]}**__:\n"+
				start(
					teleMsg[0].rstrip("\n")+(
						("\n**__1 Attachment__**") if teleMsg[2] else ""
					)
				,'> ')
			)
			log("Forwarded telegram message!",type="success")
			teleMsg=""
		if discordMsgStack:
			discordMsg=discordMsgStack.pop(0)
			teleBot.send_message(
				prefs["TelegramChannel"],
				f"{discordMsg[1]}:\n"+
				start(
					discordMsg[0].rstrip("\n")+(
						(
							"\nAttachments:\n"+
							start(
								"\n".join(discordMsg[2]),
								" |   "
							)
						) if discordMsg[2] else ""
					)
				,' |   ')
			)
			log("Forwarded discord message!",type="success")
			discordMsg=""


discordMsgStack=[]
@bot.event
async def on_message(message):
	global discordMsgStack
	if message.channel.id!=prefs['DiscordChannel'] or message.author==bot.user:
		return
	log(f"Got message from {str(message.author)} on discord!")
	discordMsg=(message.content,str(message.author),list(map(lambda x:x.url,message.attachments)))
	discordMsgStack+=[discordMsg]

bot.run(prefs["Discord"])