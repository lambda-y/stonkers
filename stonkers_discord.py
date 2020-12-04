# discord stonk bot
#import os
import discord
import yfinance as yf
import colorsys
#from '/privateTOKEN' import *


#from dotenv import load_dotenv

#load_dotenv()
#TODO
#   Currently this is setup to run locally
#   If I can get this to run on firebase that'd be awesome

f = open("privateTOKEN")

TOKEN = f.readline()
#print(TOKEN)
client = discord.Client()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('$$'):
        message.content = message.content[2::]
        if message.content.startswith('add'):
            #TODO add symbols to table to watch
            #Also need to check user's that are listed 
            print("ADD")
        elif message.content.startswith('list'):
            #TODO list stonk symbols
            #EX:    TSLA $450 +13% today
            print("LIST")
        elif message.content.startswith('graph'):
            #TODO grab stonk graph of the day
            #EX: grab trendline of TSLA of the day
            print("GRAPH")
        elif message.content.startswith('grab'):
            #TODO grab more information about a stonk
            content = message.content.split(" ")
            if(len(content) < 2):
                await message.channel.send("Please input a stock to grab :)")
                return
            else:
                stonk = yf.Ticker(content[1])
                data = stonk.info

                print(data['shortName'])


                payload = "```\n"
                payload += data['shortName'] + " \n"
                payload += "OpenPrice: " + str(data['open']) + "\tCurrentPrice: " + str(data['previousClose']) + "\n"
                changeInPercent = (data['previousClose'] / data['open'])-1
                payload += "```"
                if(changeInPercent > 0):
                    payload += "```diff\n+Overall Percent Change: " + str(changeInPercent) + "```"
                else:
                    payload += "```diff\n-Overall Percent Change: " + str(changeInPercent) + "```"

                await message.channel.send(payload)

                #print(stonk.recommendations)

        elif message.content.startswith('help'):
            payload = "```\t\tWelcome to stonkers!\n\nCommands\n"
            payload+= "add: \t  Adds new stock symbols EX: <add TSLA>*\n"
            payload+= "list: \t Lists the stock symbols that were added EX: <list>\n"
            payload+= "grab: \t Grabs information about the stock symbols EX: <grab TSLA>\n"
            payload+= "graph: \tGraphs the stock symbol:  <graph MSFT>\n"
            payload+= "```"

            await message.channel.send(payload)
            print("Help sent")
            

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('-----------')

client.run(TOKEN)

