import os
import random
import discord
import datetime
import time
import threading

from discord.ext import commands
from replit import db



claimed = {}
"""
data format is 
[
cash,
daily cooldown,
gems,
level,
{item: value, ..}
[machine id, level, status, item, amount, rate]
"""



#check timer
def checkTimer(currTime, resetTime):
    if currTime > resetTime:
        return True
    else:
        return False

def datify(iso):
    return datetime.datetime.fromisoformat(iso)
def isofy(date):
    return date.isoformat()


def cash(num):
  return (round(float(num), 2))


def display_cash(num):
  return "$" + str(num)


bot = commands.Bot(command_prefix="~", intents=discord.Intents.all())

embedTitle = "" #link text
embedUrl = "" # link url
embedDscr = "" #description text
embedThumbnail = "" #thumbnail url

def gen(username):
  while db[username][5][2] == True:
    time.sleep(db[username][5][5]*(db[username][5][1]*1.2))
    print("cash out")
    db[username][0] += db[username][4][db[username][5][3]]*db[username][5][4]
      
@bot.command()
async def startTycoon(ctx):
  itime = isofy(datetime.datetime.utcnow())
  try:
    username = ctx.message.author.mention
    if not str(username) in db:
      db[(username)] = [0, itime, 0, 1, {"copper": 1, "iron": 4}, ["basic machine", 1, False, "copper", 1, 1, 0]]
      await ctx.send("tycoon started! Access bank with cmd \"~bal\"")
    else:
      await ctx.send("already registered bozo")
  except Exception as e:
    print(e)


@bot.command()
async def bal(ctx):
  try:
    username = str(ctx.message.author.mention)
    bal = cash(db[str(username)][0])
    await ctx.send("Current Bal: " + display_cash(bal))
  except Exception as e:
    print(e)

@bot.command()
async def daily(ctx):
  try:
    
    username = str(ctx.message.author.mention)
    
    claim = cash((random.random() * 100 + 100)*(1+.33*db[(username)][3]))
    cdReset = checkTimer(datetime.datetime.utcnow(), datify(db[(username)][1]))
    if cdReset:
      db[(username)][1] = isofy(datetime.datetime.utcnow() + datetime.timedelta(hours=20))
      db[(username)][0] = claim + db[(username)][0]
      await ctx.send(display_cash(claim) + " added to player's balance!")
    else:
      diff=datify(db[(username)][1])-datetime.datetime.utcnow()
      hrs = round(diff.total_seconds()/3600, 2)
      await ctx.send("on cooldown... "+"["+str(hrs)+" hours remaining]")
  except Exception as e:
    print(e)
    await ctx.send("Uh oh: failed to claim daily...\nDebugging...")
    if username not in db:
      await ctx.send("Make a tycoon fucking ugly ass dumbass monkey")
      return
    await ctx.send(e)

@bot.command()
async def lb(ctx):
  try:
    keys = db.keys()
    if not keys:
      await ctx.send("Nobody is in the LeaderBoard!")
      
    sortedDictionary = sorted(db, key=db.get, reverse=True)
    for i, v in enumerate(sortedDictionary):
      await ctx.send(str(i+1)+ ". "+ display_cash(db[v][0])+" ("+v+")")
  except Exception as e:
    print(e)

@bot.command()
async def utc(ctx):
  utc_time = datetime.datetime.utcnow()
  await ctx.send(utc_time)


@bot.command()
async def clear(ctx):
  try:
    db.clear()
    await ctx.send("Cleared sucessfuly by: " + ctx.message.author.mention) 
  except Exception as e:
    print(e)
    await ctx.send("Uh oh: failed to clear")

@bot.command()
async def machines(ctx):
  username = ctx.message.author.mention
  data = db[(username)]
  for i, v in enumerate(data):
    if i > 4:
      id = v[0]
      lvl = v[1]
      operation = "active" if v[2] else "inactive"
      item = v[3]
      amount = str(v[4])
      rate = str(v[5])
      await ctx.send("("+str(i-4)+") "+id+" [Lv. "+str(lvl)+"] | generates "+amount+" "+ item +" every "+ rate +" seconds. (currently "+operation+")")
      time.sleep(0.75)

@bot.command()
async def toggle(ctx, arg):
  user = ctx.message.author.mention
  machineNum = int(arg)+4
  db[(user)][machineNum][2] = not db[(user)][machineNum][2]
  await ctx.send(db[(user)][machineNum][0]+" is now "+ ("on" if db[(user)][machineNum][2] else "off"))
  thread = threading.Thread(target=gen, args=(user,))
  thread.start()
  
@bot.command()
async def delete(ctx, args):
  try:
    del db[args]
    await ctx.send("Sucessfuly deleted " + args + " off Database: command done by " + ctx.message.author.mention)
  except Exception as e:
    print(e)
    await ctx.send("Uh oh: failed to delete")

@bot.command()
async def upgrade(ctx, arg):
  user = ctx.message.author.mention
  if (arg).lower() == "ore":
    if db[(user)][0] > db[user][4][db[user][5][3]]*200:
      index = list(db[user][4]).index(db[user][5][3]) + 1
      db[user][5][3] = list(db[user][4])[index]
      await ctx.send("successfully upgraded!")
    else:
      await ctx.send("not enough cash...")
      



token = os.environ['TOKEN']
bot.run(token)