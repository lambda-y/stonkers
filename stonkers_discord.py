# discord stonk bot
#import os
import discord
import yfinance as yf
import colorsys
import pandas as pd
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from pymongo import MongoClient



#from dotenv import load_dotenv

load_dotenv("config.env")

#Run MongoDB and be able to grab list of stonks to watch
mongoCL = MongoClient(os.getenv("MONGODB_ADDRESS"), int(os.getenv("MONGODB_PORT")))
db = mongoCL["stonkers"]
guilds = db["guilds"]
#accounts.load()

f = open("privateTOKEN")    #PrivateFile in the same directory

TOKEN = f.readline()
client = discord.Client()

@client.event
async def on_message(message):

    if message.content.startswith('$$'):

        if message.author == client.user:
            return


        message.content = message.content[2::]
        if message.content.startswith('add'):
            #TODO add symbols to table to watch
            #Also need to check user's that are listed 

            

            content = message.content.split(" ")
            try:
                stonk = yf.Ticker(content[1])
                stonk.info
            except Exception:
                await message.channel.send("That symbol is unrecognized or invalid, Please Try again :)")
                return

            serverID = message.guild.id
            guild = guilds.find_one({},{ "id": serverID, "stocks": [] })

            for x in guilds.find():
                print(x)

            stockList = guild["stocks"]
            if(content[1] not in stockList):
                stockList.append(content[1])
                guilds.update({"id" : serverID}, { "$set": {"stocks": stockList }})
            print(stockList)

            await message.channel.send("Stock added :)")
            
        elif message.content.startswith('list'):
            #TODO list stonk symbols
            #EX:    TSLA $450 +13% today
            serverID = message.guild.id
            guild = guilds.find_one({},{ "id": serverID, "stocks": [] })
            stockList = guild["stocks"]

            for x in stockList:
                await message.channel.send(grabStock(x))
            #print("LIST")

        elif message.content.startswith('del'):
            #TODO remove item from list
            content = message.content.split(" ")

            try:
                stonk = yf.Ticker(content[1])
                stonk.info
            except Exception:
                await message.channel.send("That symbol is unrecognized or invalid, Please Try again :)")
                return

            serverID = message.guild.id
            guild = guilds.find_one({},{ "id": serverID, "stocks": [] })

            for x in guilds.find():
                print(x)

            stockList = guild["stocks"]
            if(content[1] not in stockList):
                await message.channel.send("That stock wasn't there to begin with! :)")
                return

            stockList.remove(content[1])
            guilds.update({"id" : serverID}, { "$set": {"stocks": stockList }})
            print(stockList)

            await message.channel.send("Stock removed :)")

        elif message.content.startswith('graph'):
            content = message.content.split(" ")    #Segments data members

            if(len(content) < 2):
                await message.channel.send("Please input a stock to grab :)") 
                return

            else:

                f = plt.figure()    #Creates a new MathPlot figure
                try:
                    stonk = yf.Ticker(content[1])   #Tests to make sure that the stock is a valid symbol
                    stonk.info
                    data = stonk.history(period="1wk")
                except Exception:
                    await message.channel.send("That symbol is unrecognized or invalid, Please Try again :)")
                    return
                
                dates = []
                closingNumbers = []

                for i in range(len(data.index.values)):
                    closingNumbers.append("%.2f" % data.iloc[i][2])
                    ts = pd.to_datetime(str(data.index.values[i]))
                    dates.append(ts.strftime('%m-%d'))

                plt.plot(dates, closingNumbers, color="blue", marker='.')
                plt.xlabel("Time (1 week(s))")
                plt.ylabel("Closing Stock price (USD)")
                plt.title("Graph of " + content[1] + " over 1 week(s)")
                plt.grid(True)

                while(os.path.exists('foo.jpg')):
                    print("waiting")
                plt.savefig('foo.jpg')
                await message.channel.send(file=discord.File('foo.jpg'))
                os.remove('foo.jpg')
                f.clear()
                plt.close(f)

            print("GRAPH")
        elif message.content.startswith('grab'):
            #DONE grab more information about a stonk
            #TODO Be able to request stocks by name & symbol (Tesla & TSLA)
            
            content = message.content.split(" ")
            if(len(content) < 2):
                return("Please input a stock to grab :)")
        
            await message.channel.send(grabStock(content[1]))
            #print(stonk.recommendations)

        elif message.content.startswith('help'):
            await message.channel.send(helpFunction())
            print(message.guild.id)
            
def helpFunction():
    payload = "```\t\tWelcome to stonkers!\n\nCommands\n"
    payload+= "add: \t  Adds new stock symbols EX: <$$add TSLA>*\n"
    payload+= "del: \t  Deletes stocks from the server list EX: <$$del SBUX> \n"
    payload+= "list: \t Lists the stock symbols that were added EX: <$$list>\n"
    payload+= "grab: \t Grabs information about the stock symbols EX: <$$grab TSLA>\n"
    payload+= "graph: \tGraphs the stock symbol:  <$$graph MSFT>\n"
    payload+= "```"
    return(payload)

def grabStock(stock):
    
    try:
        stonk = yf.Ticker(stock)
        data = stonk.info
    except Exception:
        return("That symbol is unrecognized or invalid, Please Try again :)")
        
    payload = "```diff\n"
    payload += data['shortName'] + " \n"
    payload += "OpenPrice: " + str(data['open']) + "\tClosePrice: " + str(data['previousClose']) + "\n"
    changeInPercent = (data['previousClose'] / data['open'])-1
    changeInPercent *= 100
    changeInPercent = "%.2f" % changeInPercent

    if(float(changeInPercent) > 0):
        payload += "+Overall Percent Change: " + (changeInPercent)
    else:
        payload += "-Overall Percent Change: " + (changeInPercent)

    payload += "```"
    return(payload)


    

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('-----------')

client.run(TOKEN)

