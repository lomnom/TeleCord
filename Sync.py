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
		update.message.text if update.message.text else None,user,
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
	str=str.rstrip("\n")
	return startCh+('\n'+startCh).join(str.split("\n"))

def escape(chrs,str):
	for char in chrs:
		str=str.replace(char,"\\"+char)
	return str

from asyncio import sleep
@bot.event
async def on_ready(): #initialize
	global teleMsgStack,discordMsgStack
	log("Logged into discord as '{0.user}'!".format(bot),type='success')
	channel=bot.get_channel(prefs["DiscordChannel"])
	lastTeleUser=None
	lastDiscordUser=None
	while True:
		await sleep(0.05)
		if teleMsgStack:
			teleMsg=teleMsgStack.pop(0)
			await channel.send(
				(
					f"__**{teleMsg[1]}**__:\n" 
					if teleMsg[1]!=lastTeleUser else ""
				)+
				start(
					((teleMsg[0].rstrip("\n")+"\n") if teleMsg[0]!=None else "")+(
						("**__1 Attachment (see on telegram)__**") if teleMsg[2] else ""
					)
				,'> ')
			)
			log("Forwarded telegram message!",type="success")
			lastTeleUser=teleMsg[1]
			lastDiscordUser=None
		if discordMsgStack:
			discordMsg=discordMsgStack.pop(0)
			teleBot.send_message(
				prefs["TelegramChannel"],
				(
					(
						f"*__{discordMsg[1]}__*:\n" 
						if lastDiscordUser!=discordMsg[1] else ""
					)+
					start(
						escape("#~*_^",discordMsg[0]).rstrip("\n")+
						(
							(
								"\n__*Attachments:*__\n"+
								start(
									"\n".join(discordMsg[2]),
									"*|*   "
								)
							) if discordMsg[2] else ""
						)
					,'*|*   ')
				).replace('#','\\#')
				 .replace('|','\\|'),

				parse_mode='MarkdownV2'
			)
			log("Forwarded discord message!",type="success")
			lastDiscordUser=discordMsg[1]
			lastTeleUser=None

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