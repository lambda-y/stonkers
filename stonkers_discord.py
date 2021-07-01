# discord stonk bot
#import os
import discord
import yfinance as yf
import colorsys
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import drange
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from pymongo import MongoClient
import pymongo



#from dotenv import load_dotenv

load_dotenv("config.env")

#Run MongoDB and be able to grab list of stonks to watch
mongoCL = pymongo.MongoClient(os.getenv("MONGODB_ADDRESS"), int(os.getenv("MONGODB_PORT")))
db = mongoCL["stonkers"]
guilds = db["guilds"]
#accounts.load()

f = open("privateTOKEN")    #PrivateFile in the same directory




""" guilds: [
    discord1: {
        stockList
    },
    discord2: {

    }
}





 """






TOKEN = f.readline()
f.close()
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

            content = message.content.split(" ")
            try:
                stonk = yf.Ticker(content[1])
                data = stonk.info
                content[1] = content[1].upper()
                adding = [content[1], data['previousClose']]
            except Exception:
                await message.channel.send("That symbol is unrecognized or invalid, Please Try again :)")
                return

            serverID = message.guild.id
            #print(guilds.find_one())
            guild = guilds.find_one({"id": serverID})
            
            stockList = []
            try:
                stockList = guild['stocks']

                for i in stockList:
                    if(i[0] == content[1].upper()):
                        return

                stockList.append(adding)
                guilds.update_one({"id" : serverID}, { "$set": {"stocks": stockList }})
            except TypeError:
                stockList.append(adding)
                guilds.insert_one({"id" : serverID, "stocks" : stockList})

                print("Type Error in adding")
                pass
            except KeyError:
                stockList.append(adding)
                guilds.update_one({"id" : serverID}, { "$set": {"stocks": stockList }})

                print("Key Error in adding")
                pass
            
            #print(stockList)
            
            await message.channel.send("Stock added :)")
        
        elif message.content.startswith('watchlist'):
            serverID = message.guild.id
            
            guild = guilds.find_one({ "id": serverID })
            print(guild)
            print(serverID)
            stockList = guild["stocks"]
            #print(stockList)

            watchlist = []
            for x in stockList:
                watchlist.append(x[0])

            await message.channel.send("This group is currently watching: " + ", ".join(watchlist))

        elif message.content.startswith('list'):
            #TODO list stonk symbols
            #EX:    TSLA $450 +13% today
            serverID = message.guild.id
            guild = guilds.find_one({ "id": serverID })
            stockList = guild["stocks"]

            print(stockList)
            if(len(stockList) == 0):
                await message.channel.send("Looks like there was nothing to grab")
            else:
                await message.channel.send("Grabbing your list, wait a second :)")
                await message.channel.send(grabStocks(stockList))
            #print("LIST")

        elif message.content.startswith('del'):
            #TODO remove item from list
            content = message.content.split(" ")

            serverID = message.guild.id
            guild = guilds.find_one({ "id": serverID })


            stockList = guild["stocks"]
            
            for i in stockList:
                if(i[0] == content[1].upper()):
                    stockList.remove(i)
                    guilds.update_one({"id" : serverID}, { "$set": {"stocks": stockList }})
                    await message.channel.send("Stock removed :)")
                    return

            await message.channel.send("Stock wasn't there :)")

        elif message.content.startswith('graph'):
            content = message.content.split(" ")    #Segments data members

            if(len(content) < 2):
                await message.channel.send("Please input a stock to grab :)") 
                return

            else:

                f = plt.figure()    #Creates a new MathPlot figure
                try:
                    stonk = yf.Ticker(content[1])   #Tests to make sure that the stock is a valid symbol
                    data = stonk.info
                    data["previousClose"]
                    data = stonk.history(period="1wk")
                except Exception:
                    await message.channel.send("That symbol is unrecognized or invalid, Please Try again :)")
                    return
                
                dates = []
                closingNumbers = []

                for i in range(len(data.index.values)):
                    closingNumbers.append(float("%.2f" % data.iloc[i][2]))
                    ts = pd.to_datetime(str(data.index.values[i]))
                    dates.append(ts.strftime('%m-%d'))

                

                #plt.plot(range(5), closingNumbers)
                plt.scatter(dates, closingNumbers, color="blue")
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
    payload = "```\t\tWelcome to stonkers!\n\nCommands:\n"
    payload+= "add: \t  Adds new stock symbols EX: <$$add TSLA>*\n"
    payload+= "del: \t  Deletes stocks from the server list EX: <$$del SBUX> \n"
    payload+= "watchlist: Lists the stocks that were added EX: <$$watchlist> \n"
    payload+= "list: \t Lists the stock symbols that were added along with prices EX: <$$list>\n"
    payload+= "grab: \t Grabs information about the stock symbols EX: <$$grab TSLA>\n"
    payload+= "graph: \tGraphs the stock symbol:  <$$graph MSFT>\n"
    payload+= "```"
    return(payload)

def grabStock(stock):
    
    try:
        stonk = yf.Ticker(stock)
        data = stonk.info
        data["previousClose"]
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

def grabStocks(stockList):
    
    payload = "```diff\n"
    for stonkA, stockB in stockList:
        try:
            stonk = yf.Ticker(stonkA)
            data = stonk.info
            data["previousClose"]
        except Exception:
            return("That symbol is unrecognized or invalid, Please Try again :)")
            
        
        payload += data['shortName'] + " \n"
        payload += "OpenPrice: " + str(data['open']) + "\tClosePrice: " + str(data['previousClose']) + "\n"
        changeInPercent = (data['previousClose'] / data['open'])-1
        changeInPercent *= 100
        changeInPercent = "%.2f" % changeInPercent

        if(float(changeInPercent) > 0):
            payload += "+Today's Percent Change: " + (changeInPercent) + "\n"
        else:
            payload += "-Today's Percent Change: " + (changeInPercent) + "\n"

        changeInPercent = (data['previousClose'] / stockB)-1
        changeInPercent *= 100
        changeInPercent = "%.2f" % changeInPercent

        if(float(changeInPercent) > 0):
            payload += "+Overall Percent Change since adding: " + (changeInPercent) + "\n\n"
        else:
            payload += "-Overall Percent Change since adding: " + (changeInPercent) + "\n\n"


    payload += "```"
    return(payload)
    

@client.event
async def on_ready():
    activityV = discord.Activity(type=discord.ActivityType.custom, state="Use $$help for stonking commands")
    await client.change_presence(activity=activityV)
    discord.Activity(name="test", type=5)
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('-----------')

client.run(TOKEN)

